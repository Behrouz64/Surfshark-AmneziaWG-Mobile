"""Surfshark AmneziaWG Mobile Scanner — High-Performance Mobile Web Server."""

from __future__ import annotations
import argparse
import base64
import json
import os
import socket
import sys
import threading
import urllib.parse
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from typing import List, Dict, Any, Optional

# Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from core.models import ServerCluster, UserCredentials, ObfuscationPreset
from core.dns_resolver import DnsResolver
from core.checker import UdpChecker
from core.config_builder import ConfigBuilder
from core.vpn_detector import VpnDetector


class ScannerState:
    """Thread-safe application state shared across HTTP requests."""

    def __init__(self, data_file: str):
        self.data_file = data_file
        self.clusters: List[ServerCluster] = []
        self.credentials: UserCredentials = UserCredentials()
        self.preset: ObfuscationPreset = ObfuscationPreset()
        self.resolver = DnsResolver()
        self.checker = UdpChecker()
        self.is_scanning = False
        self.scan_progress = {"total": 0, "completed": 0, "working": 0, "status": "Ready"}
        self._lock = threading.Lock()
        self.load_data()

    def load_data(self) -> None:
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    ui = data.get("user_interface", {})
                    self.credentials = UserCredentials(
                        private_key=ui.get("private_key", ""),
                        address=ui.get("address", "10.14.0.2/16"),
                        dns=ui.get("dns", "162.252.172.57, 149.154.159.92"),
                    )
                    self.clusters = [ServerCluster.from_dict(s) for s in data.get("servers", [])]
            except Exception as e:
                print(f"Error loading {self.data_file}: {e}")

    def save_credentials(self, privkey: str, address: str, dns: str) -> None:
        with self._lock:
            self.credentials.private_key = privkey.strip()
            self.credentials.address = address.strip() if address.strip() else "10.14.0.2/16"
            self.credentials.dns = dns.strip() if dns.strip() else "162.252.172.57, 149.154.159.92"

    def run_scan(self, continent: str = "All") -> List[ServerCluster]:
        with self._lock:
            self.is_scanning = True
            targets = [c for c in self.clusters if continent == "All" or c.continent == continent]
            self.scan_progress = {"total": len(targets), "completed": 0, "working": 0, "status": "Resolving DoH..."}

        try:
            # Step 1: Encrypted DoH Resolution
            self.resolver.resolve_batch(targets)

            # Step 2: Concurrently probe UDP latency
            with self._lock:
                self.scan_progress["status"] = "Testing UDP reachability..."

            checked = self.checker.check_batch(targets)

            with self._lock:
                working = sum(1 for c in checked if c.best_ping is not None)
                self.scan_progress = {
                    "total": len(targets),
                    "completed": len(targets),
                    "working": working,
                    "status": f"Completed ({working} working)",
                }
                # Sort: working servers first by latency ascending
                checked.sort(key=lambda c: (0 if c.best_ping is not None else 1, c.best_ping or 9999))
                self.is_scanning = False
            return checked
        except Exception as e:
            with self._lock:
                self.is_scanning = False
                self.scan_progress["status"] = f"Error: {e}"
            return targets


GLOBAL_STATE: Optional[ScannerState] = None


class MobileApiHandler(BaseHTTPRequestHandler):
    """Handles HTTP routes for mobile touch interface, REST API, subscriptions, and downloads."""

    def _send_json(self, data: Any, status: int = 200) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, content: bytes, content_type: str, filename: Optional[str] = None) -> None:
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        if filename:
            self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(content)

    def do_OPTIONS(self) -> None:
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, HEAD")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_HEAD(self) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # 1. Mobile Web UI (Single Page Application)
        if path in ("/", "/index.html"):
            index_path = os.path.join(BASE_DIR, "templates", "index.html")
            with open(index_path, "rb") as f:
                content = f.read()
            self._send_file(content, "text/html; charset=utf-8")
            return

        # 2. Static Assets (CSS, JS)
        if path.startswith("/static/"):
            rel_file = path[len("/static/"):]
            safe_file = os.path.basename(rel_file)
            fpath = os.path.join(BASE_DIR, "static", safe_file)
            if os.path.exists(fpath):
                ctype = "text/css" if safe_file.endswith(".css") else "application/javascript"
                with open(fpath, "rb") as f:
                    self._send_file(f.read(), ctype)
                return
            self.send_error(404, "File Not Found")
            return

        # 3. System & Scanner Status API
        if path == "/api/status":
            is_vpn = VpnDetector.is_vpn_active()
            clusters = GLOBAL_STATE.clusters
            data = {
                "vpn_active": is_vpn,
                "total_servers": len(clusters),
                "is_scanning": GLOBAL_STATE.is_scanning,
                "progress": GLOBAL_STATE.scan_progress,
                "credentials": {
                    "has_key": GLOBAL_STATE.credentials.is_configured,
                    "address": GLOBAL_STATE.credentials.address,
                    "dns": GLOBAL_STATE.credentials.dns,
                    "preview": f"...{GLOBAL_STATE.credentials.private_key[-8:]}" if GLOBAL_STATE.credentials.is_configured else "Not Set",
                },
            }
            self._send_json(data)
            return

        # 4. List Servers API (with optional continent filter)
        if path == "/api/servers":
            continent = query.get("continent", ["All"])[0]
            servers = [c for c in GLOBAL_STATE.clusters if continent == "All" or c.continent == continent]
            resp = []
            for s in servers:
                s_dict = s.to_dict()
                s_dict["shadowrocket_url"] = ConfigBuilder.build_shadowrocket_url(s, GLOBAL_STATE.credentials, GLOBAL_STATE.preset)
                s_dict["shadowrocket_deeplink"] = ConfigBuilder.build_shadowrocket_deeplink(s, GLOBAL_STATE.credentials, GLOBAL_STATE.preset)
                resp.append(s_dict)
            self._send_json({"servers": resp, "count": len(resp)})
            return

        # 5. Live Subscription Endpoint (/sub) for Shadowrocket / Streisand
        if path == "/sub":
            working_clusters = [c for c in GLOBAL_STATE.clusters if c.effective_ip]
            b64_sub = ConfigBuilder.generate_subscription_base64(
                working_clusters, GLOBAL_STATE.credentials, GLOBAL_STATE.preset
            )
            self._send_file(b64_sub.encode("utf-8"), "text/plain; charset=utf-8", "surfshark_subscription.txt")
            return

        # 6. Single Config Download
        if path == "/export/conf":
            hostname = query.get("hostname", [""])[0]
            cluster = next((c for c in GLOBAL_STATE.clusters if c.hostname == hostname), None)
            if cluster and cluster.effective_ip:
                conf = ConfigBuilder.build_amnezia_config(cluster, GLOBAL_STATE.credentials, GLOBAL_STATE.preset)
                fname = f"Surfshark_{cluster.country}_{cluster.city}_{cluster.effective_ip}.conf"
                self._send_file(conf.encode("utf-8"), "text/plain; charset=utf-8", fname)
                return
            self.send_error(404, "Server cluster not found or has no IP")
            return

        # 7. Batch ZIP Download
        if path == "/export/zip":
            working_clusters = [c for c in GLOBAL_STATE.clusters if c.effective_ip]
            zip_bytes = ConfigBuilder.generate_batch_zip_bytes(
                working_clusters, GLOBAL_STATE.credentials, GLOBAL_STATE.preset
            )
            self._send_file(zip_bytes, "application/zip", "Surfshark_AmneziaWG_Mobile_Configs.zip")
            return

        # 8. QR Code Image Endpoint
        if path == "/api/qr":
            text = query.get("text", [""])[0]
            if text:
                data_url = ConfigBuilder.generate_qr_code_data_url(text)
                if data_url.startswith("data:image/png;base64,"):
                    raw_png = base64.b64decode(data_url.split(",")[1])
                    self._send_file(raw_png, "image/png")
                    return
            self.send_error(400, "Invalid text or QR generator unavailable")
            return

        self.send_error(404, "Endpoint Not Found")

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # 1. Trigger Network Scan
        if path == "/api/scan":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length) if content_length > 0 else b"{}"
            try:
                params = json.loads(body.decode("utf-8")) if body else {}
            except Exception:
                params = {}

            continent = params.get("continent", "All")

            # Run scan in thread or synchronously
            def _scan_worker():
                GLOBAL_STATE.run_scan(continent)

            thread = threading.Thread(target=_scan_worker, daemon=True)
            thread.start()

            self._send_json({"message": f"Scan started for continent '{continent}'", "status": "started"})
            return

        # 2. Update Credentials API
        if path == "/api/settings":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            try:
                params = json.loads(body.decode("utf-8"))
                privkey = params.get("private_key", "")
                address = params.get("address", "10.14.0.2/16")
                dns = params.get("dns", "162.252.172.57, 149.154.159.92")
                GLOBAL_STATE.save_credentials(privkey, address, dns)
                self._send_json({"message": "Credentials updated successfully", "has_key": GLOBAL_STATE.credentials.is_configured})
            except Exception as e:
                self._send_json({"error": str(e)}, status=400)
            return

        self.send_error(404, "Endpoint Not Found")


def get_local_ip() -> str:
    """Detect LAN IPv4 address to show clickable link for phones on Wi-Fi."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def main():
    parser = argparse.ArgumentParser(description="Surfshark AmneziaWG Mobile Scanner Server")
    parser.add_argument("--host", default="0.0.0.0", help="Binding interface (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8080, help="Port to listen on (default: 8080)")
    parser.add_argument("--data", default=os.path.join(BASE_DIR, "data", "surfshark_servers.json"), help="Path to servers JSON")
    args = parser.parse_args()

    global GLOBAL_STATE
    GLOBAL_STATE = ScannerState(args.data)

    local_ip = get_local_ip()
    port = args.port

    print("=" * 68)
    print("  🦈 Surfshark AmneziaWG Scanner — Mobile Edition 📱")
    print("=" * 68)
    print(f"  • Mobile Web App URL:  http://{local_ip}:{port}")
    print(f"  • Local Desktop URL:   http://localhost:{port}")
    print(f"  • Live Subscription:   http://{local_ip}:{port}/sub")
    print("")
    print("  👉 Connect your iPhone or Android to the same Wi-Fi, then open:")
    print(f"     http://{local_ip}:{port}")
    print("  1-Tap to import any server into Shadowrocket or AmneziaVPN!")
    print("=" * 68)

    server = ThreadingHTTPServer((args.host, port), MobileApiHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        server.shutdown()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Surfshark AmneziaWG Scanner — Mobile & Terminal CLI Tool (for Termux, VPS, and macOS/Linux)."""

from __future__ import annotations
import argparse
import json
import os
import sys
from typing import List, Optional

# Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from core.models import ServerCluster, UserCredentials, ObfuscationPreset
from core.dns_resolver import DnsResolver
from core.checker import UdpChecker
from core.config_builder import ConfigBuilder
from core.vpn_detector import VpnDetector


def load_catalog(data_path: str) -> tuple[List[ServerCluster], UserCredentials]:
    if not os.path.exists(data_path):
        print(f"Error: Server data file not found at {data_path}")
        sys.exit(1)

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    ui = data.get("user_interface", {})
    creds = UserCredentials(
        private_key=ui.get("private_key", ""),
        address=ui.get("address", "10.14.0.2/16"),
        dns=ui.get("dns", "162.252.172.57, 149.154.159.92"),
    )
    servers = [ServerCluster.from_dict(s) for s in data.get("servers", [])]
    return servers, creds


def run_cli():
    parser = argparse.ArgumentParser(
        description="🦈 Surfshark AmneziaWG Mobile & CLI Scanner (Compatible with Android Termux & VPS)"
    )
    parser.add_argument(
        "--data",
        default=os.path.join(BASE_DIR, "data", "surfshark_servers.json"),
        help="Path to servers JSON data",
    )
    parser.add_argument(
        "--continent",
        default="All",
        choices=["All", "Europe", "North America", "Asia Pacific", "Middle East", "South America", "Africa"],
        help="Filter servers by continent (default: All)",
    )
    parser.add_argument(
        "--privkey",
        default="",
        help="Client WireGuard private key (overrides saved config)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=30,
        help="Concurrency worker threads for UDP probing (default: 30)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=2.5,
        help="Probe timeout in seconds (default: 2.5)",
    )
    parser.add_argument(
        "--export-zip",
        metavar="PATH",
        help="Export all working configurations as a ZIP archive",
    )
    parser.add_argument(
        "--export-dir",
        metavar="DIR",
        help="Export individual .conf files into the specified directory",
    )
    parser.add_argument(
        "--sub",
        action="store_true",
        help="Print Base64 subscription string directly to stdout",
    )
    parser.add_argument(
        "--qr",
        metavar="HOSTNAME",
        help="Print ASCII terminal QR code for a specific server hostname",
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Launch the mobile touch web server",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port for the web server (default: 8080)",
    )

    args = parser.parse_args()

    # Serve mode
    if args.serve:
        import server
        sys.argv = [sys.argv[0], "--port", str(args.port), "--data", args.data]
        server.main()
        return

    servers, credentials = load_catalog(args.data)
    if args.privkey.strip():
        credentials.private_key = args.privkey.strip()

    preset = ObfuscationPreset()

    # Filter
    if args.continent != "All":
        servers = [s for s in servers if s.continent == args.continent]

    print("=" * 64)
    print("  🦈 Surfshark AmneziaWG Scanner — CLI & Mobile Engine")
    print("=" * 64)

    # Detect active VPN
    if VpnDetector.is_vpn_active():
        print("  ⚠️  WARNING: Active VPN interface detected (utun/tun).")
        print("     Disable VPN for true censorship bypass probing.\n")

    print(f"  • Target Continent: {args.continent}")
    print(f"  • Candidate Servers: {len(servers)}")
    print(f"  • Obfuscation: Jc={preset.jc}, Jmin={preset.jmin}, Jmax={preset.jmax}")
    print(f"  • Client Private Key: {'Configured ✅' if credentials.is_configured else 'Not Set (Placeholder)'}")
    print("-" * 64)

    # Step 1: Encrypted DoH Resolution
    print("[1/2] Resolving endpoints using Encrypted DNS-over-HTTPS (DoH)...")
    resolver = DnsResolver()
    resolver.resolve_batch(servers)

    # Step 2: UDP Handshake Probing
    print(f"[2/2] Concurrently testing UDP reachability with {args.workers} workers...")
    checker = UdpChecker(timeout=args.timeout, max_workers=args.workers)
    checked = checker.check_batch(servers)

    working = [s for s in checked if s.best_ping is not None]
    working.sort(key=lambda s: s.best_ping or 9999)

    print("\n" + "=" * 64)
    print(f"  SCAN COMPLETE: {len(working)} / {len(checked)} servers online & reachable")
    print("=" * 64)

    # Print top 15 results
    print(f"{'#':<3} {'FLAG':<4} {'COUNTRY / CITY':<26} {'IP:PORT':<21} {'LATENCY':<8}")
    print("-" * 64)
    for idx, s in enumerate(working[:20], 1):
        loc = f"{s.country} - {s.city}"[:25]
        endpoint = f"{s.effective_ip}:{s.port}"
        ping_str = f"{round(s.best_ping)} ms"
        print(f"{idx:<3} {s.flag:<4} {loc:<26} {endpoint:<21} {ping_str:<8}")

    if len(working) > 20:
        print(f"... and {len(working) - 20} more reachable servers.")

    # ASCII QR Code if requested
    if args.qr:
        target_s = next((s for s in working if args.qr.lower() in s.hostname.lower()), None)
        if not target_s and working:
            target_s = working[0]

        if target_s:
            sr_url = ConfigBuilder.build_shadowrocket_url(target_s, credentials, preset)
            print("\n" + "=" * 64)
            print(f"  QR CODE for {target_s.country} - {target_s.city} ({target_s.effective_ip})")
            print("=" * 64)
            try:
                import qrcode
                qr = qrcode.QRCode(border=1)
                qr.add_data(sr_url)
                qr.print_ascii(invert=True)
            except Exception as e:
                print(f"Could not render ASCII QR code: {e}")
            print(f"Shadowrocket URL:\n{sr_url}\n")

    # Subscription Output
    if args.sub:
        b64_sub = ConfigBuilder.generate_subscription_base64(working, credentials, preset)
        print("\n" + "=" * 64)
        print("  SHADOWROCKET / STREISAND SUBSCRIPTION PAYLOAD (Base64)")
        print("=" * 64)
        print(b64_sub)

    # Export ZIP
    if args.export_zip:
        zip_bytes = ConfigBuilder.generate_batch_zip_bytes(working, credentials, preset)
        out_path = os.path.abspath(args.export_zip)
        with open(out_path, "wb") as f:
            f.write(zip_bytes)
        print(f"\n✅ Exported {len(working)} configs to ZIP archive: {out_path}")

    # Export Directory
    if args.export_dir:
        out_dir = os.path.abspath(args.export_dir)
        os.makedirs(out_dir, exist_ok=True)
        count = 0
        for s in working:
            conf_str = ConfigBuilder.build_amnezia_config(s, credentials, preset)
            fname = f"Surfshark_{s.country}_{s.city}_{s.effective_ip}.conf"
            with open(os.path.join(out_dir, fname), "w", encoding="utf-8") as f:
                f.write(conf_str)
            count += 1
        print(f"\n✅ Exported {count} .conf files to directory: {out_dir}")


if __name__ == "__main__":
    run_cli()

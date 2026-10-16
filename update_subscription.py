"""Script to resolve all Surfshark subdomains via DoH and generate sub.txt and sub_base64.txt."""

from __future__ import annotations
import base64
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "surfshark_servers.json")

with open(DATA_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

servers = data["servers"]
ui = data.get("user_interface", {})
client_privkey = ui.get("private_key", "eIAi8RMy6+QScRWERt/+jEedxdqro4FFJO9A8L3ptGU=")
client_ip = ui.get("address", "10.14.0.2/16").split("/")[0].strip()
dns_servers = ui.get("dns", "162.252.172.57, 149.154.159.92").strip()

obfs_dict = {
    "s1": "0",
    "h2": "2",
    "jmax": "1000",
    "s2": "0",
    "h3": "3",
    "jc": "4",
    "jmin": "50",
    "h1": "1",
    "h4": "4",
}
obfs_param = urllib.parse.quote(json.dumps(obfs_dict, separators=(",", ":")))


def get_flag(code: str) -> str:
    if not code or len(code) != 2:
        return "🌐"
    try:
        return "".join(chr(127397 + ord(c.upper())) for c in code)
    except Exception:
        return "🌐"


def resolve_hostname(hostname: str) -> list[str]:
    # 1. Try Cloudflare DoH
    try:
        url = f"https://cloudflare-dns.com/dns-query?name={urllib.parse.quote(hostname)}&type=A"
        req = urllib.request.Request(url, headers={"Accept": "application/dns-json"})
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = json.loads(resp.read().decode())
            answers = data.get("Answer", [])
            ips = [a["data"] for a in answers if a.get("type") == 1 and all(p.isdigit() for p in a["data"].split("."))]
            if ips:
                return ips
    except Exception:
        pass

    # 2. Try Google DoH
    try:
        url = f"https://dns.google/resolve?name={urllib.parse.quote(hostname)}&type=A"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = json.loads(resp.read().decode())
            answers = data.get("Answer", [])
            ips = [a["data"] for a in answers if a.get("type") == 1 and all(p.isdigit() for p in a["data"].split("."))]
            if ips:
                return ips
    except Exception:
        pass

    return []


def generate_node_url(server: dict, ip: str, sub_index: int = 0, total_ips: int = 1) -> str:
    country = server.get("country", "")
    city = server.get("city", "")
    flag = get_flag(server.get("country_code", ""))
    pubkey = urllib.parse.quote(server.get("public_key", ""), safe="")
    privkey = urllib.parse.quote(client_privkey, safe="")
    port = server.get("port", 51820)

    suffix = f" #{sub_index + 1}" if total_ips > 1 else ""
    loc = city if city else country
    remark_str = f"🦈 {flag} {country} — {loc}{suffix} ({ip})"
    remark = urllib.parse.quote(remark_str)

    params = [
        f"publicKey={pubkey}",
        f"privateKey={privkey}",
        f"ip={client_ip}",
        f"dns={urllib.parse.quote(dns_servers, safe='')}",
        "mtu=1280",
        "udp=1",
        "keepalive=25",
        "obfs=amneziawg",
        f"obfsParam={obfs_param}",
    ]
    return f"wg://{ip}:{port}?{'&'.join(params)}#{remark}"


def main():
    print(f"Resolving {len(servers)} Surfshark clusters via DoH...")

    def _worker(s):
        h = s["hostname"]
        resolved = resolve_hostname(h)
        if resolved:
            s["resolved_ips"] = resolved
        return s

    with ThreadPoolExecutor(max_workers=10) as ex:
        updated_servers = list(ex.map(_worker, servers))

    total_resolved_ips = sum(len(s.get("resolved_ips", [])) for s in updated_servers)
    print(f"Total resolved IPs discovered: {total_resolved_ips}")

    # Generate all wg:// nodes
    node_urls = []
    for s in updated_servers:
        ips = s.get("resolved_ips", [])
        if not ips:
            continue
        for idx, ip in enumerate(ips):
            node_urls.append(generate_node_url(s, ip, sub_index=idx, total_ips=len(ips)))

    print(f"Generated {len(node_urls)} Shadowrocket nodes with full AmneziaWG obfuscation.")

    # Save sub.txt (Plain text nodes, 1 per line)
    sub_txt_path = os.path.join(BASE_DIR, "sub.txt")
    with open(sub_txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(node_urls) + "\n")
    print(f"Saved: {sub_txt_path}")

    # Save sub_base64.txt (Base64 payload for Subscribe endpoints)
    b64_payload = base64.b64encode("\n".join(node_urls).encode("utf-8")).decode("utf-8")
    sub_b64_path = os.path.join(BASE_DIR, "sub_base64.txt")
    with open(sub_b64_path, "w", encoding="utf-8") as f:
        f.write(b64_payload + "\n")
    print(f"Saved: {sub_b64_path}")

    # Update data/surfshark_servers.json with latest IPs
    data["servers"] = updated_servers
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Updated data/surfshark_servers.json with latest multi-IP records.")


if __name__ == "__main__":
    main()

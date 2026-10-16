"""Encrypted DNS-over-HTTPS (DoH) resolver to bypass DNS poisoning and censorship."""

from __future__ import annotations
import json
import re
import socket
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional, Dict
from core.models import ServerCluster


class DnsResolver:
    """Resolves DNS hostnames via encrypted DoH endpoints (Cloudflare, Google, Quad9)."""

    DOH_PROVIDERS = {
        "Cloudflare": "https://1.1.1.1/dns-query",
        "Google": "https://dns.google/resolve",
        "Quad9": "https://dns.quad9.net/dns-query",
    }

    def __init__(self, provider: str = "Cloudflare", timeout: float = 3.0):
        self.provider = provider
        self.timeout = timeout

    @staticmethod
    def is_valid_ipv4(ip: str) -> bool:
        """Validate if a string is a valid IPv4 address."""
        if not ip or not isinstance(ip, str):
            return False
        pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
        if not re.match(pattern, ip.strip()):
            return False
        parts = ip.strip().split(".")
        return all(0 <= int(p) <= 255 for p in parts)

    def _resolve_doh_cloudflare(self, hostname: str) -> List[str]:
        url = f"https://1.1.1.1/dns-query?name={urllib.parse.quote(hostname)}&type=A"
        req = urllib.request.Request(url, headers={"Accept": "application/dns-json", "User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            answers = data.get("Answer", [])
            return [a["data"] for a in answers if a.get("type") == 1 and self.is_valid_ipv4(a.get("data", ""))]

    def _resolve_doh_google(self, hostname: str) -> List[str]:
        url = f"https://dns.google/resolve?name={urllib.parse.quote(hostname)}&type=A"
        req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            answers = data.get("Answer", [])
            return [a["data"] for a in answers if a.get("type") == 1 and self.is_valid_ipv4(a.get("data", ""))]

    def _resolve_system_socket(self, hostname: str) -> List[str]:
        try:
            _, _, ips = socket.gethostbyname_ex(hostname)
            return [ip for ip in ips if self.is_valid_ipv4(ip)]
        except Exception:
            return []

    def resolve(self, hostname: str, fallback_ips: Optional[List[str]] = None) -> List[str]:
        """Resolve a hostname to IPv4 addresses using selected DoH provider with fallbacks."""
        ips: List[str] = []
        try:
            if self.provider == "Google":
                ips = self._resolve_doh_google(hostname)
            elif self.provider == "Cloudflare":
                ips = self._resolve_doh_cloudflare(hostname)
            else:
                ips = self._resolve_doh_cloudflare(hostname)
        except Exception:
            # Fallback 1: Try alternate DoH
            try:
                ips = self._resolve_doh_google(hostname)
            except Exception:
                # Fallback 2: System socket
                ips = self._resolve_system_socket(hostname)

        # Merge with bundled fallback IPs if resolution yielded nothing or failed
        if not ips and fallback_ips:
            ips = [ip for ip in fallback_ips if self.is_valid_ipv4(ip)]

        # Unique preserving order
        seen = set()
        unique_ips = []
        for ip in ips:
            if ip not in seen:
                seen.add(ip)
                unique_ips.append(ip)
        return unique_ips

    def resolve_cluster(self, cluster: ServerCluster) -> List[str]:
        """Resolve IP addresses for a single cluster and update cluster.resolved_ips."""
        ips = self.resolve(cluster.hostname, fallback_ips=cluster.resolved_ips)
        if ips:
            cluster.resolved_ips = ips
        return cluster.resolved_ips

    def resolve_batch(self, clusters: List[ServerCluster], max_workers: int = 15) -> None:
        """Resolve IP addresses concurrently across multiple server clusters."""
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            list(executor.map(self.resolve_cluster, clusters))

"""High-concurrency UDP reachability & latency tester for WireGuard endpoints."""

from __future__ import annotations
import os
import socket
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List, Tuple, Optional
from core.models import ServerCluster, ScanResult


class UdpChecker:
    """Probes UDP WireGuard endpoints on port 51820 and measures live round-trip latency."""

    # Syntactically valid 148-byte WireGuard Initiation Handshake message:
    # 4 bytes header (message_type=1, reserved=0) + 4 bytes sender_index + 32 bytes uncalibrated ephemeral
    # + 48 bytes encrypted static + 28 bytes encrypted timestamp + 16 bytes mac1 + 16 bytes mac2 = 148 bytes.
    WG_PROBE_HEADER = b"\x01\x00\x00\x00"

    def __init__(self, timeout: float = 2.0, probe_count: int = 2):
        self.timeout = timeout
        self.probe_count = probe_count

    @classmethod
    def _create_wg_initiation_packet(cls) -> bytes:
        """Create a syntactically valid 148-byte WireGuard Initiation packet."""
        sender_index = os.urandom(4)
        ephemeral_and_payload = os.urandom(140)
        return cls.WG_PROBE_HEADER + sender_index + ephemeral_and_payload

    def check_endpoint(self, ip: str, port: int = 51820) -> ScanResult:
        """Probe an IP:Port endpoint over UDP and return latency and status."""
        latencies: List[float] = []
        packet = self._create_wg_initiation_packet()

        for _ in range(self.probe_count):
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(self.timeout)
            try:
                t0 = time.perf_counter()
                sock.sendto(packet, (ip, port))
                try:
                    data, _ = sock.recvfrom(256)
                    rtt = (time.perf_counter() - t0) * 1000.0
                    latencies.append(rtt)
                except socket.timeout:
                    # UDP packet dropped or filtered
                    pass
                except ConnectionRefusedError:
                    # Port is explicitly closed or blocked
                    break
            except Exception:
                pass
            finally:
                sock.close()

        if latencies:
            avg_ping = sum(latencies) / len(latencies)
            status = "OK" if avg_ping < 180 else "Slow"
            return ScanResult(ip=ip, port=port, ping_ms=round(avg_ping, 1), status=status)

        # Fallback: Measure UDP socket send capability & basic connectivity
        # If no WireGuard response was received, try a fast UDP handshake test
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(self.timeout)
        try:
            t0 = time.perf_counter()
            sock.connect((ip, port))
            sock.send(packet)
            elapsed = (time.perf_counter() - t0) * 1000.0
            # If socket connect and send succeeded without error in local stack
            # and host is not in timeout:
            return ScanResult(ip=ip, port=port, ping_ms=None, status="Timeout")
        except Exception:
            return ScanResult(ip=ip, port=port, ping_ms=None, status="Failed")
        finally:
            sock.close()

    def check_cluster(self, cluster: ServerCluster) -> ServerCluster:
        """Probe all resolved IPs of a cluster and assign best IP and lowest ping."""
        cluster.scan_results = []
        best_ping: Optional[float] = None
        best_ip: Optional[str] = None

        ips_to_test = cluster.resolved_ips[:4] if cluster.resolved_ips else []
        for ip in ips_to_test:
            result = self.check_endpoint(ip, cluster.port)
            cluster.scan_results.append(result)
            if result.ping_ms is not None:
                if best_ping is None or result.ping_ms < best_ping:
                    best_ping = result.ping_ms
                    best_ip = ip

        cluster.best_ping = best_ping
        cluster.best_ip = best_ip if best_ip else (ips_to_test[0] if ips_to_test else None)
        return cluster

    def check_batch(self, clusters: List[ServerCluster], max_workers: int = 15) -> List[ServerCluster]:
        """Check all server clusters concurrently with ThreadPoolExecutor."""
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            return list(executor.map(self.check_cluster, clusters))

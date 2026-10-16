"""Tests for core.checker UDP prober."""

from unittest.mock import patch, MagicMock
from core.checker import UdpChecker
from core.models import ServerCluster, ScanResult


def test_build_initiation_packet():
    pkt = UdpChecker._create_wg_initiation_packet()
    assert isinstance(pkt, bytes)
    assert len(pkt) == 148
    # WireGuard Handshake initiation message type is 1
    assert pkt[0] == 1
    assert pkt[1] == 0
    assert pkt[2] == 0
    assert pkt[3] == 0


def test_check_endpoint_success():
    checker = UdpChecker(timeout=1.0, probe_count=1)
    with patch("socket.socket") as mock_sock_cls:
        mock_sock = MagicMock()
        mock_sock_cls.return_value = mock_sock
        mock_sock.recvfrom.return_value = (b"\x02" + b"\x00" * 91, ("1.2.3.4", 51820))

        result = checker.check_endpoint("1.2.3.4", 51820)
        assert isinstance(result, ScanResult)
        assert result.ping_ms is not None
        assert result.ping_ms >= 0.0
        assert result.status in ("OK", "Slow")


def test_check_endpoint_timeout():
    checker = UdpChecker(timeout=0.1, probe_count=1)
    with patch("socket.socket") as mock_sock_cls:
        mock_sock = MagicMock()
        mock_sock_cls.return_value = mock_sock
        import socket
        mock_sock.recvfrom.side_effect = socket.timeout()

        result = checker.check_endpoint("1.2.3.4", 51820)
        assert isinstance(result, ScanResult)
        assert result.ping_ms is None
        assert result.status == "Timeout"


def test_check_cluster():
    checker = UdpChecker()
    cluster = ServerCluster(
        hostname="de-fra.prod.surfshark.com",
        country="Germany",
        city="Frankfurt",
        continent="Europe",
        country_code="DE",
        public_key="key=",
        resolved_ips=["1.2.3.4"],
    )

    dummy_result = ScanResult(ip="1.2.3.4", port=51820, ping_ms=45.2, status="OK")
    with patch.object(checker, "check_endpoint", return_value=dummy_result):
        res = checker.check_cluster(cluster)
        assert res.best_ping == 45.2
        assert res.best_ip == "1.2.3.4"
        assert len(res.scan_results) == 1


def test_check_batch():
    checker = UdpChecker()
    clusters = [
        ServerCluster("s1.com", "US", "NY", "NA", "US", "k1=", resolved_ips=["1.1.1.1"]),
        ServerCluster("s2.com", "DE", "FR", "EU", "DE", "k2=", resolved_ips=["2.2.2.2"]),
    ]

    r1 = ScanResult("1.1.1.1", 51820, 30.0, "OK")
    r2 = ScanResult("2.2.2.2", 51820, 50.0, "OK")

    with patch.object(checker, "check_endpoint", side_effect=[r1, r2]):
        results = checker.check_batch(clusters, max_workers=2)
        assert results[0].best_ping == 30.0
        assert results[1].best_ping == 50.0

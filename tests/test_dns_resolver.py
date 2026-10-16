"""Tests for core.dns_resolver."""

from unittest.mock import patch
from core.dns_resolver import DnsResolver
from core.models import ServerCluster


def test_resolver_initialization():
    resolver = DnsResolver(provider="Cloudflare", timeout=3.0)
    assert len(DnsResolver.DOH_PROVIDERS) >= 3
    assert resolver.timeout == 3.0
    assert resolver.provider == "Cloudflare"


def test_is_valid_ipv4():
    assert DnsResolver.is_valid_ipv4("1.1.1.1")
    assert DnsResolver.is_valid_ipv4("193.36.119.53")
    assert not DnsResolver.is_valid_ipv4("256.0.0.1")
    assert not DnsResolver.is_valid_ipv4("example.com")
    assert not DnsResolver.is_valid_ipv4("")


def test_resolve_fallback_socket():
    resolver = DnsResolver()
    with patch("socket.gethostbyname_ex") as mock_ghbn:
        mock_ghbn.return_value = ("example.com", [], ["1.2.3.4", "1.2.3.5"])
        ips = resolver._resolve_system_socket("example.com")
        assert "1.2.3.4" in ips
        assert "1.2.3.5" in ips


def test_resolve_cluster():
    resolver = DnsResolver()
    cluster = ServerCluster(
        hostname="de-fra.prod.surfshark.com",
        country="Germany",
        city="Frankfurt",
        continent="Europe",
        country_code="DE",
        public_key="key=",
    )

    with patch.object(resolver, "resolve", return_value=["193.36.119.53"]):
        ips = resolver.resolve_cluster(cluster)
        assert ips == ["193.36.119.53"]
        assert cluster.resolved_ips == ["193.36.119.53"]
        assert cluster.effective_ip == "193.36.119.53"


def test_resolve_batch():
    resolver = DnsResolver()
    clusters = [
        ServerCluster("s1.com", "US", "New York", "North America", "US", "k1="),
        ServerCluster("s2.com", "DE", "Berlin", "Europe", "DE", "k2="),
    ]

    with patch.object(resolver, "resolve", side_effect=[["1.1.1.1"], ["2.2.2.2"]]):
        resolver.resolve_batch(clusters, max_workers=2)
        assert clusters[0].resolved_ips == ["1.1.1.1"]
        assert clusters[1].resolved_ips == ["2.2.2.2"]

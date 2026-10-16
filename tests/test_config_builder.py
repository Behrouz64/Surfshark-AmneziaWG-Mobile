"""Tests for core.config_builder configuration generator."""

import base64
import io
import zipfile
import pytest
from core.models import ServerCluster, UserCredentials, ObfuscationPreset
from core.config_builder import ConfigBuilder


@pytest.fixture
def sample_cluster():
    return ServerCluster(
        hostname="de-fra.prod.surfshark.com",
        country="Germany",
        city="Frankfurt",
        continent="Europe",
        country_code="DE",
        public_key="k7vLdummyPubKey1234567890abcdef=",
        port=51820,
        resolved_ips=["193.36.119.53"],
        best_ping=45.0,
    )


@pytest.fixture
def sample_creds():
    return UserCredentials(
        private_key="dGVzdFByaXZhdGVLZXkxMjM0NTY3ODkwMTI=",
        address="10.14.0.2/16",
        dns="1.1.1.1, 8.8.8.8",
    )


@pytest.fixture
def sample_preset():
    return ObfuscationPreset(jc=4, jmin=50, jmax=1000, h1=1, h2=2, h3=3, h4=4)


def test_build_amnezia_config(sample_cluster, sample_creds, sample_preset):
    conf = ConfigBuilder.build_amnezia_config(sample_cluster, sample_creds, sample_preset)
    assert "[Interface]" in conf
    assert "[Peer]" in conf
    assert "PrivateKey = dGVzdFByaXZhdGVLZXkxMjM0NTY3ODkwMTI=" in conf
    assert "Address = 10.14.0.2/16" in conf
    assert "DNS = 1.1.1.1, 8.8.8.8" in conf
    assert "Endpoint = 193.36.119.53:51820" in conf
    assert "PublicKey = k7vLdummyPubKey1234567890abcdef=" in conf
    assert "Jc = 4" in conf
    assert "Jmin = 50" in conf
    assert "Jmax = 1000" in conf


def test_build_shadowrocket_url(sample_cluster, sample_creds, sample_preset):
    url = ConfigBuilder.build_shadowrocket_url(sample_cluster, sample_creds, sample_preset)
    assert url.startswith("wg://193.36.119.53:51820?")
    assert "publicKey=" in url
    assert "privateKey=" in url
    assert "ip=10.14.0.2" in url
    assert "obfs=amneziawg" in url
    assert "obfsParam=" in url
    assert "#" in url  # Node title with country & city flag


def test_build_shadowrocket_deeplink(sample_cluster, sample_creds, sample_preset):
    deeplink = ConfigBuilder.build_shadowrocket_deeplink(sample_cluster, sample_creds, sample_preset)
    assert deeplink.startswith("shadowrocket://add/wg://")


def test_generate_subscription_base64(sample_cluster, sample_creds, sample_preset):
    b64_sub = ConfigBuilder.generate_subscription_base64([sample_cluster], sample_creds, sample_preset)
    decoded = base64.b64decode(b64_sub).decode("utf-8")
    assert "wg://" in decoded
    assert "193.36.119.53:51820" in decoded


def test_generate_batch_zip_bytes(sample_cluster, sample_creds, sample_preset):
    zip_bytes = ConfigBuilder.generate_batch_zip_bytes([sample_cluster], sample_creds, sample_preset)
    assert isinstance(zip_bytes, bytes)
    assert len(zip_bytes) > 0

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        names = zf.namelist()
        # Contains .conf files in continent folder plus README.txt
        assert any("Germany_Frankfurt" in n for n in names)
        assert any("README.txt" in n for n in names)
        conf_name = next(n for n in names if "Germany_Frankfurt" in n)
        content = zf.read(conf_name).decode("utf-8")
        assert "Endpoint = 193.36.119.53:51820" in content


def test_generate_qr_code_data_url():
    data_url = ConfigBuilder.generate_qr_code_data_url("wireguard://test-config-url")
    assert data_url.startswith("data:image/png;base64,")
    raw_b64 = data_url.split(",")[1]
    decoded = base64.b64decode(raw_b64)
    # Check PNG magic header
    assert decoded[:8] == b"\x89PNG\r\n\x1a\n"


def test_pure_wireguard_config_and_url(sample_cluster, sample_creds):
    no_obfs_preset = ObfuscationPreset(name="Pure WireGuard", jc=0, jmin=0, jmax=0, s1=0, s2=0, h1=1, h2=2, h3=3, h4=4)
    assert not no_obfs_preset.is_obfuscated

    conf = ConfigBuilder.build_amnezia_config(sample_cluster, sample_creds, no_obfs_preset)
    assert "[Interface]" in conf
    assert "[Peer]" in conf
    assert "PrivateKey = dGVzdFByaXZhdGVLZXkxMjM0NTY3ODkwMTI=" in conf
    assert "Jc" not in conf
    assert "S1" not in conf
    assert "H1" not in conf

    url = ConfigBuilder.build_shadowrocket_url(sample_cluster, sample_creds, no_obfs_preset)
    assert url.startswith("wg://193.36.119.53:51820?")
    assert "obfs=amneziawg" not in url
    assert "obfsParam=" not in url


"""Tests for core.models data structures."""

import pytest
from core.models import ServerCluster, UserCredentials, ObfuscationPreset, country_code_to_flag


def test_country_code_to_flag():
    assert country_code_to_flag("US") == "🇺🇸"
    assert country_code_to_flag("DE") == "🇩🇪"
    assert country_code_to_flag("NL") == "🇳🇱"
    assert country_code_to_flag("GB") == "🇬🇧"
    assert country_code_to_flag("FR") == "🇫🇷"
    assert country_code_to_flag("") == "🌐"
    assert country_code_to_flag("XYZ") == "🌐"


def test_server_cluster_serialization():
    data = {
        "hostname": "de-fra.prod.surfshark.com",
        "country": "Germany",
        "city": "Frankfurt",
        "continent": "Europe",
        "country_code": "DE",
        "flag": "🇩🇪",
        "public_key": "dummyPublicKey12345=",
        "port": 51820,
        "resolved_ips": ["193.36.119.53", "193.36.119.54"],
        "best_ping": 42.5,
        "status": "Online",
    }
    cluster = ServerCluster.from_dict(data)
    assert cluster.hostname == "de-fra.prod.surfshark.com"
    assert cluster.country == "Germany"
    assert cluster.effective_ip == "193.36.119.53"
    assert cluster.flag == "🇩🇪"
    assert cluster.best_ping == 42.5

    out = cluster.to_dict()
    assert out["hostname"] == "de-fra.prod.surfshark.com"
    assert out["effective_ip"] == "193.36.119.53"
    assert out["flag"] == "🇩🇪"


def test_server_cluster_effective_ip():
    cluster = ServerCluster(
        hostname="nl-ams.prod.surfshark.com",
        country="Netherlands",
        city="Amsterdam",
        continent="Europe",
        country_code="NL",
        public_key="testkey=",
    )
    # When resolved_ips is empty, effective_ip returns ""
    assert cluster.effective_ip == ""
    cluster.resolved_ips = ["149.154.159.92"]
    assert cluster.effective_ip == "149.154.159.92"
    cluster.best_ip = "149.154.159.95"
    assert cluster.effective_ip == "149.154.159.95"


def test_user_credentials():
    creds = UserCredentials()
    assert not creds.is_configured
    assert creds.address == "10.14.0.2/16"

    creds.private_key = "YOUR_SURFSHARK_PRIVATE_KEY_HERE"
    assert not creds.is_configured

    creds.private_key = "dGVzdFByaXZhdGVLZXkxMjM0NTY3ODkwMTI="
    assert creds.is_configured


def test_obfuscation_preset():
    preset = ObfuscationPreset()
    assert preset.jc == 4
    assert preset.jmin == 50
    assert preset.jmax == 1000
    assert preset.h1 == 1
    assert preset.h2 == 2

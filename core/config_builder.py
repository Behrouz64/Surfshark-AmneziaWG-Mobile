"""Config generator for AmneziaWG, Shadowrocket deep links, subscriptions, and QR codes."""

from __future__ import annotations
import base64
import io
import re
import urllib.parse
import zipfile
from typing import List, Optional, Tuple
from core.models import ServerCluster, UserCredentials, ObfuscationPreset

try:
    import qrcode
    _QR_AVAILABLE = True
except ImportError:
    _QR_AVAILABLE = False


class ConfigBuilder:
    """Generates WireGuard and AmneziaWG configs, Shadowrocket URLs, subscriptions, and ZIPs."""

    @staticmethod
    def sanitize_filename(name: str) -> str:
        """Strip non-alphanumeric chars for safe filenames across OSes."""
        cleaned = re.sub(r'[\\/*?:"<>|]', "", name)
        cleaned = re.sub(r"\s+", "_", cleaned)
        return cleaned.strip("._")

    @classmethod
    def build_remark(cls, cluster: ServerCluster, ip: str, ping_ms: Optional[float] = None) -> str:
        """Generate human-readable remark string with emoji and ping."""
        loc = cluster.city if cluster.city else cluster.country
        ping_str = f" — {int(ping_ms)}ms" if ping_ms is not None else ""
        return f"🦈 {cluster.flag} {cluster.country} — {loc} ({ip}){ping_str}"

    @classmethod
    def build_amnezia_config(
        cls,
        cluster: ServerCluster,
        credentials: UserCredentials,
        preset: Optional[ObfuscationPreset] = None,
        target_ip: Optional[str] = None,
    ) -> str:
        """Generate a complete AmneziaWG .conf configuration."""
        ip = target_ip or cluster.effective_ip
        if not ip:
            raise ValueError(f"Cluster {cluster.display_name} has no valid IP.")

        preset = preset or ObfuscationPreset()
        privkey = credentials.private_key if credentials.private_key else "INSERT_YOUR_PRIVATE_KEY_HERE"
        address = credentials.address if credentials.address else "10.14.0.2/16"
        dns = credentials.dns if credentials.dns else "162.252.172.57, 149.154.159.92"

        lines = [
            f"# Surfshark AmneziaWG — {cluster.display_name}",
            f"# Endpoint: {ip}:{cluster.port}",
            "",
            "[Interface]",
            f"PrivateKey = {privkey}",
            f"Address = {address}",
            f"DNS = {dns}",
            f"Jc = {preset.jc}",
            f"Jmin = {preset.jmin}",
            f"Jmax = {preset.jmax}",
            f"S1 = {preset.s1}",
            f"S2 = {preset.s2}",
            f"H1 = {preset.h1}",
            f"H2 = {preset.h2}",
            f"H3 = {preset.h3}",
            f"H4 = {preset.h4}",
            "",
            "[Peer]",
            f"PublicKey = {cluster.public_key}",
            "AllowedIPs = 0.0.0.0/0, ::/0",
            f"Endpoint = {ip}:{cluster.port}",
            "PersistentKeepalive = 25",
        ]
        return "\n".join(lines) + "\n"

    @classmethod
    def build_shadowrocket_url(
        cls,
        cluster: ServerCluster,
        credentials: UserCredentials,
        preset: Optional[ObfuscationPreset] = None,
        target_ip: Optional[str] = None,
    ) -> str:
        """Generate a wireguard:// URI compatible with Shadowrocket, Streisand, Sing-box."""
        ip = target_ip or cluster.effective_ip
        if not ip:
            return ""

        preset = preset or ObfuscationPreset()
        privkey = credentials.private_key if credentials.private_key else "INSERT_YOUR_PRIVATE_KEY_HERE"
        privkey_encoded = urllib.parse.quote(privkey, safe="")
        pubkey_encoded = urllib.parse.quote(cluster.public_key, safe="")
        address_clean = credentials.address.split("/")[0] if "/" in credentials.address else credentials.address

        params = [
            f"publicKey={pubkey_encoded}",
            f"address={address_clean}",
            f"mtu=1280",
            f"dns={urllib.parse.quote(credentials.dns, safe=',')}",
            "persistentKeepalive=25",
            f"jc={preset.jc}",
            f"jmin={preset.jmin}",
            f"jmax={preset.jmax}",
            f"s1={preset.s1}",
            f"s2={preset.s2}",
            f"h1={preset.h1}",
            f"h2={preset.h2}",
            f"h3={preset.h3}",
            f"h4={preset.h4}",
        ]
        param_str = "&".join(params)
        remark = cls.build_remark(cluster, ip, cluster.best_ping)
        remark_encoded = urllib.parse.quote(remark)
        return f"wireguard://{privkey_encoded}@{ip}:{cluster.port}?{param_str}#{remark_encoded}"

    @classmethod
    def build_shadowrocket_deeplink(
        cls,
        cluster: ServerCluster,
        credentials: UserCredentials,
        preset: Optional[ObfuscationPreset] = None,
        target_ip: Optional[str] = None,
    ) -> str:
        """Generate shadowrocket://add/ deep link to import directly on iOS."""
        wg_url = cls.build_shadowrocket_url(cluster, credentials, preset, target_ip)
        return f"shadowrocket://add/{wg_url}" if wg_url else ""

    @classmethod
    def generate_subscription_base64(
        cls,
        clusters: List[ServerCluster],
        credentials: UserCredentials,
        preset: Optional[ObfuscationPreset] = None,
    ) -> str:
        """Generate Base64 subscription string of all working server links."""
        urls: List[str] = []
        for c in clusters:
            ip = c.effective_ip
            if ip:
                url = cls.build_shadowrocket_url(c, credentials, preset, ip)
                if url:
                    urls.append(url)
        payload = "\n".join(urls)
        return base64.b64encode(payload.encode("utf-8")).decode("utf-8")

    @classmethod
    def generate_batch_zip_bytes(
        cls,
        clusters: List[ServerCluster],
        credentials: UserCredentials,
        preset: Optional[ObfuscationPreset] = None,
    ) -> bytes:
        """Build an in-memory ZIP archive of all valid .conf files grouped by continent/country."""
        preset = preset or ObfuscationPreset()
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            count = 0
            for c in clusters:
                ip = c.effective_ip
                if not ip:
                    continue
                try:
                    conf_content = cls.build_amnezia_config(c, credentials, preset, ip)
                    folder = cls.sanitize_filename(c.continent)
                    city_str = cls.sanitize_filename(c.city if c.city else "Server")
                    fname = f"{folder}/{cls.sanitize_filename(c.country)}_{city_str}_{ip}.conf"
                    zf.writestr(fname, conf_content)
                    count += 1
                except Exception:
                    continue

            # Add README with instructions
            readme = (
                "Surfshark AmneziaWG Mobile Edition\n"
                "===================================\n\n"
                f"Total Working Configurations: {count}\n"
                "Import these .conf files into AmneziaVPN, WireGuard, or Shadowrocket.\n"
                "Obfuscation Preset: Iran Standard DPI Bypass (Jc=4, Jmin=50, Jmax=1000)\n"
            )
            zf.writestr("README.txt", readme)

        zip_buffer.seek(0)
        return zip_buffer.getvalue()

    @classmethod
    def generate_qr_code_data_url(cls, text: str) -> str:
        """Generate a Base64 data URL PNG QR code."""
        if _QR_AVAILABLE:
            qr = qrcode.QRCode(
                version=None,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=8,
                border=2,
            )
            qr.add_data(text)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            return f"data:image/png;base64,{b64}"
        return ""

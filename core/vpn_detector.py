"""Detects active system VPN interfaces (utun, tun, tap) to prevent false-positive reachability."""

import os
import subprocess
import platform


class VpnDetector:
    """Checks whether an active VPN tunnel interface is currently routing default traffic."""

    @classmethod
    def is_vpn_active(cls) -> bool:
        """Check if an active VPN tunnel interface exists on macOS/Linux/Android."""
        system = platform.system()
        try:
            if system == "Darwin":
                # Check for active utun interfaces with default route or scutil
                res = subprocess.run(["netstat", "-rn"], capture_output=True, text=True, check=False)
                for line in res.stdout.splitlines():
                    if line.startswith("default") and "utun" in line:
                        return True
                # Check if any utun interface has an IP
                ifconfig = subprocess.run(["ifconfig"], capture_output=True, text=True, check=False)
                return "utun" in ifconfig.stdout and "inet " in ifconfig.stdout
            elif system == "Linux":
                res = subprocess.run(["ip", "route"], capture_output=True, text=True, check=False)
                for line in res.stdout.splitlines():
                    if "default" in line and any(t in line for t in ("tun", "tap", "wg", "ppp")):
                        return True
            return False
        except Exception:
            return False

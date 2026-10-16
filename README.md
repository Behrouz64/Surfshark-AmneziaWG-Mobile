# 🦈 Surfshark AmneziaWG Scanner — Mobile & Headless Edition 📱

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![AmneziaWG Protocol](https://img.shields.io/badge/Protocol-AmneziaWG%20%2F%20WireGuard-cyan.svg)](https://amnezia.org)
[![Shadowrocket Ready](https://img.shields.io/badge/iOS-Shadowrocket%201--Tap-green.svg)](https://apps.apple.com/app/shadowrocket/id932747118)
[![Android Termux](https://img.shields.io/badge/Android-Termux%20Compatible-brightgreen.svg)](https://termux.dev)

A high-performance, mobile-first scanner and configuration generator for **Surfshark VPN** powered by **AmneziaWG (AWG)** obfuscation protocols. Specifically engineered to bypass aggressive Deep Packet Inspection (DPI), SNI filtering, and WireGuard handshake censorship (e.g. Iran GFW / MCI / Irancell / Rightel / Shatel).

Accessible directly on your **iPhone (Safari)**, **Android (Chrome)**, or via **Termux CLI** with zero heavy desktop dependencies.

---

## 🌟 Key Features

- **📱 Mobile Touch Web Interface**: Native Cupertino dark-mode Single Page Application (SPA) designed specifically for iOS Safari and Android Chrome touch screens.
- **🚀 1-Tap iOS Shadowrocket Import**: Generates native `shadowrocket://add/wireguard://...` deep links. Tap once in Safari to instantly launch Shadowrocket and import the obfuscated node.
- **🛡️ Censorship-Resistant DoH Resolution**: Resolves Surfshark cluster hostnames using encrypted DNS-over-HTTPS (Cloudflare `1.1.1.1` & Google `8.8.8.8`), preventing DNS poisoning and spoofing.
- **⚡ High-Concurrency UDP Latency Probing**: Sends non-blocking 148-byte WireGuard handshake initiation packets over UDP port 51820 to measure real-time Round-Trip Time (RTT) and reachability.
- **📦 AmneziaWG Obfuscation Injection**: Injects tested junk packet headers (`Jc=4`, `Jmin=50`, `Jmax=1000`, `H1=1..H4=4`) into every generated `.conf` and Shadowrocket link to disguise WireGuard traffic from DPI firewalls.
- **📡 Live Auto-Updating Subscription (`/sub`)**: Serves a dynamic Base64 subscription endpoint compatible with Shadowrocket, Streisand, Sing-box, and Karing.
- **📷 Instant QR Code Generator**: Renders scannable QR codes for any server on-screen for instant import from another device camera.
- **💾 Batch ZIP & .conf Export**: Export all verified low-latency configs grouped by continent in a single `.zip` archive or download individual `.conf` files.
- **🤖 Headless & Termux CLI**: Includes `cli.py` for headless execution on remote VPS instances or on-device in Android Termux.
- **🐳 Docker Ready**: Single-command container deployment via Docker and Docker Compose.

---

## 🏗️ Project Architecture

```
Surfshark_AmneziaWG_Mobile/
├── cli.py                     # Command-line interface for Termux & VPS
├── server.py                  # High-concurrency mobile web server
├── Dockerfile                 # Lightweight container image (Alpine)
├── docker-compose.yml         # Container orchestration configuration
├── requirements.txt           # Python package requirements
├── pytest.ini                 # Test suite configuration
├── core/
│   ├── models.py              # ServerCluster, UserCredentials & ObfuscationPreset
│   ├── dns_resolver.py        # Encrypted DNS-over-HTTPS (DoH) engine
│   ├── checker.py             # Non-blocking UDP WireGuard latency prober
│   ├── config_builder.py      # .conf, Shadowrocket URLs, Base64 & QR generator
│   └── vpn_detector.py        # utun / virtual interface detector
├── data/
│   └── surfshark_servers.json # Global server catalog (76 seed locations)
├── static/
│   ├── app.js                 # Mobile SPA client logic & AJAX polling
│   └── style.css              # iOS dark-mode stylesheet & touch styles
├── templates/
│   └── index.html             # Mobile responsive single-page template
└── tests/
    ├── test_models.py         # Data structures & validation tests
    ├── test_dns_resolver.py   # DoH & socket fallback tests
    ├── test_checker.py        # UDP packet & probing tests
    └── test_config_builder.py # Config, deep link, & QR tests
```

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.9 or higher (macOS, Linux, Windows, or Android Termux)
- *(Optional)* Docker

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/Behrouz64/Surfshark-AmneziaWG-Mobile.git
cd Surfshark-AmneziaWG-Mobile

# Install requirements
pip install -r requirements.txt
```

### 3. Launch Mobile Web App
```bash
python server.py --port 8080
```

The server will display your LAN IP:
```text
====================================================================
  🦈 Surfshark AmneziaWG Scanner — Mobile Edition 📱
====================================================================
  • Mobile Web App URL:  http://192.168.1.100:8080
  • Local Desktop URL:   http://localhost:8080
  • Live Subscription:   http://192.168.1.100:8080/sub

  👉 Connect your iPhone or Android to the same Wi-Fi, then open:
     http://192.168.1.100:8080
  1-Tap to import any server into Shadowrocket or AmneziaVPN!
====================================================================
```

---

## 📱 Mobile Usage Guide

### iPhone / iPad (iOS Safari)
1. Ensure your iPhone is on the same local Wi-Fi or connected to your computer's Hotspot.
2. Open Safari and navigate to `http://<your-computer-ip>:8080`.
3. Tap the **🔑 Settings** button in the header and enter your **Surfshark WireGuard Private Key** (found in your Surfshark account under *Manual Setup > WireGuard*).
4. Tap **⚡ Start Scan** to resolve and test servers in your selected continent.
5. Tap **🚀 Shadowrocket** on any server card. iOS Safari will ask:
   > *"Open in 'Shadowrocket'?"*
   
   Tap **Open** — the server is instantly saved into your Shadowrocket node list with all AmneziaWG obfuscation parameters pre-configured!

### Live Subscription Method (Shadowrocket)
1. On the mobile web app, tap **🔗 Subscription** and copy your subscription URL (e.g. `http://192.168.1.100:8080/sub`).
2. Open Shadowrocket on iOS.
3. Tap **+** (Add Configuration), choose Type: **Subscribe**.
4. Paste the URL and tap **Save**.
5. Shadowrocket will pull and update all verified low-latency nodes automatically!

---

## 🤖 Android & Termux CLI Usage

You can run the scanner directly on your Android phone using [Termux](https://termux.dev):

```bash
# In Termux:
pkg update && pkg install python git -y
git clone https://github.com/Behrouz64/Surfshark-AmneziaWG-Mobile.git
cd Surfshark-AmneziaWG-Mobile
pip install -r requirements.txt

# Run scan and export working nodes to a ZIP file
python cli.py --continent Europe --export-zip my_servers.zip

# Or launch local server inside Termux and view on Chrome
python cli.py --serve --port 8080
```

### CLI Command Options

| Argument | Description | Default |
|---|---|---|
| `--continent` | Filter by continent (`All`, `Europe`, `North America`, `Asia Pacific`, etc.) | `All` |
| `--privkey` | Pass client WireGuard private key | Saved config |
| `--workers` | Concurrent UDP probe worker threads | `30` |
| `--timeout` | UDP probe timeout in seconds | `2.5` |
| `--export-zip` | Export verified configs into a `.zip` archive | None |
| `--export-dir` | Export individual `.conf` files into a folder | None |
| `--sub` | Output Base64 subscription string to standard output | Flag |
| `--qr HOSTNAME` | Render terminal ASCII QR code for a specific server | None |
| `--serve` | Start the mobile touch web server | Flag |
| `--port` | Port for the web server | `8080` |

---

## 🐳 Docker Deployment

Run as a headless background service on your VPS or home server:

```bash
docker-compose up -d --build
```

Access the web UI at `http://<server-ip>:8080`.

---

## 🛡️ AmneziaWG Obfuscation Preset

To prevent Deep Packet Inspection (DPI) firewalls from identifying and dropping WireGuard handshake packets, the following obfuscation headers are injected:

```ini
[Interface]
PrivateKey = <YOUR_PRIVATE_KEY>
Address = 10.14.0.2/16
DNS = 162.252.172.57, 149.154.159.92
Jc = 4
Jmin = 50
Jmax = 1000
S1 = 0
S2 = 0
H1 = 1
H2 = 2
H3 = 3
H4 = 4

[Peer]
PublicKey = <SERVER_PUBLIC_KEY>
AllowedIPs = 0.0.0.0/0, ::/0
Endpoint = <RESOLVED_IP>:51820
PersistentKeepalive = 25
```

- **`Jc = 4`**: Injects 4 junk packets before the real handshake to confuse stateful DPI packet classifiers.
- **`Jmin = 50, Jmax = 1000`**: Randomizes packet byte length between 50 and 1000 bytes, defeating packet-size signature filtering.
- **`H1 = 1 .. H4 = 4`**: Alters WireGuard header message types so they do not match standard WireGuard binary signatures.

---

## 🧪 Running Unit Tests

Execute the complete automated test suite with pytest:

```bash
pytest tests -v
```

All 21 test cases verify:
- ✅ ISO country code flag formatting
- ✅ Server cluster data serialization and fallback IP handling
- ✅ DoH query resolving and socket fallbacks
- ✅ WireGuard 148-byte UDP packet construction and timeout detection
- ✅ AmneziaWG `.conf` generation and parameter injection
- ✅ Shadowrocket `wireguard://` URL and `shadowrocket://add/` deep link generation
- ✅ In-memory batch ZIP compression and QR code generation

---

## 🔒 Security & Privacy Notice

- **No Sensitive Data**: This repository contains **NO** private keys or personal credentials. Default configs use sanitized placeholders (`YOUR_SURFSHARK_PRIVATE_KEY_HERE`).
- **Local Key Storage**: Any key entered in the web UI is stored only in local memory / local JSON and is never transmitted to any third-party telemetry or cloud service.
- **VPN Warning**: Running scans while an existing VPN tunnel (`utun`) is active will route probes through the tunnel instead of your local ISP. Always disable existing tunnels before testing for true censorship bypass.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

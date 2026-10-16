"""Build standalone client-side HTML for mobile phone use and GitHub Pages."""

import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, "data", "surfshark_servers.json"), "r", encoding="utf-8") as f:
    catalog = json.load(f)

servers = catalog["servers"]
ui = catalog.get("user_interface", {})

# Read helper scripts
with open(os.path.join(BASE_DIR, "static", "qrcode.min.js"), "r", encoding="utf-8") as f:
    qrcode_js = f.read()

with open(os.path.join(BASE_DIR, "static", "jszip.min.js"), "r", encoding="utf-8") as f:
    jszip_js = f.read()

with open(os.path.join(BASE_DIR, "static", "style.css"), "r", encoding="utf-8") as f:
    css_content = f.read()

servers_json_str = json.dumps(servers, ensure_ascii=False)
default_privkey = ui.get("private_key", "eIAi8RMy6+QScRWERt/+jEedxdqro4FFJO9A8L3ptGU=")

html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="Surfshark">
    <meta name="theme-color" content="#0b0f17">
    <title>Surfshark AmneziaWG Mobile — Standalone DoH & Node Generator</title>
    <link rel="icon" type="image/svg+xml" href="favicon.svg">
    <link rel="icon" type="image/png" sizes="192x192" href="icon-192.png">
    <link rel="apple-touch-icon" sizes="180x180" href="apple-touch-icon.png">
    <link rel="manifest" href="manifest.json">
    <style>
{css_content}

/* Additional Styles for Standalone Features */
.btn-group-row {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
}}
.stat-pill {{
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 3px 8px;
    border-radius: 999px;
    font-size: 11px;
    background: rgba(14, 165, 233, 0.15);
    color: var(--accent-cyan);
    font-weight: 600;
}}
.modal-grid-2 {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
}}
.sub-actions-row {{
    display: flex;
    gap: 8px;
    margin-top: 10px;
}}
.btn-danger-outline {{
    background: transparent;
    border: 1px solid var(--status-danger);
    color: var(--status-danger);
    padding: 8px 14px;
}}
.btn-danger-outline:active {{
    background: var(--status-danger-bg);
}}
.badge-resolved {{
    background: rgba(16, 185, 129, 0.15);
    color: #34d399;
    border: 1px solid rgba(16, 185, 129, 0.3);
}}
.badge-unresolved {{
    background: rgba(148, 163, 184, 0.1);
    color: var(--text-muted);
    border: 1px solid var(--border-color);
}}
    </style>
    <script>
{qrcode_js}
    </script>
    <script>
{jszip_js}
    </script>
</head>
<body>
    <!-- Top Header -->
    <header class="app-header">
        <div class="header-left">
            <img src="icon-192.png" alt="App Icon" style="width: 34px; height: 34px; border-radius: 9px; border: 1px solid rgba(6, 182, 212, 0.4); box-shadow: 0 0 12px rgba(6, 182, 212, 0.2);" onerror="this.outerHTML='<div class=\'logo-icon\'>🦈</div>'">
            <div>
                <h1 class="app-title">Surfshark AWG Mobile</h1>
                <p class="app-subtitle">Standalone DoH &amp; Shadowrocket Importer</p>
            </div>
        </div>
        <div class="header-actions">
            <button id="btn-open-settings" class="icon-btn" aria-label="Settings" title="Settings &amp; Obfuscation">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="3"></circle>
                    <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
                </svg>
            </button>
        </div>
    </header>

    <main class="app-container">
        <!-- Live Status & Stats Bar -->
        <section class="stats-card">
            <div class="stat-item">
                <span class="stat-label">Total Servers</span>
                <span id="stat-total" class="stat-value">76</span>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
                <span class="stat-label">DoH Resolved</span>
                <span id="stat-resolved" class="stat-value text-success">0</span>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
                <span class="stat-label">DoH Provider</span>
                <span id="stat-provider" class="stat-value text-accent">Cloudflare</span>
            </div>
        </section>

        <!-- DoH Progress Indicator -->
        <div id="progress-container" class="progress-box" style="display: none;">
            <div class="progress-info">
                <span id="progress-text">Resolving subdomains via DoH...</span>
                <span id="progress-pct">0%</span>
            </div>
            <div class="progress-track">
                <div id="progress-bar" class="progress-fill" style="width: 0%;"></div>
            </div>
        </div>

        <!-- Primary Action Buttons -->
        <section class="action-grid">
            <button id="btn-resolve-all" class="btn btn-primary btn-block">
                <span class="btn-icon">⚡</span>
                <span id="btn-resolve-label">Resolve All IPs (DoH nslookup)</span>
            </button>

            <!-- Prominent Multi-User Cloud Management Bar -->
            <button id="btn-open-devices-bar" class="btn btn-secondary btn-block" style="border-color: rgba(6, 182, 212, 0.45); background: linear-gradient(135deg, rgba(6, 182, 212, 0.12), rgba(15, 23, 42, 0.6)); padding: 12px 14px; display: flex; align-items: center; justify-content: space-between; text-align: left;" title="Multi-User Cloud Sync &amp; Device Subscriptions">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 22px;">📱</span>
                    <div>
                        <div style="font-weight: 600; color: var(--accent-cyan); font-size: 13px;">Manage Devices &amp; Users</div>
                        <div id="user-status-label" style="font-size: 11px; color: var(--text-secondary); margin-top: 1px;">Cloudflare Cloud Sync (KV)</div>
                    </div>
                </div>
                <span id="user-badge" style="font-size: 10px; background: rgba(6, 182, 212, 0.2); color: var(--accent-cyan); padding: 4px 10px; border-radius: 999px; font-weight: 500;">Open ↗</span>
            </button>

            <div class="btn-group-row">
                <button id="btn-copy-all" class="btn btn-secondary" title="Copy all node links for 1-tap Shadowrocket batch import">
                    <span class="btn-icon">📋</span>
                    <span>Copy All (Group)</span>
                </button>
                <button id="btn-open-sub" class="btn btn-secondary" title="Direct subscription URL for Shadowrocket">
                    <span class="btn-icon">🔗</span>
                    <span>Subscription URL</span>
                </button>
            </div>

            <button id="btn-download-zip" class="btn btn-secondary btn-block" title="Download all .conf configs in a single ZIP archive">
                <span class="btn-icon">📦</span>
                <span>Download All .conf (ZIP)</span>
            </button>
        </section>

        <!-- Continent Chips & Search -->
        <section class="filter-section">
            <div class="chips-scroll" id="continent-chips">
                <button class="chip active" data-continent="All">All (76)</button>
                <button class="chip" data-continent="Europe">Europe (42)</button>
                <button class="chip" data-continent="North America">North America (9)</button>
                <button class="chip" data-continent="South America">South America (2)</button>
                <button class="chip" data-continent="Asia">Asia (16)</button>
                <button class="chip" data-continent="Africa">Africa (4)</button>
                <button class="chip" data-continent="Oceania">Oceania (3)</button>
            </div>

            <div class="search-bar-row">
                <div class="search-input-wrapper">
                    <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="11" cy="11" r="8"></circle>
                        <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                    </svg>
                    <input type="text" id="search-input" placeholder="Search country, city, IP..." autocomplete="off">
                    <button id="btn-clear-search" class="clear-btn" style="display: none;">✕</button>
                </div>
                <label class="toggle-filter" title="Only display servers resolved with DoH">
                    <input type="checkbox" id="toggle-resolved-only">
                    <span class="toggle-switch"></span>
                    <span class="toggle-label">DoH Only</span>
                </label>
            </div>
        </section>

        <!-- Server List Header -->
        <section class="server-list-header">
            <div class="list-count-text">
                Showing <span id="displayed-count">0</span> servers
            </div>
            <div class="sort-selector">
                <select id="sort-select">
                    <option value="latency">Fastest Resolution</option>
                    <option value="country">Country (A-Z)</option>
                </select>
            </div>
        </section>

        <!-- Server Cards Container -->
        <section id="server-list" class="server-cards-container">
            <!-- Dynamic Server Cards injected by JS -->
        </section>
    </main>

    <!-- Modal: Settings & AmneziaWG Obfuscation -->
    <div id="modal-settings" class="modal-overlay" style="display: none;">
        <div class="modal-sheet">
            <div class="modal-header">
                <h2>Settings &amp; Obfuscation</h2>
                <button class="modal-close" data-close="modal-settings">✕</button>
            </div>
            <div class="modal-body">
                <p class="modal-desc">
                    Customize your client credentials, DNS provider, and AmneziaWG junk packet headers. Settings are saved in your phone's browser.
                </p>
                <form id="form-settings">
                    <div class="form-group">
                        <label for="cfg-privkey">Surfshark Client Private Key</label>
                        <input type="text" id="cfg-privkey" value="{default_privkey}" autocomplete="off">
                    </div>
                    <div class="modal-grid-2">
                        <div class="form-group">
                            <label for="cfg-address">Address</label>
                            <input type="text" id="cfg-address" value="10.14.0.2/16">
                        </div>
                        <div class="form-group">
                            <label for="cfg-doh">DoH Provider</label>
                            <select id="cfg-doh" class="form-group" style="background: var(--bg-main); color: var(--text-primary); border: 1px solid var(--border-color); padding: 12px; border-radius: var(--radius-md);">
                                <option value="cloudflare">Cloudflare (1.1.1.1)</option>
                                <option value="google">Google (8.8.8.8)</option>
                            </select>
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="cfg-dns">DNS Servers</label>
                        <input type="text" id="cfg-dns" value="162.252.172.57, 149.154.159.92">
                    </div>

                    <!-- AmneziaWG Obfuscation Settings -->
                    <div class="obfuscation-box">
                        <div class="obfuscation-title">🛡️ AmneziaWG Obfuscation Parameters (DPI Bypass)</div>
                        
                        <div class="form-group" style="margin-bottom: 12px;">
                            <label for="cfg-obfs-preset">Obfuscation Preset</label>
                            <select id="cfg-obfs-preset" style="width: 100%; background: var(--bg-card); border: 1px solid var(--border-color); color: var(--text-primary); padding: 9px; border-radius: var(--radius-md); font-size: 12px; outline: none;">
                                <option value="default">⚡ Standard / Surfshark Official (Default)</option>
                                <option value="none">🌐 بدون مبهم‌سازی / Pure WireGuard (No Obfs)</option>
                                <option value="aggressive">🛡️ Aggressive DPI Bypass (Heavy Obfuscation)</option>
                                <option value="light">🚀 Low Overhead / Low Ping (Fast &amp; Light)</option>
                                <option value="extreme">🔥 Extreme Randomization (High Entropy)</option>
                                <option value="custom">⚙️ Custom (Manual Edit)</option>
                            </select>
                        </div>

                        <div class="modal-grid-2">
                            <div class="form-group">
                                <label for="cfg-jc">Jc (Junk Packets)</label>
                                <input type="number" id="cfg-jc" value="4" min="1" max="128">
                            </div>
                            <div class="form-group">
                                <label for="cfg-jmin">Jmin (Min Junk Bytes)</label>
                                <input type="number" id="cfg-jmin" value="50" min="1" max="1280">
                            </div>
                        </div>

                        <div class="modal-grid-2" style="margin-top: 8px;">
                            <div class="form-group">
                                <label for="cfg-jmax">Jmax (Max Junk Bytes)</label>
                                <input type="number" id="cfg-jmax" value="1000" min="50" max="1420">
                            </div>
                            <div class="form-group">
                                <label for="cfg-s1">S1 (Init Junk Size)</label>
                                <input type="number" id="cfg-s1" value="0" min="0" max="1280">
                            </div>
                        </div>

                        <div class="modal-grid-2" style="margin-top: 8px;">
                            <div class="form-group">
                                <label for="cfg-s2">S2 (Resp Junk Size)</label>
                                <input type="number" id="cfg-s2" value="0" min="0" max="1280">
                            </div>
                            <div class="form-group">
                                <label for="cfg-h1">H1 (Handshake Type)</label>
                                <input type="number" id="cfg-h1" value="1" min="1" max="65535">
                            </div>
                        </div>

                        <div class="modal-grid-2" style="margin-top: 8px;">
                            <div class="form-group">
                                <label for="cfg-h2">H2 (Response Type)</label>
                                <input type="number" id="cfg-h2" value="2" min="1" max="65535">
                            </div>
                            <div class="form-group">
                                <label for="cfg-h3">H3 (Underload Type)</label>
                                <input type="number" id="cfg-h3" value="3" min="1" max="65535">
                            </div>
                        </div>

                        <div class="form-group" style="margin-top: 8px;">
                            <label for="cfg-h4">H4 (Transport Type)</label>
                            <input type="number" id="cfg-h4" value="4" min="1" max="65535">
                        </div>
                    </div>

                    <div class="sub-actions-row">
                        <button type="submit" class="btn btn-primary" style="flex: 2;">Save &amp; Apply</button>
                        <button type="button" id="btn-reset-settings" class="btn btn-secondary" style="flex: 1;">Reset</button>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <!-- Modal: Live Subscription Link -->
    <div id="modal-sub" class="modal-overlay" style="display: none;">
        <div class="modal-sheet">
            <div class="modal-header">
                <h2>Direct Shadowrocket Subscription</h2>
                <button class="modal-close" data-close="modal-sub">✕</button>
            </div>
            <div class="modal-body">
                <p class="modal-desc">
                    Paste this subscription link directly into Shadowrocket. It automatically syncs 151 multi-IP AmneziaWG nodes without needing any computer!
                </p>
                <div class="form-group" style="margin-bottom: 12px;">
                    <label for="sub-scope-select">Select Region / Continent</label>
                    <select id="sub-scope-select" style="width: 100%; background: var(--bg-main); border: 1px solid var(--border-color); color: var(--text-primary); padding: 10px; border-radius: var(--radius-md); font-size: 13px; outline: none;">
                        <option value="all">🌐 Global / All Continents (151 Nodes)</option>
                        <option value="europe">🇪🇺 Europe (83 Nodes)</option>
                        <option value="north_america">🌎 North America (18 Nodes)</option>
                        <option value="south_america">🌎 South America (4 Nodes)</option>
                        <option value="asia">🌏 Asia (32 Nodes)</option>
                        <option value="americas">🌎 All Americas (22 Nodes)</option>
                        <option value="africa">🌍 Africa (8 Nodes)</option>
                        <option value="oceania">🇦🇺 Oceania (6 Nodes)</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Plain Text Subscription URL</label>
                    <div style="display: flex; gap: 8px;">
                        <input type="text" id="sub-url-input" readonly value="https://behrouz64.github.io/Surfshark-AmneziaWG-Mobile/sub.txt" style="flex: 1; background: var(--bg-main); border: 1px solid var(--border-color); color: var(--text-primary); padding: 10px; border-radius: var(--radius-md); font-family: monospace; font-size: 11px;">
                        <button id="btn-copy-sub-url" class="btn btn-primary" style="padding: 8px 14px;">Copy</button>
                    </div>
                </div>
                <div class="form-group" style="margin-top: 10px;">
                    <label>Base64 Subscription URL</label>
                    <div style="display: flex; gap: 8px;">
                        <input type="text" id="sub-b64-input" readonly value="https://behrouz64.github.io/Surfshark-AmneziaWG-Mobile/sub_base64.txt" style="flex: 1; background: var(--bg-main); border: 1px solid var(--border-color); color: var(--text-primary); padding: 10px; border-radius: var(--radius-md); font-family: monospace; font-size: 11px;">
                        <button id="btn-copy-b64-url" class="btn btn-secondary" style="padding: 8px 14px;">Copy</button>
                    </div>
                </div>
                <div class="sub-steps" style="margin-top: 14px; background: var(--bg-main); padding: 12px; border-radius: var(--radius-md); font-size: 12px; border: 1px solid var(--border-color);">
                    <h4 style="margin-bottom: 6px; color: var(--accent-cyan);">How to add in Shadowrocket:</h4>
                    <ol style="padding-left: 18px; line-height: 1.6; color: var(--text-secondary);">
                        <li>Select your preferred region (or Global) above.</li>
                        <li>Tap <strong>Copy</strong> on either URL above.</li>
                        <li>Open Shadowrocket on your iPhone and tap <strong>+</strong> (top-right).</li>
                        <li>Select Type: <strong>Subscribe</strong>.</li>
                        <li>Paste the URL and tap <strong>Save</strong>.</li>
                        <li>All nodes will download and auto-update!</li>
                    </ol>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal: Device & Multi-User Manager (Cloudflare KV) -->
    <div id="modal-devices" class="modal-overlay" style="display: none;">
        <div class="modal-sheet" style="max-height: 85vh; overflow-y: auto;">
            <div class="modal-header">
                <h2>📱 Cloud Device &amp; User Manager</h2>
                <button class="modal-close" data-close="modal-devices">✕</button>
            </div>
            <div class="modal-body">
                <!-- 1. First-Time Setup Card (if no admin registered yet) -->
                <div id="auth-setup-card" style="display: block; background: var(--bg-main); border: 1px solid var(--accent-cyan); border-radius: var(--radius-md); padding: 14px;">
                    <h3 style="color: var(--accent-cyan); font-size: 14px; margin-bottom: 6px;">👑 First-Time Setup (Create Admin)</h3>
                    <p style="font-size: 11px; color: var(--text-secondary); margin-bottom: 12px; line-height: 1.5;">
                        Create your Master Admin account to manage and synchronize subscriptions across all your devices securely on Cloudflare.
                    </p>
                    <form id="form-admin-setup" onsubmit="return false;" style="display: flex; flex-direction: column; gap: 8px;">
                        <div class="form-group">
                            <label>Admin Username</label>
                            <input type="text" id="setup-username" placeholder="e.g. admin" required style="width: 100%; background: var(--bg-card); border: 1px solid var(--border-color); color: var(--text-primary); padding: 8px; border-radius: var(--radius-md); font-size: 12px;">
                        </div>
                        <div class="form-group">
                            <label>Admin Password</label>
                            <input type="password" id="setup-password" placeholder="Choose a password" required style="width: 100%; background: var(--bg-card); border: 1px solid var(--border-color); color: var(--text-primary); padding: 8px; border-radius: var(--radius-md); font-size: 12px;">
                        </div>
                        <div class="form-group">
                            <label>Master Recovery Key (for password reset)</label>
                            <input type="text" id="setup-recovery-key" placeholder="A secret passphrase (e.g. my-secret-pin-99)" required style="width: 100%; background: var(--bg-card); border: 1px solid var(--border-color); color: var(--text-primary); padding: 8px; border-radius: var(--radius-md); font-size: 12px;">
                            <span style="font-size: 10px; color: var(--text-muted); margin-top: 2px;">⚠️ Save this key safely! If you ever forget your password, you can reset it with this key.</span>
                        </div>
                        <button type="button" id="btn-submit-setup" class="btn btn-primary" style="margin-top: 6px; padding: 10px;">
                            🚀 Initialize Cloud Account
                        </button>
                    </form>
                </div>

                <!-- 2. Login Card -->
                <div id="auth-login-card" style="display: none; background: var(--bg-main); border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 14px;">
                    <h3 style="color: var(--accent-cyan); font-size: 14px; margin-bottom: 6px;">🔑 Login to Cloud Manager</h3>
                    <p style="font-size: 11px; color: var(--text-secondary); margin-bottom: 12px;">
                        Login to view and manage your synchronized devices from any Mac or phone.
                    </p>
                    <form id="form-user-login" onsubmit="return false;" style="display: flex; flex-direction: column; gap: 8px;">
                        <div class="form-group">
                            <label>Username</label>
                            <input type="text" id="login-username" placeholder="Username" required style="width: 100%; background: var(--bg-card); border: 1px solid var(--border-color); color: var(--text-primary); padding: 8px; border-radius: var(--radius-md); font-size: 12px;">
                        </div>
                        <div class="form-group">
                            <label>Password</label>
                            <input type="password" id="login-password" placeholder="Password" required style="width: 100%; background: var(--bg-card); border: 1px solid var(--border-color); color: var(--text-primary); padding: 8px; border-radius: var(--radius-md); font-size: 12px;">
                        </div>
                        <button type="button" id="btn-submit-login" class="btn btn-primary" style="margin-top: 4px; padding: 10px;">
                            🔓 Login
                        </button>
                        <div style="text-align: center; margin-top: 6px;">
                            <a href="javascript:void(0)" id="link-show-reset" style="color: var(--text-muted); font-size: 11px; text-decoration: underline;">Forgot password? Reset with Recovery Key</a>
                        </div>
                    </form>
                </div>

                <!-- 3. Password Reset Card -->
                <div id="auth-reset-card" style="display: none; background: var(--bg-main); border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 14px;">
                    <h3 style="color: #f59e0b; font-size: 14px; margin-bottom: 6px;">🔄 Reset Password</h3>
                    <p style="font-size: 11px; color: var(--text-secondary); margin-bottom: 12px;">
                        Enter your username and your Master Recovery Key to reset your password.
                    </p>
                    <form id="form-user-reset" onsubmit="return false;" style="display: flex; flex-direction: column; gap: 8px;">
                        <div class="form-group">
                            <label>Username</label>
                            <input type="text" id="reset-username" placeholder="Username" required style="width: 100%; background: var(--bg-card); border: 1px solid var(--border-color); color: var(--text-primary); padding: 8px; border-radius: var(--radius-md); font-size: 12px;">
                        </div>
                        <div class="form-group">
                            <label>Master Recovery Key</label>
                            <input type="text" id="reset-recovery-key" placeholder="Enter recovery key..." required style="width: 100%; background: var(--bg-card); border: 1px solid var(--border-color); color: var(--text-primary); padding: 8px; border-radius: var(--radius-md); font-size: 12px;">
                        </div>
                        <div class="form-group">
                            <label>New Password</label>
                            <input type="password" id="reset-new-password" placeholder="Enter new password" required style="width: 100%; background: var(--bg-card); border: 1px solid var(--border-color); color: var(--text-primary); padding: 8px; border-radius: var(--radius-md); font-size: 12px;">
                        </div>
                        <div class="sub-actions-row" style="margin-top: 4px;">
                            <button type="button" id="btn-submit-reset" class="btn btn-primary" style="flex: 2; padding: 9px;">Reset Password</button>
                            <button type="button" id="btn-cancel-reset" class="btn btn-secondary" style="flex: 1; padding: 9px;">Cancel</button>
                        </div>
                    </form>
                </div>

                <!-- 4. Logged-In Active Session View -->
                <div id="auth-logged-in-view" style="display: none;">
                    <!-- User Status Bar -->
                    <div style="background: var(--bg-main); border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 10px 12px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center;">
                        <div style="display: flex; align-items: center; gap: 6px;">
                            <span style="font-size: 14px;">👤</span>
                            <span style="font-size: 12px; font-weight: 600; color: var(--text-primary);" id="session-user-name">User</span>
                            <span id="session-role-badge" style="font-size: 9px; padding: 2px 6px; border-radius: 4px; background: rgba(6, 182, 212, 0.2); color: var(--accent-cyan); text-transform: uppercase;">ADMIN</span>
                        </div>
                        <div style="display: flex; gap: 6px;">
                            <button type="button" id="btn-toggle-admin-users" class="btn btn-secondary" style="display: none; padding: 4px 8px; font-size: 10px;">👥 Users</button>
                            <button type="button" id="btn-user-logout" class="btn btn-secondary" style="padding: 4px 8px; font-size: 10px; color: #ef4444;">🚪 Logout</button>
                        </div>
                    </div>

                    <!-- Admin Users Management Panel (collapsible) -->
                    <div id="admin-users-panel" style="display: none; margin-bottom: 14px; background: var(--bg-main); border: 1px solid var(--accent-cyan); border-radius: var(--radius-md); padding: 12px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <h4 style="color: var(--accent-cyan); font-size: 12px; margin: 0;">👥 User Accounts Management</h4>
                            <button type="button" id="btn-close-users-panel" style="background: none; border: none; color: var(--text-muted); cursor: pointer; font-size: 12px;">✕</button>
                        </div>
                        <div id="admin-users-list" style="display: flex; flex-direction: column; gap: 6px; margin-bottom: 10px; max-height: 140px; overflow-y: auto;">
                            <!-- Injected dynamically -->
                        </div>
                        <div style="border-top: 1px solid var(--border-color); padding-top: 8px;">
                            <span style="font-size: 10px; font-weight: 600; color: var(--text-secondary); display: block; margin-bottom: 4px;">➕ Add New User Account</span>
                            <div style="display: flex; gap: 6px; margin-bottom: 6px;">
                                <input type="text" id="new-user-name" placeholder="Username" style="flex: 1; background: var(--bg-card); border: 1px solid var(--border-color); color: var(--text-primary); padding: 6px; border-radius: var(--radius-md); font-size: 11px;">
                                <input type="password" id="new-user-pass" placeholder="Password" style="flex: 1; background: var(--bg-card); border: 1px solid var(--border-color); color: var(--text-primary); padding: 6px; border-radius: var(--radius-md); font-size: 11px;">
                                <select id="new-user-role" style="background: var(--bg-card); border: 1px solid var(--border-color); color: var(--text-primary); padding: 6px; border-radius: var(--radius-md); font-size: 10px;">
                                    <option value="user">User</option>
                                    <option value="admin">Admin</option>
                                </select>
                            </div>
                            <button type="button" id="btn-create-sub-user" class="btn btn-primary" style="width: 100%; padding: 6px; font-size: 11px;">Create User Account</button>
                        </div>
                    </div>

                    <!-- Form to Add New Device -->
                    <form id="form-create-device" onsubmit="return false;" style="display: flex; flex-direction: column; gap: 10px;">
                        <div class="form-group">
                            <label for="dev-name-input">Device Name / Label</label>
                            <input type="text" id="dev-name-input" placeholder="e.g. iPhone-Dad or MacBook" required style="width: 100%; background: var(--bg-main); border: 1px solid var(--border-color); color: var(--text-primary); padding: 9px; border-radius: var(--radius-md); font-size: 12px;">
                        </div>

                        <div class="form-group">
                            <label for="dev-key-input">Surfshark WireGuard Private Key</label>
                            <div style="display: flex; gap: 6px;">
                                <input type="text" id="dev-key-input" placeholder="Paste Private Key from Surfshark account..." required style="flex: 1; background: var(--bg-main); border: 1px solid var(--border-color); color: var(--text-primary); padding: 9px; border-radius: var(--radius-md); font-family: monospace; font-size: 11px;">
                                <button type="button" id="btn-paste-dev-key" class="btn btn-secondary" style="padding: 6px 12px; font-size: 11px;" title="Paste from clipboard">📋 Paste</button>
                            </div>
                            <span style="font-size: 10px; color: var(--text-muted); margin-top: 4px; display: block; line-height: 1.4;">
                                💡 کلید اختصاصی را از پنل Surfshark (بخش Manual setup &gt; WireGuard) دریافت و اینجا وارد کنید.
                            </span>
                        </div>

                        <div class="sub-actions-row">
                            <div class="form-group" style="flex: 1;">
                                <label for="dev-obfs-select">Obfuscation</label>
                                <select id="dev-obfs-select" style="width: 100%; background: var(--bg-main); border: 1px solid var(--border-color); color: var(--text-primary); padding: 9px; border-radius: var(--radius-md); font-size: 12px; outline: none;">
                                    <option value="awg">🛡️ AmneziaWG (DPI Bypass)</option>
                                    <option value="none">🌐 Pure WireGuard (No Obfs)</option>
                                </select>
                            </div>
                            <div class="form-group" style="flex: 1;">
                                <label for="dev-duration-select">Duration / Expiry</label>
                                <select id="dev-duration-select" style="width: 100%; background: var(--bg-main); border: 1px solid var(--border-color); color: var(--text-primary); padding: 9px; border-radius: var(--radius-md); font-size: 12px; outline: none;">
                                    <option value="30">30 Days</option>
                                    <option value="7">7 Days (Trial)</option>
                                    <option value="60">60 Days (2 Months)</option>
                                    <option value="90">90 Days (3 Months)</option>
                                    <option value="180">180 Days (6 Months)</option>
                                    <option value="365">365 Days (1 Year)</option>
                                    <option value="0">Unlimited (No Expiry)</option>
                                </select>
                            </div>
                        </div>

                        <div class="form-group" style="margin-top: 4px;">
                            <label for="dev-region-select">Region / Continent</label>
                            <select id="dev-region-select" style="width: 100%; background: var(--bg-main); border: 1px solid var(--border-color); color: var(--text-primary); padding: 9px; border-radius: var(--radius-md); font-size: 12px; outline: none;">
                                <option value="all">🌐 All Continents</option>
                                <option value="europe">🇪🇺 Europe</option>
                                <option value="north_america">🌎 North America</option>
                                <option value="south_america">🌎 South America</option>
                                <option value="americas">🌎 All Americas</option>
                                <option value="asia">🌏 Asia</option>
                                <option value="africa">🌍 Africa</option>
                                <option value="oceania">🇦🇺 Oceania</option>
                            </select>
                        </div>

                        <button type="button" id="btn-create-dev-sub" class="btn btn-primary" style="margin-top: 4px; padding: 10px;">
                            ⚡ Save to Cloud &amp; Generate Link
                        </button>
                    </form>

                    <!-- Result Card (shown after generation) -->
                    <div id="dev-result-box" style="display: none; margin-top: 14px; background: var(--bg-main); border: 1px solid var(--accent-cyan); border-radius: var(--radius-md); padding: 12px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <h4 id="dev-res-title" style="color: var(--accent-cyan); margin: 0; font-size: 13px;">New Subscription Ready!</h4>
                            <span id="dev-res-badge" style="font-size: 10px; background: rgba(6, 182, 212, 0.2); color: var(--accent-cyan); padding: 2px 6px; border-radius: 4px;">Active</span>
                        </div>
                        
                        <div class="form-group" style="margin-bottom: 8px;">
                            <label style="font-size: 10px;">Direct Shadowrocket Subscription Link</label>
                            <div style="display: flex; gap: 6px;">
                                <input type="text" id="dev-res-url" readonly style="flex: 1; background: var(--bg-card); border: 1px solid var(--border-color); color: var(--text-primary); padding: 6px; border-radius: var(--radius-md); font-family: monospace; font-size: 10px;">
                                <button id="btn-copy-dev-url" class="btn btn-primary" style="padding: 4px 10px; font-size: 11px;">Copy</button>
                            </div>
                        </div>

                        <div style="display: flex; align-items: center; justify-content: center; gap: 12px; margin-top: 10px; background: var(--bg-card); padding: 10px; border-radius: var(--radius-md);">
                            <div id="dev-qr-container" style="background: white; padding: 6px; border-radius: 6px; width: 100px; height: 100px; display: flex; align-items: center; justify-content: center;"></div>
                            <div style="flex: 1; font-size: 11px; color: var(--text-secondary); line-height: 1.5;">
                                <strong>Scan with Shadowrocket:</strong>
                                <p style="margin: 4px 0 0 0;">Open Shadowrocket on your iPhone, tap <strong>[ - ]</strong> (Scan QR), and aim at this code.</p>
                            </div>
                        </div>
                    </div>

                    <!-- Cloud Synced Devices Section -->
                    <div style="margin-top: 16px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <h4 style="font-size: 12px; color: var(--text-secondary); margin: 0;">☁️ Cloud Synced Devices (<span id="saved-dev-count">0</span>)</h4>
                            <button type="button" id="btn-refresh-cloud-devs" style="background: none; border: none; color: var(--accent-cyan); font-size: 11px; cursor: pointer;">🔄 Refresh</button>
                        </div>
                        <div id="saved-devices-list" style="display: flex; flex-direction: column; gap: 8px;">
                            <div style="text-align: center; color: var(--text-muted); font-size: 11px; padding: 12px;">Loading cloud devices...</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal: Batch Export & Copy (Group) -->
    <div id="modal-batch" class="modal-overlay" style="display: none;">
        <div class="modal-sheet">
            <div class="modal-header">
                <h2>Group Export for Shadowrocket</h2>
                <button class="modal-close" data-close="modal-batch">✕</button>
            </div>
            <div class="modal-body">
                <p class="modal-desc">
                    Copy all links or the Base64 subscription below. In Shadowrocket, opening the app automatically detects multiple links in clipboard!
                </p>
                <div class="form-group">
                    <label>Node Links (<span id="batch-count">0</span> nodes)</label>
                    <textarea id="batch-textarea" readonly rows="8" style="width: 100%; background: var(--bg-main); border: 1px solid var(--border-color); color: var(--text-primary); font-family: monospace; font-size: 11px; padding: 10px; border-radius: var(--radius-md); outline: none;"></textarea>
                </div>
                <div class="sub-actions-row">
                    <button id="btn-copy-batch-raw" class="btn btn-primary" style="flex: 1;">📋 Copy Raw Links</button>
                    <button id="btn-copy-batch-b64" class="btn btn-secondary" style="flex: 1;">📦 Copy Base64 Sub</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal: QR Code Viewer -->
    <div id="modal-qr" class="modal-overlay" style="display: none;">
        <div class="modal-sheet">
            <div class="modal-header">
                <h2 id="qr-modal-title">Server QR Code</h2>
                <button class="modal-close" data-close="modal-qr">✕</button>
            </div>
            <div class="modal-body text-center">
                <p class="modal-desc" id="qr-modal-desc">Scan with Shadowrocket or camera</p>
                <div class="qr-image-wrapper">
                    <div id="qr-canvas-box" style="display: flex; justify-content: center;"></div>
                </div>
                <div class="qr-action-row">
                    <button id="btn-qr-copy" class="btn btn-secondary btn-block">📋 Copy Import Link</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Toast Notification -->
    <div id="toast" class="toast-popup" style="display: none;"></div>

    <script>
    // Embedded Seed Catalog of 76 Surfshark Clusters
    const DEFAULT_SERVERS = {servers_json_str};

    // Country code to Flag emoji helper
    function getFlagEmoji(countryCode) {{
        if (!countryCode || countryCode.length !== 2) return "🌐";
        try {{
            const codePoints = countryCode.toUpperCase().split("").map(c => 127397 + c.charCodeAt(0));
            return String.fromCodePoint(...codePoints);
        }} catch (e) {{
            return "🌐";
        }}
    }}

    // State
    const App = {{
        servers: [],
        filtered: [],
        selectedContinent: "All",
        searchTerm: "",
        resolvedOnly: false,
        sortBy: "latency",
        isResolving: false,
        activeQrUrl: "",
        settings: {{
            privkey: "{default_privkey}",
            address: "10.14.0.2/16",
            dns: "162.252.172.57, 149.154.159.92",
            doh_provider: "cloudflare",
            jc: 4,
            jmin: 50,
            jmax: 1000,
            s1: 0,
            s2: 0,
            h1: 1,
            h2: 2,
            h3: 3,
            h4: 4
        }}
    }};

    const OBFUSCATION_PRESETS = {{
        default: {{
            name: "Standard",
            jc: 4, jmin: 50, jmax: 1000, s1: 0, s2: 0, h1: 1, h2: 2, h3: 3, h4: 4
        }},
        none: {{
            name: "Pure WireGuard",
            jc: 0, jmin: 0, jmax: 0, s1: 0, s2: 0, h1: 1, h2: 2, h3: 3, h4: 4
        }},
        aggressive: {{
            name: "Aggressive",
            jc: 8, jmin: 80, jmax: 1280, s1: 15, s2: 15, h1: 1488, h2: 1489, h3: 1490, h4: 1491
        }},
        light: {{
            name: "Light",
            jc: 3, jmin: 40, jmax: 70, s1: 0, s2: 0, h1: 1, h2: 2, h3: 3, h4: 4
        }},
        extreme: {{
            name: "Extreme",
            jc: 6, jmin: 100, jmax: 1100, s1: 20, s2: 20, h1: 2, h2: 5, h3: 7, h4: 9
        }}
    }};

    function detectPreset(s) {{
        if (Number(s.jc) === 0 && Number(s.s1) === 0 && Number(s.s2) === 0 && Number(s.h1) === 1 && Number(s.h2) === 2 && Number(s.h3) === 3 && Number(s.h4) === 4) {{
            return "none";
        }}
        for (const [key, p] of Object.entries(OBFUSCATION_PRESETS)) {{
            if (
                Number(s.jc) === p.jc && Number(s.jmin) === p.jmin && Number(s.jmax) === p.jmax &&
                Number(s.s1) === p.s1 && Number(s.s2) === p.s2 &&
                Number(s.h1) === p.h1 && Number(s.h2) === p.h2 && Number(s.h3) === p.h3 && Number(s.h4) === p.h4
            ) {{
                return key;
            }}
        }}
        return "custom";
    }}

    function applyPresetValues(presetKey) {{
        const p = OBFUSCATION_PRESETS[presetKey];
        if (!p) return;
        document.getElementById("cfg-jc").value = p.jc;
        document.getElementById("cfg-jmin").value = p.jmin;
        document.getElementById("cfg-jmax").value = p.jmax;
        document.getElementById("cfg-s1").value = p.s1;
        document.getElementById("cfg-s2").value = p.s2;
        document.getElementById("cfg-h1").value = p.h1;
        document.getElementById("cfg-h2").value = p.h2;
        document.getElementById("cfg-h3").value = p.h3;
        document.getElementById("cfg-h4").value = p.h4;
    }}

    // Load Settings from LocalStorage
    function loadSavedSettings() {{
        try {{
            const saved = localStorage.getItem("surfshark_awg_settings");
            if (saved) {{
                const parsed = JSON.parse(saved);
                App.settings = Object.assign(App.settings, parsed);
            }}
        }} catch (e) {{
            console.warn("Could not load saved settings", e);
        }}

        // Update form values
        document.getElementById("cfg-privkey").value = App.settings.privkey;
        document.getElementById("cfg-address").value = App.settings.address;
        document.getElementById("cfg-dns").value = App.settings.dns;
        document.getElementById("cfg-doh").value = App.settings.doh_provider;
        document.getElementById("cfg-jc").value = App.settings.jc;
        document.getElementById("cfg-jmin").value = App.settings.jmin;
        document.getElementById("cfg-jmax").value = App.settings.jmax;
        document.getElementById("cfg-s1").value = App.settings.s1 || 0;
        document.getElementById("cfg-s2").value = App.settings.s2 || 0;
        document.getElementById("cfg-h1").value = App.settings.h1 || 1;
        document.getElementById("cfg-h2").value = App.settings.h2 || 2;
        document.getElementById("cfg-h3").value = App.settings.h3 || 3;
        document.getElementById("cfg-h4").value = App.settings.h4 || 4;

        const presetKey = detectPreset(App.settings);
        document.getElementById("cfg-obfs-preset").value = presetKey;
        document.getElementById("stat-provider").textContent = App.settings.doh_provider === "google" ? "Google" : "Cloudflare";
    }}

    function saveSettings() {{
        App.settings.privkey = document.getElementById("cfg-privkey").value.trim() || "{default_privkey}";
        App.settings.address = document.getElementById("cfg-address").value.trim() || "10.14.0.2/16";
        App.settings.dns = document.getElementById("cfg-dns").value.trim() || "162.252.172.57, 149.154.159.92";
        const parseNum = (id, fallback) => {{
            const v = parseInt(document.getElementById(id).value, 10);
            return isNaN(v) ? fallback : v;
        }};
        App.settings.jc = parseNum("cfg-jc", 4);
        App.settings.jmin = parseNum("cfg-jmin", 50);
        App.settings.jmax = parseNum("cfg-jmax", 1000);
        App.settings.s1 = parseNum("cfg-s1", 0);
        App.settings.s2 = parseNum("cfg-s2", 0);
        App.settings.h1 = parseNum("cfg-h1", 1);
        App.settings.h2 = parseNum("cfg-h2", 2);
        App.settings.h3 = parseNum("cfg-h3", 3);
        App.settings.h4 = parseNum("cfg-h4", 4);

        localStorage.setItem("surfshark_awg_settings", JSON.stringify(App.settings));
        document.getElementById("stat-provider").textContent = App.settings.doh_provider === "google" ? "Google" : "Cloudflare";
        showToast("Settings saved and applied!");
        applyFilters();
    }}

    // DoH (DNS-over-HTTPS) Resolver
    async function resolveSingleHostname(hostname, provider) {{
        const isGoogle = provider === "google";
        const url = isGoogle
            ? `https://dns.google/resolve?name=${{encodeURIComponent(hostname)}}&type=A`
            : `https://cloudflare-dns.com/dns-query?name=${{encodeURIComponent(hostname)}}&type=A`;

        const headers = isGoogle ? {{ "Accept": "application/json" }} : {{ "Accept": "application/dns-json" }};
        const t0 = performance.now();

        try {{
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 4000);
            const resp = await fetch(url, {{ headers, signal: controller.signal }});
            clearTimeout(timeoutId);

            if (!resp.ok) throw new Error(`HTTP ${{resp.status}}`);
            const data = await resp.json();
            const rtt = Math.round(performance.now() - t0);
            const answers = data.Answer || [];
            const ips = answers.filter(a => a.type === 1 && /^[0-9.]+$/.test(a.data)).map(a => a.data);
            return {{ ips, rtt }};
        }} catch (err) {{
            // Fallback to alternate DoH provider
            try {{
                const fallbackUrl = isGoogle
                    ? `https://cloudflare-dns.com/dns-query?name=${{encodeURIComponent(hostname)}}&type=A`
                    : `https://dns.google/resolve?name=${{encodeURIComponent(hostname)}}&type=A`;
                const fallbackHeaders = isGoogle ? {{ "Accept": "application/dns-json" }} : {{ "Accept": "application/json" }};
                const resp = await fetch(fallbackUrl, {{ headers: fallbackHeaders }});
                const data = await resp.json();
                const rtt = Math.round(performance.now() - t0);
                const answers = data.Answer || [];
                const ips = answers.filter(a => a.type === 1 && /^[0-9.]+$/.test(a.data)).map(a => a.data);
                return {{ ips, rtt }};
            }} catch (fallbackErr) {{
                return {{ ips: [], rtt: null }};
            }}
        }}
    }}

    // Batch DoH Resolver across clusters
    async function resolveAllServers() {{
        if (App.isResolving) return;
        App.isResolving = true;

        const btn = document.getElementById("btn-resolve-all");
        const progressBox = document.getElementById("progress-container");
        const progressBar = document.getElementById("progress-bar");
        const progressText = document.getElementById("progress-text");
        const progressPct = document.getElementById("progress-pct");

        btn.classList.add("scanning");
        btn.querySelector("span:last-child").textContent = "Resolving Subdomains...";
        progressBox.style.display = "block";

        const targets = App.servers;
        const total = targets.length;
        let completed = 0;
        let resolvedCount = 0;
        const CONCURRENCY = 6;

        for (let i = 0; i < total; i += CONCURRENCY) {{
            const chunk = targets.slice(i, i + CONCURRENCY);
            await Promise.all(chunk.map(async (srv) => {{
                const res = await resolveSingleHostname(srv.hostname, App.settings.doh_provider);
                if (res.ips && res.ips.length > 0) {{
                    srv.effective_ip = res.ips[0];
                    srv.resolved_ips = res.ips;
                    srv.ping_ms = res.rtt;
                    srv.is_doh_resolved = true;
                    resolvedCount++;
                }} else if (srv.resolved_ips && srv.resolved_ips.length > 0) {{
                    srv.effective_ip = srv.resolved_ips[0];
                }}
                completed++;
                const pct = Math.round((completed / total) * 100);
                progressBar.style.width = `${{pct}}%`;
                progressPct.textContent = `${{pct}}%`;
                progressText.textContent = `Resolved ${{completed}} of ${{total}} via ${{App.settings.doh_provider === "google" ? "Google" : "Cloudflare"}} DoH...`;
            }}));
            applyFilters();
        }}

        App.isResolving = false;
        btn.classList.remove("scanning");
        btn.querySelector("span:last-child").textContent = "Resolve All IPs (DoH nslookup)";
        progressBox.style.display = "none";
        document.getElementById("stat-resolved").textContent = resolvedCount;
        showToast(`DoH completed! ${{resolvedCount}} servers resolved to live IPs.`);
        applyFilters();
    }}

    // Config & Link Builders
    function buildRemark(srv, targetIp = null, index = 0, total = 1) {{
        const loc = srv.city || srv.country;
        const ip = targetIp || srv.effective_ip || srv.hostname;
        const suffix = total > 1 ? ` #${{index + 1}}` : "";
        const pingStr = srv.ping_ms ? ` — ${{srv.ping_ms}}ms` : "";
        return `🦈 ${{srv.flag}} ${{srv.country}} — ${{loc}}${{suffix}} (${{ip}})${{pingStr}}`;
    }}

    function buildWireguardUrl(srv, targetIp = null, index = 0, total = 1) {{
        const ip = targetIp || srv.effective_ip || (srv.resolved_ips && srv.resolved_ips[0]) || srv.hostname;
        const s = App.settings;
        const privkey = encodeURIComponent(s.privkey);
        const pubkey = encodeURIComponent(srv.public_key);
        const addr = (s.address || "10.14.0.2").split("/")[0].trim();
        const dnsEncoded = encodeURIComponent(s.dns || "162.252.172.57, 149.154.159.92");
        const remark = encodeURIComponent(buildRemark(srv, ip, index, total));
        const isObfs = !(Number(s.jc) === 0 && Number(s.s1) === 0 && Number(s.s2) === 0 && Number(s.h1) === 1 && Number(s.h2) === 2 && Number(s.h3) === 3 && Number(s.h4) === 4);

        const params = [
            `publicKey=${{pubkey}}`,
            `privateKey=${{privkey}}`,
            `ip=${{addr}}`,
            `dns=${{dnsEncoded}}`,
            `mtu=1280`,
            `udp=1`,
            `keepalive=25`
        ];

        if (isObfs) {{
            const obfsObj = {{
                s1: String(s.s1 !== undefined ? s.s1 : 0),
                h2: String(s.h2 !== undefined ? s.h2 : 2),
                jmax: String(s.jmax || 1000),
                s2: String(s.s2 !== undefined ? s.s2 : 0),
                h3: String(s.h3 !== undefined ? s.h3 : 3),
                jc: String(s.jc || 4),
                jmin: String(s.jmin || 50),
                h1: String(s.h1 || 1),
                h4: String(s.h4 !== undefined ? s.h4 : 4)
            }};
            const obfsParam = encodeURIComponent(JSON.stringify(obfsObj));
            params.push("obfs=amneziawg");
            params.push(`obfsParam=${{obfsParam}}`);
        }}

        return `wg://${{ip}}:${{srv.port || 51820}}?${{params.join("&")}}#${{remark}}`;
    }}

    function buildAmneziaConf(srv, targetIp = null, index = 0, total = 1) {{
        const ip = targetIp || srv.effective_ip || (srv.resolved_ips && srv.resolved_ips[0]) || srv.hostname;
        const s = App.settings;
        const suffix = total > 1 ? ` #${{index + 1}}` : "";
        const isObfs = !(Number(s.jc) === 0 && Number(s.s1) === 0 && Number(s.s2) === 0 && Number(s.h1) === 1 && Number(s.h2) === 2 && Number(s.h3) === 3 && Number(s.h4) === 4);
        const confLines = [
            `# Surfshark ${{isObfs ? "AmneziaWG" : "WireGuard"}} — ${{srv.country}} - ${{srv.city}}${{suffix}}`,
            `# Endpoint: ${{ip}}:${{srv.port || 51820}}`,
            "",
            "[Interface]",
            `PrivateKey = ${{s.privkey}}`,
            `Address = ${{s.address}}`,
            `DNS = ${{s.dns}}`
        ];

        if (isObfs) {{
            confLines.push(
                `Jc = ${{s.jc}}`,
                `Jmin = ${{s.jmin}}`,
                `Jmax = ${{s.jmax}}`,
                `S1 = ${{s.s1}}`,
                `S2 = ${{s.s2}}`,
                `H1 = ${{s.h1}}`,
                `H2 = ${{s.h2}}`,
                `H3 = ${{s.h3}}`,
                `H4 = ${{s.h4}}`
            );
        }}

        confLines.push(
            "",
            "[Peer]",
            `PublicKey = ${{srv.public_key}}`,
            "AllowedIPs = 0.0.0.0/0, ::/0",
            `Endpoint = ${{ip}}:${{srv.port || 51820}}`,
            "PersistentKeepalive = 25",
            ""
        );

        return confLines.join("\\n");
    }}

    // Filter & Render
    function applyFilters() {{
        let list = [...App.servers];

        if (App.selectedContinent !== "All") {{
            if (App.selectedContinent === "Americas") {{
                list = list.filter(s => s.continent === "Americas" || s.continent === "North America" || s.continent === "South America");
            }} else {{
                list = list.filter(s => s.continent === App.selectedContinent);
            }}
        }}

        if (App.searchTerm) {{
            const q = App.searchTerm.toLowerCase();
            list = list.filter(s =>
                s.country.toLowerCase().includes(q) ||
                s.city.toLowerCase().includes(q) ||
                s.hostname.toLowerCase().includes(q) ||
                (s.effective_ip && s.effective_ip.includes(q))
            );
        }}

        if (App.resolvedOnly) {{
            list = list.filter(s => s.is_doh_resolved);
        }}

        if (App.sortBy === "latency") {{
            list.sort((a, b) => {{
                const aPing = a.ping_ms || 9999;
                const bPing = b.ping_ms || 9999;
                return aPing - bPing || a.country.localeCompare(b.country);
            }});
        }} else {{
            list.sort((a, b) => a.country.localeCompare(b.country) || a.city.localeCompare(b.city));
        }}

        App.filtered = list;
        document.getElementById("displayed-count").textContent = list.length;
        renderCards(list);
    }}

    function renderCards(servers) {{
        const container = document.getElementById("server-list");
        if (!servers || servers.length === 0) {{
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">🔍</div>
                    <p>No servers match your filter.</p>
                </div>
            `;
            return;
        }}

        const html = servers.map(s => {{
            const ips = (s.resolved_ips && s.resolved_ips.length > 0) ? s.resolved_ips : [s.effective_ip || s.hostname];
            const primaryIp = ips[0];
            const wgUrl = buildWireguardUrl(s, primaryIp, 0, ips.length);
            const deeplink = `shadowrocket://add/${{wgUrl}}`;

            let badgeHtml = "";
            if (s.is_doh_resolved) {{
                badgeHtml = `<span class="badge badge-resolved">⚡ ${{s.ping_ms}}ms (${{ips.length}} IPs)</span>`;
            }} else {{
                badgeHtml = `<span class="badge badge-unresolved">Seed (${{ips.length}} IPs)</span>`;
            }}

            const ipPills = ips.map((item, idx) => `
                <button class="btn-card-action btn-copy-one" data-url="${{buildWireguardUrl(s, item, idx, ips.length)}}" style="font-size: 10px; padding: 2px 7px; margin-right: 4px; display: inline-flex;" title="Copy IP #${{idx + 1}}">
                    #${{idx + 1}}: ${{item}} 📋
                </button>
            `).join("");

            return `
                <div class="server-card ${{s.is_doh_resolved ? 'working' : ''}}">
                    <div class="server-card-top">
                        <div class="server-location">
                            <span class="server-flag">${{s.flag}}</span>
                            <div>
                                <div class="server-info-title">${{s.country}} · ${{s.city}}</div>
                                <div class="server-info-sub" style="margin-top: 5px; display: flex; flex-wrap: wrap; gap: 4px;">${{ipPills}}</div>
                            </div>
                        </div>
                        <div>${{badgeHtml}}</div>
                    </div>
                    <div class="server-card-actions">
                        <a href="${{deeplink}}" class="btn-sr-add" title="Add directly to iOS Shadowrocket">
                            <span>🚀</span> Shadowrocket
                        </a>
                        <button class="btn-card-action btn-copy-one" data-url="${{wgUrl}}">
                            <span>📋</span> Copy
                        </button>
                        <button class="btn-card-action btn-show-qr" data-url="${{wgUrl}}" data-title="${{s.country}} - ${{s.city}}">
                            <span>📱</span> QR
                        </button>
                        <button class="btn-card-action btn-download-conf" data-idx="${{s._idx}}">
                            <span>💾</span> .conf
                        </button>
                    </div>
                </div>
            `;
        }}).join("");

        container.innerHTML = html;

        // Bind Card Actions
        container.querySelectorAll(".btn-copy-one").forEach(b => {{
            b.addEventListener("click", () => copyToClipboard(b.dataset.url, "Node link copied for Shadowrocket!"));
        }});

        container.querySelectorAll(".btn-show-qr").forEach(b => {{
            b.addEventListener("click", () => openQrModal(b.dataset.url, b.dataset.title));
        }});

        container.querySelectorAll(".btn-download-conf").forEach(b => {{
            b.addEventListener("click", () => {{
                const s = App.servers[parseInt(b.dataset.idx)];
                downloadConfFile(s);
            }});
        }});
    }}

    // Export Utilities
    function downloadConfFile(s) {{
        const confStr = buildAmneziaConf(s);
        const blob = new Blob([confStr], {{ type: "text/plain;charset=utf-8" }});
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `Surfshark_${{s.country}}_${{s.city}}_${{s.effective_ip || 'conf'}}.conf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        showToast(`Downloaded ${{s.country}} .conf`);
    }}

    async function downloadAllZip() {{
        if (typeof JSZip === "undefined") {{
            showToast("ZIP library loading... try again in a moment.");
            return;
        }}
        showToast("Generating ZIP archive with all resolved IPs...");
        const zip = new JSZip();
        App.servers.forEach(s => {{
            const continent = s.continent || "Other";
            const ips = (s.resolved_ips && s.resolved_ips.length > 0) ? s.resolved_ips : [s.effective_ip || 'node'];
            ips.forEach((ip, idx) => {{
                const suffix = ips.length > 1 ? `_IP${{idx + 1}}` : "";
                const fname = `${{continent}}/Surfshark_${{s.country}}_${{s.city}}${{suffix}}_${{ip}}.conf`;
                zip.file(fname, buildAmneziaConf(s, ip, idx, ips.length));
            }});
        }});

        const content = await zip.generateAsync({{ type: "blob" }});
        const url = URL.createObjectURL(content);
        const a = document.createElement("a");
        a.href = url;
        a.download = "Surfshark_AmneziaWG_Mobile_All_Configs.zip";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        showToast("ZIP archive downloaded successfully!");
    }}

    function openBatchModal() {{
        const urls = [];
        App.filtered.forEach(s => {{
            const ips = (s.resolved_ips && s.resolved_ips.length > 0) ? s.resolved_ips : [s.effective_ip || s.hostname];
            ips.forEach((ip, idx) => {{
                urls.push(buildWireguardUrl(s, ip, idx, ips.length));
            }});
        }});
        document.getElementById("batch-count").textContent = urls.length;
        document.getElementById("batch-textarea").value = urls.join("\\n");
        openModal("modal-batch");
    }}

    function openQrModal(url, title) {{
        App.activeQrUrl = url;
        document.getElementById("qr-modal-title").textContent = title || "Server QR Code";
        const box = document.getElementById("qr-canvas-box");
        box.innerHTML = "";
        try {{
            new QRCode(box, {{
                text: url,
                width: 210,
                height: 210,
                colorDark: "#000000",
                colorLight: "#ffffff",
                correctLevel: QRCode.CorrectLevel.M
            }});
        }} catch (e) {{
            box.innerHTML = "<p>QR generator unavailable</p>";
        }}
        openModal("modal-qr");
    }}

    function openModal(id) {{
        const m = document.getElementById(id);
        if (m) {{
            m.style.display = "flex";
            document.body.style.overflow = "hidden";
        }}
    }}

    function closeModal(id) {{
        const m = document.getElementById(id);
        if (m) {{
            m.style.display = "none";
            document.body.style.overflow = "";
        }}
    }}

    function copyToClipboard(text, successMsg) {{
        if (navigator.clipboard && navigator.clipboard.writeText) {{
            navigator.clipboard.writeText(text).then(() => showToast(successMsg)).catch(() => fallbackCopy(text, successMsg));
        }} else {{
            fallbackCopy(text, successMsg);
        }}
    }}

    function fallbackCopy(text, successMsg) {{
        const ta = document.createElement("textarea");
        ta.value = text;
        ta.style.position = "fixed";
        ta.style.opacity = "0";
        document.body.appendChild(ta);
        ta.select();
        try {{
            document.execCommand("copy");
            showToast(successMsg);
        }} catch (e) {{
            showToast("Copied to clipboard!");
        }}
        document.body.removeChild(ta);
    }}

    function showToast(msg) {{
        const toast = document.getElementById("toast");
        toast.textContent = msg;
        toast.style.display = "block";
        if (toast._timer) clearTimeout(toast._timer);
        toast._timer = setTimeout(() => {{ toast.style.display = "none"; }}, 2500);
    }}

    // Init App
    document.addEventListener("DOMContentLoaded", () => {{
        loadSavedSettings();

        // Hydrate servers list
        App.servers = DEFAULT_SERVERS.map((s, idx) => ({{
            ...s,
            _idx: idx,
            flag: getFlagEmoji(s.country_code),
            effective_ip: (s.resolved_ips && s.resolved_ips[0]) || s.hostname,
            ping_ms: null,
            is_doh_resolved: false
        }}));

        document.getElementById("stat-total").textContent = App.servers.length;

        // Continent clicks
        document.getElementById("continent-chips").addEventListener("click", (e) => {{
            const chip = e.target.closest(".chip");
            if (!chip) return;
            document.querySelectorAll("#continent-chips .chip").forEach(c => c.classList.remove("active"));
            chip.classList.add("active");
            App.selectedContinent = chip.dataset.continent;
            applyFilters();
        }});

        // Search
        const searchInput = document.getElementById("search-input");
        const clearBtn = document.getElementById("btn-clear-search");
        searchInput.addEventListener("input", (e) => {{
            App.searchTerm = e.target.value.trim();
            clearBtn.style.display = App.searchTerm ? "block" : "none";
            applyFilters();
        }});
        clearBtn.addEventListener("click", () => {{
            searchInput.value = "";
            App.searchTerm = "";
            clearBtn.style.display = "none";
            applyFilters();
        }});

        // Toggles & Sort
        document.getElementById("toggle-resolved-only").addEventListener("change", (e) => {{
            App.resolvedOnly = e.target.checked;
            applyFilters();
        }});

        document.getElementById("sort-select").addEventListener("change", (e) => {{
            App.sortBy = e.target.value;
            applyFilters();
        }});

        // Primary Buttons
        document.getElementById("btn-resolve-all").addEventListener("click", resolveAllServers);
        document.getElementById("btn-download-zip").addEventListener("click", downloadAllZip);
        document.getElementById("btn-copy-all").addEventListener("click", openBatchModal);

        function updateSubUrls() {{
            const sel = document.getElementById("sub-scope-select");
            const scope = sel ? sel.value : "all";
            const baseUrl = (window.location.origin && window.location.origin !== "null" && window.location.protocol.startsWith("http") && !window.location.origin.includes("github.io"))
                ? window.location.origin
                : "https://behrouz64.github.io/Surfshark-AmneziaWG-Mobile";
            
            const fileSuffix = scope === "all" ? "" : "_" + scope;
            const txtUrl = baseUrl + "/sub" + fileSuffix + ".txt";
            const b64Url = baseUrl + "/sub" + (fileSuffix === "" ? "_base64" : fileSuffix + "_b64") + ".txt";
            
            document.getElementById("sub-url-input").value = txtUrl;
            document.getElementById("sub-b64-input").value = b64Url;
        }}

        document.getElementById("btn-open-sub").addEventListener("click", () => {{
            updateSubUrls();
            openModal("modal-sub");
        }});

        document.getElementById("sub-scope-select").addEventListener("change", updateSubUrls);

        // Subscription Modal Copy buttons
        document.getElementById("btn-copy-sub-url").addEventListener("click", () => {{
            const url = document.getElementById("sub-url-input").value;
            copyToClipboard(url, "Subscription URL copied! Paste into Shadowrocket.");
        }});

        document.getElementById("btn-copy-b64-url").addEventListener("click", () => {{
            const url = document.getElementById("sub-b64-input").value;
            copyToClipboard(url, "Base64 Subscription URL copied!");
        }});

        // Batch Modal Copy buttons
        document.getElementById("btn-copy-batch-raw").addEventListener("click", () => {{
            const text = document.getElementById("batch-textarea").value;
            copyToClipboard(text, "All links copied! Open Shadowrocket to import.");
        }});

        document.getElementById("btn-copy-batch-b64").addEventListener("click", () => {{
            const text = document.getElementById("batch-textarea").value;
            try {{
                const b64 = btoa(unescape(encodeURIComponent(text)));
                copyToClipboard(b64, "Base64 subscription payload copied!");
            }} catch (e) {{
                copyToClipboard(text, "Copied links!");
            }}
        }});

        // QR copy button
        document.getElementById("btn-qr-copy").addEventListener("click", () => {{
            if (App.activeQrUrl) copyToClipboard(App.activeQrUrl, "Link copied!");
        }});

        // Settings Modal
        document.getElementById("btn-open-settings").addEventListener("click", () => openModal("modal-settings"));
        document.getElementById("form-settings").addEventListener("submit", (e) => {{
            e.preventDefault();
            saveSettings();
            closeModal("modal-settings");
        }});
        // Preset change listener
        document.getElementById("cfg-obfs-preset").addEventListener("change", (e) => {{
            const val = e.target.value;
            if (val !== "custom") {{
                applyPresetValues(val);
                showToast("Preset " + val + " loaded");
            }}
        }});

        ["cfg-jc", "cfg-jmin", "cfg-jmax", "cfg-s1", "cfg-s2", "cfg-h1", "cfg-h2", "cfg-h3", "cfg-h4"].forEach(id => {{
            const el = document.getElementById(id);
            if (el) {{
                el.addEventListener("input", () => {{
                    const current = {{
                        jc: parseInt(document.getElementById("cfg-jc").value) || 0,
                        jmin: parseInt(document.getElementById("cfg-jmin").value) || 0,
                        jmax: parseInt(document.getElementById("cfg-jmax").value) || 0,
                        s1: parseInt(document.getElementById("cfg-s1").value) || 0,
                        s2: parseInt(document.getElementById("cfg-s2").value) || 0,
                        h1: parseInt(document.getElementById("cfg-h1").value) || 0,
                        h2: parseInt(document.getElementById("cfg-h2").value) || 0,
                        h3: parseInt(document.getElementById("cfg-h3").value) || 0,
                        h4: parseInt(document.getElementById("cfg-h4").value) || 0,
                    }};
                    document.getElementById("cfg-obfs-preset").value = detectPreset(current);
                }});
            }}
        }});

        document.getElementById("btn-reset-settings").addEventListener("click", () => {{
            localStorage.removeItem("surfshark_awg_settings");
            App.settings = Object.assign(App.settings, OBFUSCATION_PRESETS.default, {{
                privkey: "{default_privkey}",
                address: "10.14.0.2/16",
                dns: "162.252.172.57, 149.154.159.92",
                doh_provider: "cloudflare"
            }});
            loadSavedSettings();
            showToast("Settings reset to Default Preset");
            applyFilters();
        }});

        // Close modal handlers
        document.querySelectorAll(".modal-close").forEach(btn => {{
            btn.addEventListener("click", () => closeModal(btn.dataset.close));
        }});
        document.querySelectorAll(".modal-overlay").forEach(overlay => {{
            overlay.addEventListener("click", (e) => {{
                if (e.target === overlay) overlay.style.display = "none";
                document.body.style.overflow = "";
            }});
        }});

        // --- Multi-Device & Cloud Sync Manager Logic ---
        function escapeHtml(str) {{
            if (!str) return "";
            return String(str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
        }}

        const DEFAULT_CF_WORKER = "https://surfshark-amneziawg-sub.bsaidian.workers.dev";
        let cfWorkerUrl = localStorage.getItem("surfshark_cf_worker_url") || DEFAULT_CF_WORKER;

        let authSession = null;
        try {{
            const rawSession = localStorage.getItem("surfshark_auth_session");
            if (rawSession) authSession = JSON.parse(rawSession);
        }} catch (e) {{
            authSession = null;
        }}

        let managedDevices = [];
        try {{
            managedDevices = JSON.parse(localStorage.getItem("surfshark_managed_devices") || "[]");
        }} catch (e) {{
            managedDevices = [];
        }}

        function getEffectiveWorkerUrl() {{
            return cfWorkerUrl.trim().replace(/\/+$/, "") || DEFAULT_CF_WORKER;
        }}

        function updateMainPageAuthBadge() {{
            const statusLabel = document.getElementById("user-status-label");
            const badge = document.getElementById("user-badge");
            if (!statusLabel || !badge) return;

            if (authSession && authSession.username) {{
                statusLabel.textContent = "👤 Synced: " + authSession.username;
                badge.textContent = authSession.role === "admin" ? "Admin 👑" : "User 👤";
                badge.style.background = "rgba(16, 185, 129, 0.2)";
                badge.style.color = "#10b981";
            }} else {{
                statusLabel.textContent = "Cloudflare Cloud Sync (KV)";
                badge.textContent = "Open ↗";
                badge.style.background = "rgba(6, 182, 212, 0.2)";
                badge.style.color = "var(--accent-cyan)";
            }}
        }}

        function updateAuthUI() {{
            updateMainPageAuthBadge();

            const setupCard = document.getElementById("auth-setup-card");
            const loginCard = document.getElementById("auth-login-card");
            const resetCard = document.getElementById("auth-reset-card");
            const loggedInView = document.getElementById("auth-logged-in-view");

            if (!setupCard || !loginCard || !loggedInView) return;

            if (authSession && authSession.username) {{
                setupCard.style.display = "none";
                loginCard.style.display = "none";
                if (resetCard) resetCard.style.display = "none";
                loggedInView.style.display = "block";

                const nameEl = document.getElementById("session-user-name");
                const roleBadge = document.getElementById("session-role-badge");
                const btnUsers = document.getElementById("btn-toggle-admin-users");

                if (nameEl) nameEl.textContent = authSession.username;
                if (roleBadge) {{
                    roleBadge.textContent = (authSession.role || "user").toUpperCase();
                    roleBadge.style.background = authSession.role === "admin" ? "rgba(6, 182, 212, 0.2)" : "rgba(100, 116, 139, 0.2)";
                    roleBadge.style.color = authSession.role === "admin" ? "var(--accent-cyan)" : "var(--text-secondary)";
                }}
                if (btnUsers) {{
                    btnUsers.style.display = authSession.role === "admin" ? "inline-block" : "none";
                }}
            }} else {{
                loggedInView.style.display = "none";
            }}
        }}

        async function checkAuthStatus() {{
            const workerBase = getEffectiveWorkerUrl();
            const setupCard = document.getElementById("auth-setup-card");
            const loginCard = document.getElementById("auth-login-card");
            const resetCard = document.getElementById("auth-reset-card");
            const loggedInView = document.getElementById("auth-logged-in-view");

            if (authSession && authSession.token) {{
                try {{
                    const res = await fetch(workerBase + "/api/auth/me", {{
                        headers: {{ "Authorization": "Bearer " + authSession.token }}
                    }});
                    if (res.ok) {{
                        const d = await res.json();
                        if (d.authenticated && d.user) {{
                            authSession.role = d.user.role;
                            authSession.username = d.user.username;
                            localStorage.setItem("surfshark_auth_session", JSON.stringify(authSession));
                            updateAuthUI();
                            fetchCloudDevices();
                            return;
                        }}
                    }}
                }} catch (e) {{
                    console.warn("Could not verify session with worker:", e);
                    updateAuthUI();
                    renderManagedDevices();
                    return;
                }}
                authSession = null;
                localStorage.removeItem("surfshark_auth_session");
            }}

            // Check if admin is initialized
            try {{
                const statusRes = await fetch(workerBase + "/api/auth/status");
                if (statusRes.ok) {{
                    const sData = await statusRes.json();
                    if (!sData.hasAdmin) {{
                        if (setupCard) setupCard.style.display = "block";
                        if (loginCard) loginCard.style.display = "none";
                        if (resetCard) resetCard.style.display = "none";
                        if (loggedInView) loggedInView.style.display = "none";
                        const stLabel = document.getElementById("user-status-label");
                        const badge = document.getElementById("user-badge");
                        if (stLabel) stLabel.textContent = "Initial Admin Setup Required";
                        if (badge) {{
                            badge.textContent = "Setup 🚀";
                            badge.style.background = "rgba(245, 158, 11, 0.2)";
                            badge.style.color = "#f59e0b";
                        }}
                        return;
                    }}
                }}
            }} catch (e) {{
                console.warn("Error checking auth status:", e);
            }}

            if (setupCard) setupCard.style.display = "none";
            if (loginCard) loginCard.style.display = "block";
            if (resetCard) resetCard.style.display = "none";
            if (loggedInView) loggedInView.style.display = "none";
            updateAuthUI();
        }}

        async function fetchCloudDevices() {{
            if (!authSession || !authSession.token) {{
                renderManagedDevices();
                return;
            }}

            try {{
                const res = await fetch(getEffectiveWorkerUrl() + "/api/devices", {{
                    headers: {{ "Authorization": "Bearer " + authSession.token }}
                }});
                if (res.status === 401) {{
                    authSession = null;
                    localStorage.removeItem("surfshark_auth_session");
                    checkAuthStatus();
                    return;
                }}
                if (res.ok) {{
                    const data = await res.json();
                    managedDevices = data.devices || [];
                    localStorage.setItem("surfshark_managed_devices", JSON.stringify(managedDevices));
                    renderManagedDevices();
                }}
            }} catch (err) {{
                console.warn("Fetch cloud devices error:", err);
                renderManagedDevices();
            }}
        }}

        function renderManagedDevices() {{
            const container = document.getElementById("saved-devices-list");
            const countEl = document.getElementById("saved-dev-count");
            if (!container) return;

            if (countEl) countEl.textContent = managedDevices.length;
            if (managedDevices.length === 0) {{
                container.innerHTML = '<div style="text-align: center; color: var(--text-muted); font-size: 11px; padding: 12px; border: 1px dashed var(--border-color); border-radius: var(--radius-md);">No devices added yet. Create one above!</div>';
                return;
            }}

            const nowSec = Math.floor(Date.now() / 1000);
            let html = "";
            managedDevices.forEach((dev, idx) => {{
                let statusBadge = "";
                if (dev.expTimestamp === 0) {{
                    statusBadge = '<span style="font-size: 9px; padding: 2px 6px; border-radius: 4px; background: rgba(16, 185, 129, 0.15); color: #10b981;">♾️ Unlimited</span>';
                }} else if (nowSec > dev.expTimestamp) {{
                    const expDate = new Date(dev.expTimestamp * 1000).toISOString().split("T")[0];
                    statusBadge = '<span style="font-size: 9px; padding: 2px 6px; border-radius: 4px; background: rgba(239, 68, 68, 0.15); color: #ef4444;">❌ Expired (' + expDate + ')</span>';
                }} else {{
                    const daysLeft = Math.ceil((dev.expTimestamp - nowSec) / 86400);
                    const color = daysLeft <= 5 ? "#f59e0b" : "#10b981";
                    const bg = daysLeft <= 5 ? "rgba(245, 158, 11, 0.15)" : "rgba(16, 185, 129, 0.15)";
                    statusBadge = '<span style="font-size: 9px; padding: 2px 6px; border-radius: 4px; background: ' + bg + '; color: ' + color + ';">⏳ ' + daysLeft + ' days left</span>';
                }}

                html += '<div style="background: var(--bg-main); border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 10px; display: flex; flex-direction: column; gap: 6px;">' +
                    '<div style="display: flex; justify-content: space-between; align-items: center;">' +
                        '<div style="display: flex; align-items: center; gap: 6px;">' +
                            '<span style="font-size: 13px;">📱</span>' +
                            '<strong style="font-size: 12px; color: var(--text-primary);">' + escapeHtml(dev.name) + '</strong>' +
                            (dev.obfs === "none" ? '<span style="font-size: 9px; padding: 1px 5px; border-radius: 4px; background: rgba(234, 179, 8, 0.2); color: #eab308;">🌐 WireGuard</span>' : '<span style="font-size: 9px; padding: 1px 5px; border-radius: 4px; background: rgba(59, 130, 246, 0.2); color: #60a5fa;">🛡️ AWG</span>') +
                            '<span style="font-size: 10px; color: var(--text-secondary); text-transform: capitalize;">(' + (dev.region ? escapeHtml(dev.region.replace(/_/g, " ")) : "all") + ')</span>' +
                        '</div>' +
                        statusBadge +
                    '</div>' +
                    '<div style="display: flex; gap: 6px; margin-top: 4px;">' +
                        '<button type="button" class="btn btn-secondary btn-copy-dev-item" data-index="' + idx + '" style="flex: 1; padding: 4px 8px; font-size: 10px;">📋 Copy Link</button>' +
                        '<button type="button" class="btn btn-secondary btn-qr-dev-item" data-index="' + idx + '" style="padding: 4px 10px; font-size: 10px;">📱 QR</button>' +
                        '<button type="button" class="btn btn-secondary btn-del-dev-item" data-index="' + idx + '" style="padding: 4px 8px; font-size: 10px; color: #ef4444;" title="Delete Device">🗑️</button>' +
                    '</div>' +
                '</div>';
            }});
            container.innerHTML = html;

            container.querySelectorAll(".btn-copy-dev-item").forEach(btn => {{
                btn.addEventListener("click", () => {{
                    const i = parseInt(btn.getAttribute("data-index"), 10);
                    if (managedDevices[i]) {{
                        copyToClipboard(managedDevices[i].url, "Subscription URL for " + managedDevices[i].name + " copied!");
                    }}
                }});
            }});

            container.querySelectorAll(".btn-qr-dev-item").forEach(btn => {{
                btn.addEventListener("click", () => {{
                    const i = parseInt(btn.getAttribute("data-index"), 10);
                    if (managedDevices[i]) {{
                        showDevQr(managedDevices[i]);
                    }}
                }});
            }});

            container.querySelectorAll(".btn-del-dev-item").forEach(btn => {{
                btn.addEventListener("click", async () => {{
                    const i = parseInt(btn.getAttribute("data-index"), 10);
                    const dev = managedDevices[i];
                    if (!dev) return;
                    if (!confirm("Delete device " + dev.name + "?")) return;

                    if (authSession && authSession.token) {{
                        try {{
                            const res = await fetch(getEffectiveWorkerUrl() + "/api/devices?id=" + encodeURIComponent(dev.id), {{
                                method: "DELETE",
                                headers: {{ "Authorization": "Bearer " + authSession.token }}
                            }});
                            if (res.ok) {{
                                const d = await res.json();
                                managedDevices = d.devices || [];
                                localStorage.setItem("surfshark_managed_devices", JSON.stringify(managedDevices));
                                renderManagedDevices();
                                showToast("Device removed from cloud.");
                                return;
                            }}
                        }} catch (e) {{
                            console.warn("Delete cloud device error:", e);
                        }}
                    }}

                    managedDevices.splice(i, 1);
                    localStorage.setItem("surfshark_managed_devices", JSON.stringify(managedDevices));
                    renderManagedDevices();
                    showToast("Device removed.");
                }});
            }});
        }}

        async function fetchAdminUsers() {{
            const listEl = document.getElementById("admin-users-list");
            if (!listEl || !authSession || !authSession.token) return;

            listEl.innerHTML = '<div style="font-size: 11px; color: var(--text-muted); text-align: center; padding: 6px;">Loading accounts...</div>';

            try {{
                const res = await fetch(getEffectiveWorkerUrl() + "/api/users", {{
                    headers: {{ "Authorization": "Bearer " + authSession.token }}
                }});
                if (!res.ok) {{
                    listEl.innerHTML = '<div style="font-size: 11px; color: #ef4444;">Failed to load user accounts.</div>';
                    return;
                }}
                const data = await res.json();
                const users = data.users || [];
                if (users.length === 0) {{
                    listEl.innerHTML = '<div style="font-size: 11px; color: var(--text-muted);">No users found.</div>';
                    return;
                }}

                let html = "";
                users.forEach(u => {{
                    const isMe = (u.username === authSession.username);
                    const roleColor = u.role === "admin" ? "var(--accent-cyan)" : "var(--text-secondary)";
                    const roleBg = u.role === "admin" ? "rgba(6, 182, 212, 0.2)" : "rgba(100, 116, 139, 0.2)";

                    html += '<div style="display: flex; justify-content: space-between; align-items: center; background: var(--bg-card); padding: 6px 10px; border-radius: var(--radius-md); border: 1px solid var(--border-color);">' +
                        '<div style="display: flex; align-items: center; gap: 6px;">' +
                            '<span style="font-size: 11px; font-weight: 600; color: var(--text-primary);">' + escapeHtml(u.username) + (isMe ? ' <span style="font-size: 9px; color: var(--text-muted);">(You)</span>' : '') + '</span>' +
                            '<span style="font-size: 9px; padding: 1px 5px; border-radius: 4px; background: ' + roleBg + '; color: ' + roleColor + '; text-transform: uppercase;">' + escapeHtml(u.role) + '</span>' +
                        '</div>' +
                        (isMe ? '' : '<button type="button" class="btn btn-secondary btn-del-sub-user" data-user="' + escapeHtml(u.username) + '" style="padding: 2px 6px; font-size: 10px; color: #ef4444;" title="Delete User">🗑️</button>') +
                    '</div>';
                }});
                listEl.innerHTML = html;

                listEl.querySelectorAll(".btn-del-sub-user").forEach(btn => {{
                    btn.addEventListener("click", async () => {{
                        const targetU = btn.getAttribute("data-user");
                        if (!targetU) return;
                        if (!confirm("Are you sure you want to delete user " + targetU + " and all their devices?")) return;

                        try {{
                            const dRes = await fetch(getEffectiveWorkerUrl() + "/api/users?user=" + encodeURIComponent(targetU), {{
                                method: "DELETE",
                                headers: {{ "Authorization": "Bearer " + authSession.token }}
                            }});
                            const dData = await dRes.json();
                            if (!dRes.ok || !dData.success) {{
                                alert(dData.error || "Failed to delete user.");
                                return;
                            }}
                            showToast("User " + targetU + " deleted.");
                            fetchAdminUsers();
                        }} catch (err) {{
                            alert("Network error: " + err.message);
                        }}
                    }});
                }});

            }} catch (err) {{
                listEl.innerHTML = '<div style="font-size: 11px; color: #ef4444;">Error: ' + escapeHtml(err.message) + '</div>';
            }}
        }}

        function showDevQr(dev) {{
            const box = document.getElementById("qr-box");
            const label = document.getElementById("qr-modal-title");
            if (label) label.textContent = "Shadowrocket QR — " + dev.name;
            if (box) {{
                box.innerHTML = "";
                try {{
                    new QRCode(box, {{
                        text: dev.url,
                        width: 220,
                        height: 220,
                        colorDark: "#000000",
                        colorLight: "#ffffff",
                        correctLevel: QRCode.CorrectLevel.M
                    }});
                }} catch (e) {{
                    box.innerHTML = "<p>QR generator unavailable</p>";
                }}
                App.activeQrUrl = dev.url;
                openModal("modal-qr");
            }}
        }}

        // Paste Private Key
        const btnPasteDevKey = document.getElementById("btn-paste-dev-key");
        if (btnPasteDevKey) {{
            btnPasteDevKey.addEventListener("click", async () => {{
                try {{
                    if (navigator.clipboard && navigator.clipboard.readText) {{
                        const text = await navigator.clipboard.readText();
                        if (text && text.trim()) {{
                            document.getElementById("dev-key-input").value = text.trim();
                            showToast("Private key pasted from clipboard!");
                            return;
                        }}
                    }}
                }} catch (e) {{}}
                document.getElementById("dev-key-input").focus();
                showToast("Please paste your Surfshark private key");
            }});
        }}

        // First-Time Setup Admin
        const btnSubmitSetup = document.getElementById("btn-submit-setup");
        if (btnSubmitSetup) {{
            btnSubmitSetup.addEventListener("click", async () => {{
                const u = document.getElementById("setup-username").value.trim();
                const p = document.getElementById("setup-password").value;
                const rec = document.getElementById("setup-recovery-key").value.trim();

                if (!u || u.length < 3) {{
                    alert("Username must be at least 3 characters.");
                    return;
                }}
                if (!p || p.length < 4) {{
                    alert("Password must be at least 4 characters.");
                    return;
                }}
                if (!rec || rec.length < 6) {{
                    alert("Master Recovery Key must be at least 6 characters.");
                    return;
                }}

                btnSubmitSetup.disabled = true;
                btnSubmitSetup.textContent = "Initializing...";

                try {{
                    const res = await fetch(getEffectiveWorkerUrl() + "/api/auth/setup", {{
                        method: "POST",
                        headers: {{ "Content-Type": "application/json" }},
                        body: JSON.stringify({{ username: u, password: p, recoveryKey: rec }})
                    }});
                    const data = await res.json();
                    if (!res.ok || !data.success) {{
                        alert(data.error || "Setup failed.");
                        return;
                    }}

                    authSession = {{ token: data.token, username: data.username, role: data.role }};
                    localStorage.setItem("surfshark_auth_session", JSON.stringify(authSession));
                    alert("🎉 Master Admin created successfully!\\n\\n⚠️ IMPORTANT: Keep your Master Recovery Key safe. You can use it to reset your password if you ever forget it.");
                    updateAuthUI();
                    fetchCloudDevices();
                }} catch (err) {{
                    alert("Network error: " + err.message);
                }} finally {{
                    btnSubmitSetup.disabled = false;
                    btnSubmitSetup.textContent = "🚀 Initialize Cloud Account";
                }}
            }});
        }}

        // User Login
        const btnSubmitLogin = document.getElementById("btn-submit-login");
        if (btnSubmitLogin) {{
            btnSubmitLogin.addEventListener("click", async () => {{
                const u = document.getElementById("login-username").value.trim();
                const p = document.getElementById("login-password").value;

                if (!u || !p) {{
                    alert("Please enter username and password.");
                    return;
                }}

                btnSubmitLogin.disabled = true;
                btnSubmitLogin.textContent = "Logging in...";

                try {{
                    const res = await fetch(getEffectiveWorkerUrl() + "/api/auth/login", {{
                        method: "POST",
                        headers: {{ "Content-Type": "application/json" }},
                        body: JSON.stringify({{ username: u, password: p }})
                    }});
                    const data = await res.json();
                    if (!res.ok || !data.success) {{
                        alert(data.error || "Invalid username or password.");
                        return;
                    }}

                    authSession = {{ token: data.token, username: data.username, role: data.role }};
                    localStorage.setItem("surfshark_auth_session", JSON.stringify(authSession));
                    showToast("Logged in as " + data.username);
                    updateAuthUI();
                    fetchCloudDevices();
                }} catch (err) {{
                    alert("Network error: " + err.message);
                }} finally {{
                    btnSubmitLogin.disabled = false;
                    btnSubmitLogin.textContent = "🔓 Login";
                }}
            }});
        }}

        // Password Reset
        const linkShowReset = document.getElementById("link-show-reset");
        if (linkShowReset) {{
            linkShowReset.addEventListener("click", () => {{
                const loginCard = document.getElementById("auth-login-card");
                const resetCard = document.getElementById("auth-reset-card");
                if (loginCard) loginCard.style.display = "none";
                if (resetCard) resetCard.style.display = "block";
            }});
        }}

        const btnCancelReset = document.getElementById("btn-cancel-reset");
        if (btnCancelReset) {{
            btnCancelReset.addEventListener("click", () => {{
                const loginCard = document.getElementById("auth-login-card");
                const resetCard = document.getElementById("auth-reset-card");
                if (resetCard) resetCard.style.display = "none";
                if (loginCard) loginCard.style.display = "block";
            }});
        }}

        const btnSubmitReset = document.getElementById("btn-submit-reset");
        if (btnSubmitReset) {{
            btnSubmitReset.addEventListener("click", async () => {{
                const u = document.getElementById("reset-username").value.trim();
                const rec = document.getElementById("reset-recovery-key").value.trim();
                const newP = document.getElementById("reset-new-password").value;

                if (!u || !rec || !newP) {{
                    alert("Please fill in all fields.");
                    return;
                }}
                if (newP.length < 4) {{
                    alert("New password must be at least 4 characters.");
                    return;
                }}

                btnSubmitReset.disabled = true;
                btnSubmitReset.textContent = "Resetting...";

                try {{
                    const res = await fetch(getEffectiveWorkerUrl() + "/api/auth/reset", {{
                        method: "POST",
                        headers: {{ "Content-Type": "application/json" }},
                        body: JSON.stringify({{ username: u, recoveryKey: rec, newPassword: newP }})
                    }});
                    const data = await res.json();
                    if (!res.ok || !data.success) {{
                        alert(data.error || "Password reset failed. Check recovery key.");
                        return;
                    }}

                    alert("✅ Password reset successfully! You can now log in with your new password.");
                    const resetCard = document.getElementById("auth-reset-card");
                    const loginCard = document.getElementById("auth-login-card");
                    if (resetCard) resetCard.style.display = "none";
                    if (loginCard) {{
                        loginCard.style.display = "block";
                        const logU = document.getElementById("login-username");
                        if (logU) logU.value = u;
                        const logP = document.getElementById("login-password");
                        if (logP) {{ logP.value = ""; logP.focus(); }}
                    }}
                }} catch (err) {{
                    alert("Network error: " + err.message);
                }} finally {{
                    btnSubmitReset.disabled = false;
                    btnSubmitReset.textContent = "Reset Password";
                }}
            }});
        }}

        // Logout
        const btnLogout = document.getElementById("btn-user-logout");
        if (btnLogout) {{
            btnLogout.addEventListener("click", () => {{
                authSession = null;
                localStorage.removeItem("surfshark_auth_session");
                checkAuthStatus();
                showToast("Logged out successfully.");
            }});
        }}

        // Admin Users Panel Toggles
        const btnToggleUsers = document.getElementById("btn-toggle-admin-users");
        if (btnToggleUsers) {{
            btnToggleUsers.addEventListener("click", () => {{
                const p = document.getElementById("admin-users-panel");
                if (!p) return;
                const isHidden = (p.style.display === "none" || !p.style.display);
                p.style.display = isHidden ? "block" : "none";
                if (isHidden) fetchAdminUsers();
            }});
        }}

        const btnCloseUsers = document.getElementById("btn-close-users-panel");
        if (btnCloseUsers) {{
            btnCloseUsers.addEventListener("click", () => {{
                const p = document.getElementById("admin-users-panel");
                if (p) p.style.display = "none";
            }});
        }}

        const btnCreateSubUser = document.getElementById("btn-create-sub-user");
        if (btnCreateSubUser) {{
            btnCreateSubUser.addEventListener("click", async () => {{
                const u = document.getElementById("new-user-name").value.trim();
                const p = document.getElementById("new-user-pass").value;
                const r = document.getElementById("new-user-role").value;

                if (!u || u.length < 3) {{
                    alert("Username must be at least 3 characters.");
                    return;
                }}
                if (!p || p.length < 4) {{
                    alert("Password must be at least 4 characters.");
                    return;
                }}

                btnCreateSubUser.disabled = true;
                btnCreateSubUser.textContent = "Creating...";

                try {{
                    const res = await fetch(getEffectiveWorkerUrl() + "/api/users", {{
                        method: "POST",
                        headers: {{
                            "Content-Type": "application/json",
                            "Authorization": "Bearer " + authSession.token
                        }},
                        body: JSON.stringify({{ username: u, password: p, role: r }})
                    }});
                    const data = await res.json();
                    if (!res.ok || !data.success) {{
                        alert(data.error || "Failed to create user.");
                        return;
                    }}

                    document.getElementById("new-user-name").value = "";
                    document.getElementById("new-user-pass").value = "";
                    showToast("User " + u + " created successfully!");
                    fetchAdminUsers();
                }} catch (err) {{
                    alert("Network error: " + err.message);
                }} finally {{
                    btnCreateSubUser.disabled = false;
                    btnCreateSubUser.textContent = "Create User Account";
                }}
            }});
        }}

        // Refresh Cloud Devices
        const btnRefreshCloud = document.getElementById("btn-refresh-cloud-devs");
        if (btnRefreshCloud) {{
            btnRefreshCloud.addEventListener("click", () => {{
                fetchCloudDevices();
                showToast("Refreshing cloud devices...");
            }});
        }}

        // Save & Generate Device Subscription
        const btnCreateDevSub = document.getElementById("btn-create-dev-sub");
        if (btnCreateDevSub) {{
            btnCreateDevSub.addEventListener("click", async () => {{
                const name = document.getElementById("dev-name-input").value.trim();
                const key = document.getElementById("dev-key-input").value.trim();
                const obfsChoice = document.getElementById("dev-obfs-select") ? document.getElementById("dev-obfs-select").value : "awg";
                const durationDays = parseInt(document.getElementById("dev-duration-select").value, 10);
                const region = document.getElementById("dev-region-select").value;

                if (!name) {{
                    alert("Please enter a device name / label.");
                    return;
                }}
                if (!key) {{
                    alert("Please enter the WireGuard private key from your Surfshark account.");
                    return;
                }}

                const nowSec = Math.floor(Date.now() / 1000);
                const expSec = durationDays > 0 ? (nowSec + durationDays * 86400) : 0;
                const workerBase = getEffectiveWorkerUrl();

                let subUrl = workerBase + "/sub?key=" + encodeURIComponent(key) +
                               "&name=" + encodeURIComponent(name) +
                               "&exp=" + expSec +
                               "&continent=" + encodeURIComponent(region);
                if (obfsChoice === "none") {{
                    subUrl += "&obfs=0";
                }}

                const devObj = {{
                    id: "dev_" + Date.now(),
                    name: name,
                    key: key,
                    obfs: obfsChoice,
                    durationDays: durationDays,
                    expTimestamp: expSec,
                    region: region,
                    url: subUrl,
                    createdAt: nowSec
                }};

                if (authSession && authSession.token) {{
                    btnCreateDevSub.disabled = true;
                    btnCreateDevSub.textContent = "Saving to Cloud...";
                    try {{
                        const res = await fetch(workerBase + "/api/devices", {{
                            method: "POST",
                            headers: {{
                                "Content-Type": "application/json",
                                "Authorization": "Bearer " + authSession.token
                            }},
                            body: JSON.stringify(devObj)
                        }});
                        if (res.ok) {{
                            const d = await res.json();
                            managedDevices = d.devices || [devObj, ...managedDevices];
                            localStorage.setItem("surfshark_managed_devices", JSON.stringify(managedDevices));
                        }} else {{
                            managedDevices.unshift(devObj);
                            localStorage.setItem("surfshark_managed_devices", JSON.stringify(managedDevices));
                        }}
                    }} catch (err) {{
                        console.warn("Error posting device to cloud:", err);
                        managedDevices.unshift(devObj);
                        localStorage.setItem("surfshark_managed_devices", JSON.stringify(managedDevices));
                    }} finally {{
                        btnCreateDevSub.disabled = false;
                        btnCreateDevSub.textContent = "⚡ Save to Cloud & Generate Link";
                    }}
                }} else {{
                    managedDevices.unshift(devObj);
                    localStorage.setItem("surfshark_managed_devices", JSON.stringify(managedDevices));
                }}

                renderManagedDevices();

                const resBox = document.getElementById("dev-result-box");
                if (resBox) {{
                    resBox.style.display = "block";
                    document.getElementById("dev-res-title").textContent = "Subscription for " + name;
                    document.getElementById("dev-res-url").value = subUrl;
                    const daysText = durationDays > 0 ? (durationDays + " Days") : "Unlimited";
                    document.getElementById("dev-res-badge").textContent = daysText;

                    const qrBox = document.getElementById("dev-qr-container");
                    if (qrBox) {{
                        qrBox.innerHTML = "";
                        try {{
                            new QRCode(qrBox, {{
                                text: subUrl,
                                width: 90,
                                height: 90,
                                colorDark: "#000000",
                                colorLight: "#ffffff",
                                correctLevel: QRCode.CorrectLevel.M
                            }});
                        }} catch (e) {{
                            qrBox.innerHTML = "QR";
                        }}
                    }}
                }}

                showToast("Device subscription generated & synced!");
            }});
        }}

        // Copy Device URL
        const btnCopyDevUrl = document.getElementById("btn-copy-dev-url");
        if (btnCopyDevUrl) {{
            btnCopyDevUrl.addEventListener("click", () => {{
                const u = document.getElementById("dev-res-url").value;
                copyToClipboard(u, "Device subscription URL copied!");
            }});
        }}

        // Open Modal Handlers
        const btnDevModal = document.getElementById("btn-open-devices");
        if (btnDevModal) {{
            btnDevModal.addEventListener("click", () => {{
                checkAuthStatus();
                openModal("modal-devices");
            }});
        }}

        const btnBar = document.getElementById("btn-open-devices-bar");
        if (btnBar) {{
            btnBar.addEventListener("click", () => {{
                checkAuthStatus();
                openModal("modal-devices");
            }});
        }}

        // Initial Auth & Device Load
        checkAuthStatus();
        updateMainPageAuthBadge();
        renderManagedDevices();

        applyFilters();
    }});
    </script>
</body>
</html>
'''

# Write standalone files
with open(os.path.join(BASE_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(html_content)
print("Created root index.html (for GitHub Pages)")

with open(os.path.join(BASE_DIR, "templates", "index.html"), "w", encoding="utf-8") as f:
    f.write(html_content)
print("Updated templates/index.html")

with open(os.path.join(BASE_DIR, "surfshark_standalone.html"), "w", encoding="utf-8") as f:
    f.write(html_content)
print("Created surfshark_standalone.html (Single-file offline edition)")

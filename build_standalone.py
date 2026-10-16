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
    <meta name="theme-color" content="#0b0f17">
    <title>Surfshark AmneziaWG Mobile — Standalone DoH & Node Generator</title>
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
            <div class="logo-icon">🦈</div>
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
                <button class="chip active" data-continent="All">All</button>
                <button class="chip" data-continent="Europe">Europe</button>
                <button class="chip" data-continent="Americas">Americas</button>
                <button class="chip" data-continent="Asia">Asia</button>
                <button class="chip" data-continent="Africa">Africa</button>
                <button class="chip" data-continent="Oceania">Oceania</button>
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
                        <div class="modal-grid-2">
                            <div class="form-group">
                                <label for="cfg-jmax">Jmax (Max Junk Bytes)</label>
                                <input type="number" id="cfg-jmax" value="1000" min="50" max="1420">
                            </div>
                            <div class="form-group">
                                <label for="cfg-h1">H1 (Header Type 1)</label>
                                <input type="number" id="cfg-h1" value="1" min="1" max="255">
                            </div>
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
                        <option value="asia">🌏 Asia (32 Nodes)</option>
                        <option value="americas">🌎 Americas (22 Nodes)</option>
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
        document.getElementById("cfg-h1").value = App.settings.h1;
        document.getElementById("stat-provider").textContent = App.settings.doh_provider === "google" ? "Google" : "Cloudflare";
    }}

    function saveSettings() {{
        App.settings.privkey = document.getElementById("cfg-privkey").value.trim() || "{default_privkey}";
        App.settings.address = document.getElementById("cfg-address").value.trim() || "10.14.0.2/16";
        App.settings.dns = document.getElementById("cfg-dns").value.trim() || "162.252.172.57, 149.154.159.92";
        App.settings.doh_provider = document.getElementById("cfg-doh").value;
        App.settings.jc = parseInt(document.getElementById("cfg-jc").value) || 4;
        App.settings.jmin = parseInt(document.getElementById("cfg-jmin").value) || 50;
        App.settings.jmax = parseInt(document.getElementById("cfg-jmax").value) || 1000;
        App.settings.h1 = parseInt(document.getElementById("cfg-h1").value) || 1;

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

        const params = [
            `publicKey=${{pubkey}}`,
            `privateKey=${{privkey}}`,
            `ip=${{addr}}`,
            `dns=${{dnsEncoded}}`,
            `mtu=1280`,
            `udp=1`,
            `keepalive=25`,
            `obfs=amneziawg`,
            `obfsParam=${{obfsParam}}`
        ].join("&");

        return `wg://${{ip}}:${{srv.port || 51820}}?${{params}}#${{remark}}`;
    }}

    function buildAmneziaConf(srv, targetIp = null, index = 0, total = 1) {{
        const ip = targetIp || srv.effective_ip || (srv.resolved_ips && srv.resolved_ips[0]) || srv.hostname;
        const s = App.settings;
        const suffix = total > 1 ? ` #${{index + 1}}` : "";
        return [
            `# Surfshark AmneziaWG — ${{srv.country}} - ${{srv.city}}${{suffix}}`,
            `# Endpoint: ${{ip}}:${{srv.port || 51820}}`,
            "",
            "[Interface]",
            `PrivateKey = ${{s.privkey}}`,
            `Address = ${{s.address}}`,
            `DNS = ${{s.dns}}`,
            `Jc = ${{s.jc}}`,
            `Jmin = ${{s.jmin}}`,
            `Jmax = ${{s.jmax}}`,
            `S1 = ${{s.s1}}`,
            `S2 = ${{s.s2}}`,
            `H1 = ${{s.h1}}`,
            `H2 = ${{s.h2}}`,
            `H3 = ${{s.h3}}`,
            `H4 = ${{s.h4}}`,
            "",
            "[Peer]",
            `PublicKey = ${{srv.public_key}}`,
            "AllowedIPs = 0.0.0.0/0, ::/0",
            `Endpoint = ${{ip}}:${{srv.port || 51820}}`,
            "PersistentKeepalive = 25",
            ""
        ].join("\\n");
    }}

    // Filter & Render
    function applyFilters() {{
        let list = [...App.servers];

        if (App.selectedContinent !== "All") {{
            list = list.filter(s => s.continent === App.selectedContinent);
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
        document.getElementById("btn-reset-settings").addEventListener("click", () => {{
            localStorage.removeItem("surfshark_awg_settings");
            loadSavedSettings();
            showToast("Settings reset to defaults");
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

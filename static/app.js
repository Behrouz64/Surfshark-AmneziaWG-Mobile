/**
 * Surfshark AmneziaWG Mobile Scanner — Frontend Application Logic
 */

(function () {
    'use strict';

    // State
    const state = {
        servers: [],
        filteredServers: [],
        selectedContinent: 'All',
        searchTerm: '',
        workingOnly: false,
        sortBy: 'latency',
        isScanning: false,
        pollTimer: null,
        activeQrUrl: '',
    };

    // DOM Elements
    const elements = {
        statTotal: document.getElementById('stat-total'),
        statWorking: document.getElementById('stat-working'),
        statStatus: document.getElementById('stat-status'),
        vpnWarning: document.getElementById('vpn-warning'),
        credBanner: document.getElementById('credentials-banner'),
        progressContainer: document.getElementById('progress-container'),
        progressBar: document.getElementById('progress-bar'),
        progressText: document.getElementById('progress-status-text'),
        progressPercentage: document.getElementById('progress-percentage'),
        btnScan: document.getElementById('btn-scan'),
        btnScanLabel: document.getElementById('btn-scan-label'),
        btnSubInfo: document.getElementById('btn-sub-info'),
        btnExportZip: document.getElementById('btn-export-zip'),
        continentChips: document.getElementById('continent-chips'),
        searchInput: document.getElementById('search-input'),
        btnClearSearch: document.getElementById('btn-clear-search'),
        toggleWorkingOnly: document.getElementById('toggle-working-only'),
        sortSelect: document.getElementById('sort-select'),
        displayedCount: document.getElementById('displayed-count'),
        serverList: document.getElementById('server-list'),
        // Modals
        modalSettings: document.getElementById('modal-settings'),
        btnOpenSettings: document.getElementById('btn-open-settings'),
        btnBannerSetup: document.getElementById('btn-banner-setup'),
        formSettings: document.getElementById('form-settings'),
        inputPrivKey: document.getElementById('input-privkey'),
        inputAddress: document.getElementById('input-address'),
        inputDns: document.getElementById('input-dns'),
        modalQr: document.getElementById('modal-qr'),
        qrModalTitle: document.getElementById('qr-modal-title'),
        qrImg: document.getElementById('qr-img'),
        btnQrCopy: document.getElementById('btn-qr-copy'),
        modalSub: document.getElementById('modal-sub'),
        subUrlInput: document.getElementById('sub-url-input'),
        btnCopySubUrl: document.getElementById('btn-copy-sub-url'),
        toast: document.getElementById('toast'),
    };

    // Initialize
    document.addEventListener('DOMContentLoaded', init);

    function init() {
        bindEvents();
        fetchStatus();
        fetchServers();
    }

    function bindEvents() {
        // Continent chip clicks
        elements.continentChips.addEventListener('click', (e) => {
            const chip = e.target.closest('.chip');
            if (!chip) return;
            elements.continentChips.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
            chip.classList.add('active');
            state.selectedContinent = chip.dataset.continent;
            applyFilters();
        });

        // Search input
        elements.searchInput.addEventListener('input', (e) => {
            state.searchTerm = e.target.value.trim().toLowerCase();
            elements.btnClearSearch.style.display = state.searchTerm ? 'block' : 'none';
            applyFilters();
        });

        elements.btnClearSearch.addEventListener('click', () => {
            elements.searchInput.value = '';
            state.searchTerm = '';
            elements.btnClearSearch.style.display = 'none';
            applyFilters();
        });

        // Working only toggle
        elements.toggleWorkingOnly.addEventListener('change', (e) => {
            state.workingOnly = e.target.checked;
            applyFilters();
        });

        // Sort change
        elements.sortSelect.addEventListener('change', (e) => {
            state.sortBy = e.target.value;
            applyFilters();
        });

        // Scan button
        elements.btnScan.addEventListener('click', handleStartScan);

        // Export ZIP
        elements.btnExportZip.addEventListener('click', () => {
            window.location.href = '/export/zip';
            showToast('Downloading all server configs ZIP...');
        });

        // Subscription Modal
        elements.btnSubInfo.addEventListener('click', () => {
            const subUrl = `${window.location.origin}/sub`;
            elements.subUrlInput.value = subUrl;
            openModal(elements.modalSub);
        });

        elements.btnCopySubUrl.addEventListener('click', () => {
            copyToClipboard(elements.subUrlInput.value, 'Subscription URL copied to clipboard!');
        });

        // Settings Modal
        elements.btnOpenSettings.addEventListener('click', () => openModal(elements.modalSettings));
        if (elements.btnBannerSetup) {
            elements.btnBannerSetup.addEventListener('click', () => openModal(elements.modalSettings));
        }

        elements.formSettings.addEventListener('submit', handleSaveSettings);

        // QR copy button
        elements.btnQrCopy.addEventListener('click', () => {
            if (state.activeQrUrl) {
                copyToClipboard(state.activeQrUrl, 'Node URL copied to clipboard!');
            }
        });

        // Modal close buttons (data-close)
        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', () => {
                const modalId = btn.dataset.close;
                const modal = document.getElementById(modalId);
                if (modal) closeModal(modal);
            });
        });

        // Close on background overlay click
        document.querySelectorAll('.modal-overlay').forEach(overlay => {
            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) {
                    closeModal(overlay);
                }
            });
        });
    }

    // API Calls
    async function fetchStatus() {
        try {
            const res = await fetch('/api/status');
            const data = await res.json();

            // VPN Warning
            elements.vpnWarning.style.display = data.vpn_active ? 'flex' : 'none';

            // Credentials banner
            if (data.credentials && !data.credentials.has_key) {
                elements.credBanner.style.display = 'flex';
            } else {
                elements.credBanner.style.display = 'none';
            }

            if (data.credentials) {
                if (data.credentials.private_key) {
                    elements.inputPrivKey.value = data.credentials.private_key;
                }
                elements.inputAddress.value = data.credentials.address || '10.14.0.2/16';
                elements.inputDns.value = data.credentials.dns || '162.252.172.57, 149.154.159.92';
            }

            // Stats
            elements.statTotal.textContent = data.total_servers || 0;
            if (data.progress) {
                elements.statWorking.textContent = data.progress.working || 0;
                elements.statStatus.textContent = data.progress.status || 'Ready';
            }

            // Handle scanning state
            if (data.is_scanning) {
                setScanningUI(true, data.progress);
                if (!state.pollTimer) {
                    state.pollTimer = setInterval(pollScanStatus, 1000);
                }
            } else {
                if (state.isScanning) {
                    // Just finished scanning
                    setScanningUI(false);
                    fetchServers();
                }
            }
        } catch (err) {
            console.error('Failed to fetch status:', err);
        }
    }

    async function fetchServers() {
        try {
            const res = await fetch('/api/servers?continent=All');
            const data = await res.json();
            state.servers = data.servers || [];
            applyFilters();
        } catch (err) {
            console.error('Failed to fetch servers:', err);
            elements.serverList.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">❌</div>
                    <p>Failed to load servers. Please refresh.</p>
                </div>
            `;
        }
    }

    async function handleStartScan() {
        if (state.isScanning) return;

        try {
            setScanningUI(true, { total: state.servers.length, completed: 0, status: 'Starting scan...' });
            await fetch('/api/scan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ continent: state.selectedContinent }),
            });
            showToast('Scan initiated...');
            if (state.pollTimer) clearInterval(state.pollTimer);
            state.pollTimer = setInterval(pollScanStatus, 1000);
        } catch (err) {
            console.error('Failed to start scan:', err);
            setScanningUI(false);
            showToast('Failed to start scan');
        }
    }

    async function pollScanStatus() {
        try {
            const res = await fetch('/api/status');
            const data = await res.json();

            if (data.progress) {
                updateProgressUI(data.progress);
                elements.statWorking.textContent = data.progress.working || 0;
                elements.statStatus.textContent = data.progress.status || 'Scanning...';
            }

            if (!data.is_scanning) {
                clearInterval(state.pollTimer);
                state.pollTimer = null;
                setScanningUI(false);
                showToast(`Scan complete! ${data.progress ? data.progress.working : 0} online.`);
                fetchServers();
            }
        } catch (err) {
            console.error('Error polling status:', err);
        }
    }

    async function handleSaveSettings(e) {
        e.preventDefault();
        const privkey = elements.inputPrivKey.value.trim();
        const address = elements.inputAddress.value.trim();
        const dns = elements.inputDns.value.trim();

        try {
            const res = await fetch('/api/settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ private_key: privkey, address, dns }),
            });
            const data = await res.json();
            if (res.ok) {
                showToast('Credentials saved successfully!');
                closeModal(elements.modalSettings);
                fetchStatus();
                fetchServers();
            } else {
                showToast(data.error || 'Failed to save credentials');
            }
        } catch (err) {
            console.error('Error saving settings:', err);
            showToast('Network error saving settings');
        }
    }

    // UI Updates & Filtering
    function applyFilters() {
        let result = [...state.servers];

        // Continent filter
        if (state.selectedContinent !== 'All') {
            result = result.filter(s => s.continent === state.selectedContinent);
        }

        // Search filter
        if (state.searchTerm) {
            const q = state.searchTerm;
            result = result.filter(s =>
                (s.country && s.country.toLowerCase().includes(q)) ||
                (s.city && s.city.toLowerCase().includes(q)) ||
                (s.hostname && s.hostname.toLowerCase().includes(q)) ||
                (s.effective_ip && s.effective_ip.includes(q))
            );
        }

        // Working only filter
        if (state.workingOnly) {
            result = result.filter(s => s.best_ping !== null && s.best_ping !== undefined);
        }

        // Sort
        if (state.sortBy === 'latency') {
            result.sort((a, b) => {
                const aWorking = a.best_ping !== null && a.best_ping !== undefined;
                const bWorking = b.best_ping !== null && b.best_ping !== undefined;
                if (aWorking && !bWorking) return -1;
                if (!aWorking && bWorking) return 1;
                if (aWorking && bWorking) return a.best_ping - b.best_ping;
                return a.country.localeCompare(b.country);
            });
        } else if (state.sortBy === 'country') {
            result.sort((a, b) => a.country.localeCompare(b.country) || a.city.localeCompare(b.city));
        }

        state.filteredServers = result;
        elements.displayedCount.textContent = result.length;
        renderServerCards(result);
    }

    function renderServerCards(servers) {
        if (!servers || servers.length === 0) {
            elements.serverList.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">🔍</div>
                    <p>No servers match your filter criteria.</p>
                </div>
            `;
            return;
        }

        const html = servers.map(s => {
            const isOnline = s.best_ping !== null && s.best_ping !== undefined;
            let latencyBadge = '';
            if (isOnline) {
                const ping = Math.round(s.best_ping);
                const badgeColor = ping < 150 ? 'badge-green' : ping < 300 ? 'badge-yellow' : 'badge-gray';
                latencyBadge = `<span class="badge ${badgeColor}">⚡ ${ping} ms</span>`;
            } else if (s.status === 'Checked') {
                latencyBadge = `<span class="badge badge-gray">Timeout</span>`;
            } else {
                latencyBadge = `<span class="badge badge-gray">Untested</span>`;
            }

            const ipText = s.effective_ip ? `${s.effective_ip}:${s.port || 51820}` : s.hostname;
            const deeplink = s.shadowrocket_deeplink || '#';
            const rawWireguard = s.shadowrocket_url || '';

            return `
                <div class="server-card ${isOnline ? 'working' : ''}" data-hostname="${escapeHtml(s.hostname)}">
                    <div class="server-card-top">
                        <div class="server-location">
                            <span class="server-flag">${s.flag || '🌐'}</span>
                            <div>
                                <div class="server-info-title">${escapeHtml(s.country)} · ${escapeHtml(s.city)}</div>
                                <div class="server-info-sub">${escapeHtml(ipText)}</div>
                            </div>
                        </div>
                        <div>
                            ${latencyBadge}
                        </div>
                    </div>
                    <div class="server-card-actions">
                        <a href="${escapeHtml(deeplink)}" class="btn-sr-add" title="Open and add directly into Shadowrocket iOS">
                            <span>🚀</span> Shadowrocket
                        </a>
                        <button class="btn-card-action btn-show-qr" data-url="${escapeHtml(rawWireguard)}" data-title="${escapeHtml(s.country)} - ${escapeHtml(s.city)}">
                            <span>📱</span> QR
                        </button>
                        <button class="btn-card-action btn-copy-conf" data-url="${escapeHtml(rawWireguard)}">
                            <span>📋</span> Copy
                        </button>
                        <a href="/export/conf?hostname=${encodeURIComponent(s.hostname)}" class="btn-card-action" download title="Download .conf file">
                            <span>💾</span> .conf
                        </a>
                    </div>
                </div>
            `;
        }).join('');

        elements.serverList.innerHTML = html;

        // Bind card actions
        elements.serverList.querySelectorAll('.btn-show-qr').forEach(btn => {
            btn.addEventListener('click', () => {
                const url = btn.dataset.url;
                const title = btn.dataset.title;
                openQrModal(url, title);
            });
        });

        elements.serverList.querySelectorAll('.btn-copy-conf').forEach(btn => {
            btn.addEventListener('click', () => {
                const url = btn.dataset.url;
                copyToClipboard(url, 'Shadowrocket / WireGuard URL copied!');
            });
        });
    }

    function setScanningUI(scanning, progress) {
        state.isScanning = scanning;
        if (scanning) {
            elements.btnScan.classList.add('scanning');
            elements.btnScanLabel.textContent = 'Scanning...';
            elements.progressContainer.style.display = 'block';
            if (progress) updateProgressUI(progress);
        } else {
            elements.btnScan.classList.remove('scanning');
            elements.btnScanLabel.textContent = 'Start Scan';
            elements.progressContainer.style.display = 'none';
        }
    }

    function updateProgressUI(progress) {
        const total = progress.total || 1;
        const completed = progress.completed || 0;
        const pct = Math.min(100, Math.round((completed / total) * 100));
        elements.progressBar.style.width = `${pct}%`;
        elements.progressPercentage.textContent = `${pct}%`;
        elements.progressText.textContent = progress.status || `Tested ${completed} of ${total}`;
    }

    function openQrModal(url, title) {
        if (!url) {
            showToast('No valid URL for this server yet. Set your private key first.');
            return;
        }
        state.activeQrUrl = url;
        elements.qrModalTitle.textContent = title || 'Server QR Code';
        elements.qrImg.src = `/api/qr?text=${encodeURIComponent(url)}`;
        openModal(elements.modalQr);
    }

    function openModal(modal) {
        if (modal) {
            modal.style.display = 'flex';
            document.body.style.overflow = 'hidden';
        }
    }

    function closeModal(modal) {
        if (modal) {
            modal.style.display = 'none';
            document.body.style.overflow = '';
        }
    }

    function copyToClipboard(text, successMsg) {
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(text).then(() => {
                showToast(successMsg);
            }).catch(() => {
                fallbackCopy(text, successMsg);
            });
        } else {
            fallbackCopy(text, successMsg);
        }
    }

    function fallbackCopy(text, successMsg) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.opacity = '0';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        try {
            document.execCommand('copy');
            showToast(successMsg);
        } catch (err) {
            showToast('Failed to copy');
        }
        document.body.removeChild(textArea);
    }

    function showToast(message, duration = 2500) {
        const toast = elements.toast;
        toast.textContent = message;
        toast.style.display = 'block';
        if (toast._timer) clearTimeout(toast._timer);
        toast._timer = setTimeout(() => {
            toast.style.display = 'none';
        }, duration);
    }

    function escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }
})();

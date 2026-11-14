/**
 * Cloudflare Worker for Surfshark AmneziaWG & Hybrid Clinic
 * - Multi-User Management with Cloudflare KV
 * - Role-Based Access (Admin & Standard Users)
 * - Cloud Device Synchronization across Mobile & Desktop
 * - Password Reset with Master Recovery Key
 * - Dynamic Private Key & Expiry Subscriptions for Shadowrocket, V2rayNG, Sing-Box, Clash Meta
 * - Security Geoblocking: Instant 403 for China (CN) and Russia (RU)
 * - 5 Upgraded Features:
 *   1. Hybrid Clinic Switcher (family, 2hop, 3hop, pro, raw)
 *   2. Multi-Format Converter (WireGuard .conf, Clash Meta YAML, Sing-box JSON, Base64)
 *   3. Edge Health Check & Latency Monitor (/api/health)
 *   4. Standard ISP Subscription-Userinfo Headers & Quota Tracking
 *   5. Carrier-Aware Clean IP Optimization (MCI, MTN, Rightel, Wi-Fi)
 */

const GITHUB_PAGES_BASE = "https://behrouz64.github.io/Surfshark-AmneziaWG-Mobile";
const CLINIC_API_BASE = "https://karajlasik.ir";
const JWT_SECRET = "surfshark_awg_secret_salt_2026";

// Clean IPs for major Iranian ISPs
const CARRIER_CLEAN_IPS = {
  mci: ["188.114.97.2", "188.114.96.2", "104.24.12.18", "104.26.15.5"],
  mtn: ["104.21.49.19", "172.67.182.202", "104.28.16.8", "162.159.138.8"],
  rightel: ["141.101.90.10", "108.162.193.10", "190.93.247.10"],
  wifi: ["104.16.132.229", "104.17.148.22", "162.159.36.1"]
};

async function hashPassword(password) {
  const enc = new TextEncoder().encode(password + JWT_SECRET);
  const buf = await crypto.subtle.digest("SHA-256", enc);
  return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, "0")).join("");
}

function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization",
    },
  });
}

function textResponse(text, status = 200, headers = {}) {
  return new Response(text, {
    status,
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization",
      ...headers,
    },
  });
}

async function verifyAuth(request, env) {
  const authHeader = request.headers.get("Authorization") || "";
  const token = authHeader.replace(/^Bearer\s+/i, "").trim();
  if (!token) return null;

  try {
    const raw = atob(token);
    const [username, expStr, sig] = raw.split(":");
    if (!username || !expStr || !sig) return null;

    if (Date.now() > parseInt(expStr, 10)) return null;

    const expectedSig = (await hashPassword(username + expStr)).substring(0, 16);
    if (sig !== expectedSig) return null;

    const usersJson = await env.SURFSHARK_KV.get("users_registry");
    const users = usersJson ? JSON.parse(usersJson) : {};
    const user = users[username];
    if (!user) return null;

    return { username, role: user.role };
  } catch (e) {
    return null;
  }
}

async function createToken(username) {
  const exp = Date.now() + 30 * 86400 * 1000; // 30 days session
  const sig = (await hashPassword(username + exp)).substring(0, 16);
  return btoa(`${username}:${exp}:${sig}`);
}

function parseWgNode(line) {
  try {
    const [mainPart, hashRemark] = line.split("#");
    const remark = hashRemark ? decodeURIComponent(hashRemark) : "WireGuard";
    const parsedUrl = new URL(mainPart);
    const endpoint = parsedUrl.host;
    const publicKey = parsedUrl.searchParams.get("publicKey") || "";
    const privateKey = parsedUrl.searchParams.get("privateKey") || "";
    const presharedKey = parsedUrl.searchParams.get("presharedKey") || "";
    const ip = parsedUrl.searchParams.get("ip") || "10.14.0.2";
    return { remark, endpoint, publicKey, privateKey, presharedKey, ip, raw: line };
  } catch (e) {
    return null;
  }
}

function generateWireguardConf(node) {
  return `[Interface]
PrivateKey = ${node.privateKey}
Address = ${node.ip}/16
DNS = 162.252.172.57, 149.154.159.92

[Peer]
PublicKey = ${node.publicKey}
${node.presharedKey ? `PresharedKey = ${node.presharedKey}\n` : ""}Endpoint = ${node.endpoint}
AllowedIPs = 0.0.0.0/0, ::/0
PersistentKeepalive = 25
`;
}

function generateClashMetaYaml(nodes) {
  const proxies = [];
  for (const n of nodes) {
    if (n.startsWith("wg://")) {
      const parsed = parseWgNode(n);
      if (!parsed) continue;
      const [server, port] = parsed.endpoint.split(":");
      proxies.push({
        name: parsed.remark.replace(/[:[\]]/g, "_"),
        type: "wireguard",
        server: server,
        port: parseInt(port || "51820", 10),
        ip: parsed.ip,
        "public-key": parsed.publicKey,
        "private-key": parsed.privateKey,
        udp: true,
        remote_dns_resolve: true,
        dns: ["162.252.172.57", "149.154.159.92"]
      });
    } else if (n.startsWith("vless://")) {
      try {
        const u = new URL(n);
        const uuid = u.username;
        const server = u.hostname;
        const port = parseInt(u.port || "443", 10);
        const remark = u.hash ? decodeURIComponent(u.hash.slice(1)) : "VLESS";
        const params = u.searchParams;
        proxies.push({
          name: remark.replace(/[:[\]]/g, "_"),
          type: "vless",
          server: server,
          port: port,
          uuid: uuid,
          cipher: "none",
          tls: params.get("security") === "tls" || params.get("security") === "reality",
          "skip-cert-verify": true,
          servername: params.get("sni") || server,
          network: params.get("type") || "ws",
          "ws-opts": params.get("type") === "ws" ? { path: params.get("path") || "/", headers: { Host: params.get("host") || server } } : undefined
        });
      } catch (e) {}
    }
  }

  const proxyNames = proxies.map(p => `      - "${p.name}"`).join("\n");
  let yaml = `port: 7890
socks-port: 7891
allow-lan: false
mode: rule
log-level: info
proxies:\n`;

  for (const p of proxies) {
    yaml += `  - name: "${p.name}"\n    type: ${p.type}\n    server: ${p.server}\n    port: ${p.port}\n`;
    if (p.type === "wireguard") {
      yaml += `    ip: ${p.ip}\n    public-key: "${p['public-key']}"\n    private-key: "${p['private-key']}"\n    udp: true\n`;
    } else if (p.type === "vless") {
      yaml += `    uuid: "${p.uuid}"\n    tls: ${p.tls}\n    network: ${p.network}\n    servername: "${p.servername}"\n`;
      if (p['ws-opts']) {
        yaml += `    ws-opts:\n      path: "${p['ws-opts'].path}"\n      headers:\n        Host: "${p['ws-opts'].headers.Host}"\n`;
      }
    }
  }

  yaml += `\nproxy-groups:\n  - name: "AUTO-SELECT"\n    type: url-test\n    url: http://www.gstatic.com/generate_204\n    interval: 300\n    proxies:\n${proxyNames}\n`;
  yaml += `  - name: "PROXY"\n    type: select\n    proxies:\n      - "AUTO-SELECT"\n${proxyNames}\n`;
  yaml += `\nrules:\n  - MATCH,PROXY\n`;
  return yaml;
}

function generateSingBoxJson(nodes) {
  const outbounds = [];
  for (const n of nodes) {
    if (n.startsWith("wg://")) {
      const parsed = parseWgNode(n);
      if (!parsed) continue;
      const [server, port] = parsed.endpoint.split(":");
      outbounds.push({
        type: "wireguard",
        tag: parsed.remark,
        server: server,
        server_port: parseInt(port || "51820", 10),
        local_address: [`${parsed.ip}/32`],
        private_key: parsed.privateKey,
        peer_public_key: parsed.publicKey,
        system_interface: false
      });
    }
  }
  return JSON.stringify({
    version: 1,
    outbounds: outbounds.length > 0 ? outbounds : []
  }, null, 2);
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const params = url.searchParams;

    // Handle CORS preflight
    if (request.method === "OPTIONS") {
      return new Response(null, {
        headers: {
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type, Authorization",
        },
      });
    }

    // ==========================================
    // 🛡 SECURITY: Block traffic from China (CN) & Russia (RU)
    // ==========================================
    const clientCountry = (request.cf?.country || "").toUpperCase();
    if (clientCountry === "CN" || clientCountry === "RU") {
      return new Response("Access Denied (403): Access is blocked from your geographic region.", {
        status: 403,
        headers: { "Content-Type": "text/plain; charset=utf-8" },
      });
    }

    // ==========================================
    // 3. API: EDGE HEALTH CHECK & LATENCY (/api/health)
    // ==========================================
    if (url.pathname === "/api/health" || url.pathname === "/health") {
      const checkTarget = async (name, testUrl) => {
        const start = Date.now();
        try {
          const resp = await fetch(testUrl, { method: "HEAD", signal: AbortSignal.timeout(4000) });
          return { name, status: resp.ok || resp.status < 500 ? "online" : "warning", latency: Date.now() - start, code: resp.status };
        } catch (e) {
          return { name, status: "offline", latency: Date.now() - start, error: e.message };
        }
      };

      const results = await Promise.all([
        checkTarget("Iran Arvan Gateway (karajlasik.ir)", `${CLINIC_API_BASE}/`),
        checkTarget("US RackNerd Core (api.iranlasik.ir)", "https://api.iranlasik.ir/"),
        checkTarget("Surfshark Nodes Repo", `${GITHUB_PAGES_BASE}/sub.txt`),
      ]);

      return jsonResponse({
        success: true,
        edgeColo: request.cf?.colo || "UNKNOWN",
        clientCountry: request.cf?.country || "UNKNOWN",
        timestamp: new Date().toISOString(),
        targets: results,
      });
    }

    // ==========================================
    // 0. WEB APP & STATIC PROXY (Cloudflare Edge)
    // ==========================================
    if (url.pathname === "/" || url.pathname === "/index.html" || url.pathname === "/app") {
      const isHtml = (request.headers.get("Accept") || "").includes("text/html");
      const hasSubParam = params.has("key") || params.has("exp") || params.has("format") || params.has("b64") || params.has("tier") || params.has("type");
      if (isHtml && !hasSubParam) {
        try {
          const upstream = await fetch(`${GITHUB_PAGES_BASE}/index.html`, {
            cf: { cacheTtl: 180, cacheEverything: true },
          });
          if (upstream.ok) {
            const html = await upstream.text();
            return new Response(html, {
              status: 200,
              headers: {
                "Content-Type": "text/html; charset=utf-8",
                "Access-Control-Allow-Origin": "*",
                "Cache-Control": "public, max-age=180",
              },
            });
          }
        } catch (e) {
          // fall through
        }
      }
    }

    // Static Assets Proxy (.txt, .svg, .png, .json)
    if (
      url.pathname.endsWith(".txt") ||
      url.pathname.endsWith(".svg") ||
      url.pathname.endsWith(".png") ||
      url.pathname.endsWith(".json")
    ) {
      try {
        const assetResp = await fetch(`${GITHUB_PAGES_BASE}${url.pathname}`, {
          cf: { cacheTtl: 300, cacheEverything: true },
        });
        if (assetResp.ok) {
          const contentType = assetResp.headers.get("Content-Type") || "text/plain; charset=utf-8";
          return new Response(assetResp.body, {
            status: 200,
            headers: {
              "Content-Type": contentType,
              "Access-Control-Allow-Origin": "*",
              "Cache-Control": "public, max-age=300",
            },
          });
        }
      } catch (e) {
        // fall through
      }
    }

    // ==========================================
    // 1. API: AUTH STATUS & SETUP (First-time Admin)
    // ==========================================
    if (url.pathname === "/api/auth/status") {
      const usersJson = await env.SURFSHARK_KV.get("users_registry");
      const users = usersJson ? JSON.parse(usersJson) : {};
      const hasUsers = Object.keys(users).length > 0;
      return jsonResponse({ hasAdmin: hasUsers, count: Object.keys(users).length });
    }

    if (url.pathname === "/api/auth/setup" && request.method === "POST") {
      const usersJson = await env.SURFSHARK_KV.get("users_registry");
      let users = usersJson ? JSON.parse(usersJson) : {};
      
      if (Object.keys(users).length > 0) {
        return jsonResponse({ error: "System already initialized. Please login." }, 400);
      }

      const body = await request.json();
      const username = (body.username || "").trim().toLowerCase();
      const password = body.password || "";
      const recoveryKey = (body.recoveryKey || "").trim();

      if (!username || username.length < 3) {
        return jsonResponse({ error: "Username must be at least 3 characters." }, 400);
      }
      if (!password || password.length < 4) {
        return jsonResponse({ error: "Password must be at least 4 characters." }, 400);
      }
      if (!recoveryKey || recoveryKey.length < 6) {
        return jsonResponse({ error: "Recovery key must be at least 6 characters." }, 400);
      }

      const pwHash = await hashPassword(password);
      const recHash = await hashPassword(recoveryKey);

      users[username] = {
        passwordHash: pwHash,
        role: "admin",
        createdAt: Math.floor(Date.now() / 1000)
      };

      await env.SURFSHARK_KV.put("users_registry", JSON.stringify(users));
      await env.SURFSHARK_KV.put("master_recovery_hash", recHash);

      const token = await createToken(username);
      return jsonResponse({ success: true, token, username, role: "admin" });
    }

    // ==========================================
    // 2. API: LOGIN
    // ==========================================
    if (url.pathname === "/api/auth/login" && request.method === "POST") {
      const body = await request.json();
      const username = (body.username || "").trim().toLowerCase();
      const password = body.password || "";

      const usersJson = await env.SURFSHARK_KV.get("users_registry");
      const users = usersJson ? JSON.parse(usersJson) : {};
      const user = users[username];

      if (!user) {
        return jsonResponse({ error: "Invalid username or password" }, 401);
      }

      const pwHash = await hashPassword(password);
      if (pwHash !== user.passwordHash) {
        return jsonResponse({ error: "Invalid username or password" }, 401);
      }

      const token = await createToken(username);
      return jsonResponse({ success: true, token, username, role: user.role });
    }

    // ==========================================
    // 3. API: PASSWORD RESET (Using Master Recovery Key)
    // ==========================================
    if (url.pathname === "/api/auth/reset" && request.method === "POST") {
      const body = await request.json();
      const username = (body.username || "").trim().toLowerCase();
      const recoveryKey = (body.recoveryKey || "").trim();
      const newPassword = body.newPassword || "";

      if (!username || !recoveryKey || !newPassword) {
        return jsonResponse({ error: "Please fill all fields." }, 400);
      }

      const storedRecHash = await env.SURFSHARK_KV.get("master_recovery_hash");
      const inputRecHash = await hashPassword(recoveryKey);

      if (!storedRecHash || storedRecHash !== inputRecHash) {
        return jsonResponse({ error: "Invalid Recovery Key!" }, 403);
      }

      const usersJson = await env.SURFSHARK_KV.get("users_registry");
      let users = usersJson ? JSON.parse(usersJson) : {};
      if (!users[username]) {
        return jsonResponse({ error: `User ${username} not found.` }, 404);
      }

      users[username].passwordHash = await hashPassword(newPassword);
      await env.SURFSHARK_KV.put("users_registry", JSON.stringify(users));
      return jsonResponse({ success: true, message: "Password reset successfully! You can now login." });
    }

    // ==========================================
    // 4. API: GET ME (Check Session)
    // ==========================================
    if (url.pathname === "/api/auth/me") {
      const auth = await verifyAuth(request, env);
      if (!auth) return jsonResponse({ error: "Unauthorized" }, 401);
      return jsonResponse({ authenticated: true, user: auth });
    }

    // ==========================================
    // 5. API: USERS MANAGEMENT (Admin Only)
    // ==========================================
    if (url.pathname === "/api/users") {
      const auth = await verifyAuth(request, env);
      if (!auth || auth.role !== "admin") {
        return jsonResponse({ error: "Admin access required." }, 403);
      }

      const usersJson = await env.SURFSHARK_KV.get("users_registry");
      let users = usersJson ? JSON.parse(usersJson) : {};

      // GET: List all users
      if (request.method === "GET") {
        const userList = Object.keys(users).map(u => ({
          username: u,
          role: users[u].role,
          createdAt: users[u].createdAt
        }));
        return jsonResponse({ users: userList });
      }

      // POST: Create a new user account
      if (request.method === "POST") {
        const body = await request.json();
        const newU = (body.username || "").trim().toLowerCase();
        const newP = body.password || "";
        const role = body.role === "admin" ? "admin" : "user";

        if (!newU || newU.length < 3) return jsonResponse({ error: "Username too short." }, 400);
        if (!newP || newP.length < 4) return jsonResponse({ error: "Password too short." }, 400);

        if (users[newU]) return jsonResponse({ error: "User already exists." }, 400);

        users[newU] = {
          passwordHash: await hashPassword(newP),
          role: role,
          createdAt: Math.floor(Date.now() / 1000)
        };

        await env.SURFSHARK_KV.put("users_registry", JSON.stringify(users));
        return jsonResponse({ success: true, message: `User ${newU} created.` });
      }

      // DELETE: Delete user
      if (request.method === "DELETE") {
        const targetU = (params.get("user") || "").trim().toLowerCase();
        if (!targetU) return jsonResponse({ error: "User parameter missing" }, 400);
        if (targetU === auth.username) return jsonResponse({ error: "Cannot delete your own admin account!" }, 400);

        delete users[targetU];
        await env.SURFSHARK_KV.put("users_registry", JSON.stringify(users));
        await env.SURFSHARK_KV.delete(`devices:${targetU}`);
        return jsonResponse({ success: true, message: `User ${targetU} deleted.` });
      }
    }

    // ==========================================
    // 6. API: CLOUD DEVICES SYNC (KV)
    // ==========================================
    if (url.pathname === "/api/devices") {
      const auth = await verifyAuth(request, env);
      if (!auth) return jsonResponse({ error: "Unauthorized" }, 401);

      if (auth.role !== "admin") {
        return jsonResponse({ error: "Forbidden: Device management is restricted to Admin only." }, 403);
      }

      const targetUsername = params.has("user") ? params.get("user") : auth.username;
      const kvKey = `devices:${targetUsername}`;

      // GET: Retrieve user devices from Cloudflare KV
      if (request.method === "GET") {
        const devJson = await env.SURFSHARK_KV.get(kvKey);
        const devices = devJson ? JSON.parse(devJson) : [];
        return jsonResponse({ devices, username: targetUsername });
      }

      // POST / PUT: Save or append/update device in Cloudflare KV
      if (request.method === "POST" || request.method === "PUT") {
        const newDev = await request.json();
        if (!newDev || !newDev.name) {
          return jsonResponse({ error: "Invalid device data: name is required" }, 400);
        }
        if (!newDev.id) {
          newDev.id = "dev_" + Date.now();
        }
        if (newDev.key === undefined) {
          newDev.key = "";
        }

        const devJson = await env.SURFSHARK_KV.get(kvKey);
        let devices = devJson ? JSON.parse(devJson) : [];

        // Match existing device by id OR by name
        const existingIdx = devices.findIndex(d => (d.id && d.id === newDev.id) || (d.name && d.name.trim() === newDev.name.trim()));
        if (existingIdx !== -1) {
          devices[existingIdx] = { ...devices[existingIdx], ...newDev };
        } else {
          devices.unshift(newDev);
        }

        await env.SURFSHARK_KV.put(kvKey, JSON.stringify(devices));
        return jsonResponse({ success: true, devices });
      }

      // DELETE: Remove device from Cloudflare KV
      if (request.method === "DELETE") {
        const devId = params.get("id");
        if (!devId) return jsonResponse({ error: "Device ID missing" }, 400);

        const devJson = await env.SURFSHARK_KV.get(kvKey);
        let devices = devJson ? JSON.parse(devJson) : [];
        devices = devices.filter(d => d.id !== devId);

        await env.SURFSHARK_KV.put(kvKey, JSON.stringify(devices));
        return jsonResponse({ success: true, devices });
      }
    }

    // ==========================================
    // 7. SUBSCRIPTION ENDPOINT (/sub)
    // ==========================================
    const deviceKey = params.get("key") || "";
    const expParam = params.get("exp") || "0";
    const quotaParam = params.get("quota") || params.get("quota_gb") || "0";
    const continent = (params.get("continent") || params.get("region") || "all").toLowerCase();
    const tier = (params.get("tier") || params.get("type") || "surfshark").toLowerCase();
    const rawFormatParam = params.get("format") || "";
    const format = rawFormatParam ? rawFormatParam.toLowerCase() : "base64";
    const selectedIsp = (params.get("isp") || "").toLowerCase();

    const nowSeconds = Math.floor(Date.now() / 1000);
    const expTimestamp = parseInt(expParam, 10) || 0;
    const finalExpire = expTimestamp > 0 ? expTimestamp : nowSeconds + 31536000;

    // Traffic quota calculation (in bytes)
    let quotaGb = parseFloat(String(quotaParam).replace(/[^0-9.]/g, "")) || 0;
    let totalBytes = 0;
    if (quotaGb > 0) {
      totalBytes = Math.floor(quotaGb * 1073741824); // 1 GB = 1024^3 bytes
    } else {
      totalBytes = 2147483648000; // ~2000 GB default for unlimited
    }
    const uploadBytes = 104857600;   // 100 MB simulated active usage
    const downloadBytes = 524288000; // 500 MB simulated active usage
    const userinfoStr = `upload=${uploadBytes}; download=${downloadBytes}; total=${totalBytes}; expire=${finalExpire}`;

    // Check expiration
    const isExpired = expTimestamp > 0 && nowSeconds > expTimestamp;
    if (isExpired) {
      const expDateStr = new Date(expTimestamp * 1000).toISOString().split("T")[0];
      const expiredRemark = encodeURIComponent(`⚠️ Subscription Expired on ${expDateStr} — Contact Admin`);
      const alertNode = `wg://127.0.0.1:51820?publicKey=dZNq48noPkey9rwSbAU%2BmasbafpDSaAmtAMaP%2BgzLxA%3D&privateKey=GJfG1b7zCubnBHQHdNyJVKDMtoylDQgfpqZDhm4jjVM%3D&ip=10.14.0.2#${expiredRemark}`;
      
      const payload = (format === "base64" || params.get("b64") === "1") ? btoa(alertNode) : alertNode;
      return textResponse(payload, 200, {
        "X-Subscription-Status": "Expired",
        "Subscription-Userinfo": `upload=${totalBytes}; download=0; total=${totalBytes}; expire=${expTimestamp}`
      });
    }

    // Detect ISP from ASN or parameter
    const asn = request.cf?.asn || 0;
    const asOrg = (request.cf?.asOrganization || "").toLowerCase();
    let detectedIsp = selectedIsp;
    if (!detectedIsp) {
      if (asn === 197207 || asOrg.includes("mobile telecommunication")) detectedIsp = "mci";
      else if (asn === 44244 || asOrg.includes("irancell")) detectedIsp = "mtn";
      else if (asn === 57218 || asOrg.includes("rightel")) detectedIsp = "rightel";
      else if (asOrg.includes("shatel") || asOrg.includes("telecommunication")) detectedIsp = "wifi";
    }

    // ----------------------------------------------------
    // 7.1. HYBRID CLINIC TIERS (family, 2hop, 3hop, pro)
    // ----------------------------------------------------
    if (["family", "2hop", "3hop", "pro"].includes(tier)) {
      const clinicPath = tier === "family" ? "/sub/family" : `/sub/${tier}`;
      try {
        const clinicResp = await fetch(`${CLINIC_API_BASE}${clinicPath}?quota=${quotaGb}&exp=${finalExpire}`, {
          headers: { "User-Agent": "v2rayNG/1.8.5 Cloudflare-Worker" },
          cf: { cacheTtl: 60, cacheEverything: false }
        });
        if (clinicResp.ok) {
          const rawClinic = await clinicResp.text();
          let decodedClinic = rawClinic.trim();
          try {
            decodedClinic = atob(decodedClinic.trim());
          } catch (e) {
            // Already plain text
          }
          let clinicLines = decodedClinic.split("\n").map(l => l.trim()).filter(l => l.length > 0);

          // Standard Profile Headers
          const clinicHeaders = {
            "Subscription-Userinfo": userinfoStr,
            "Profile-Update-Interval": "6",
            "Profile-Title": btoa(unescape(encodeURIComponent(`KarajLasik-${tier.toUpperCase()}${quotaGb > 0 ? `-${quotaGb}GB` : ""}`))),
            "X-Subscription-Tier": tier,
            "X-Subscription-Quota-GB": String(quotaGb > 0 ? quotaGb : "Unlimited"),
            "X-Detected-ISP": detectedIsp || "Universal",
            "Cache-Control": "public, max-age=120"
          };

          if (format === "clash" || format === "clashmeta") {
            return textResponse(generateClashMetaYaml(clinicLines), 200, {
              ...clinicHeaders,
              "Content-Disposition": `attachment; filename="KarajLasik_${tier}.yaml"`
            });
          }

          if (format === "singbox") {
            return jsonResponse(JSON.parse(generateSingBoxJson(clinicLines)), 200);
          }

          const joinedBody = clinicLines.join("\n") + "\n";
          const finalPayload = (format === "raw") ? joinedBody : btoa(unescape(encodeURIComponent(joinedBody)));
          return textResponse(finalPayload, 200, clinicHeaders);
        }
      } catch (err) {
        // Fall through to Surfshark nodes if clinic server is unreachable
      }
    }

    // ----------------------------------------------------
    // 7.2. SURFSHARK AMNEZIAWG TIERS (GitHub Pages Source)
    // ----------------------------------------------------
    let cleanContinent = continent.replace(/[\s\-]+/g, "_");
    if (cleanContinent === "na" || cleanContinent === "northamerica") cleanContinent = "north_america";
    if (cleanContinent === "sa" || cleanContinent === "southamerica") cleanContinent = "south_america";

    let sourceFileName = "sub.txt";
    if (["europe", "north_america", "south_america", "asia", "americas", "africa", "oceania", "static"].includes(cleanContinent)) {
      sourceFileName = `sub_${cleanContinent}.txt`;
    }

    const targetUrl = `${GITHUB_PAGES_BASE}/${sourceFileName}`;

    try {
      let upstreamResp = await fetch(targetUrl, {
        cf: { cacheTtl: 120, cacheEverything: true },
      });

      if (!upstreamResp.ok) {
        const rawFallbackUrl = `https://raw.githubusercontent.com/Behrouz64/Surfshark-AmneziaWG-Mobile/master/${sourceFileName}`;
        upstreamResp = await fetch(rawFallbackUrl, {
          cf: { cacheTtl: 120, cacheEverything: true },
        });
      }

      if (!upstreamResp.ok) {
        return textResponse(`Error fetching upstream: ${upstreamResp.status}`, 502);
      }

      const rawContent = await upstreamResp.text();
      const lines = rawContent.split("\n").map(l => l.trim()).filter(l => l.startsWith("wg://"));

      if (lines.length === 0) {
        return textResponse("No active nodes found in subscription.", 500);
      }

      // Add status info banner if expiring
      let infoNode = null;
      if (expTimestamp > 0) {
        const daysLeft = Math.ceil((expTimestamp - nowSeconds) / 86400);
        const expDateStr = new Date(expTimestamp * 1000).toISOString().split("T")[0];
        const infoRemark = encodeURIComponent(`⏳ Subscription Active until ${expDateStr} (${daysLeft} days left)`);
        infoNode = `wg://10.255.255.1:51820?publicKey=dZNq48noPkey9rwSbAU%2BmasbafpDSaAmtAMaP%2BgzLxA%3D&privateKey=GJfG1b7zCubnBHQHdNyJVKDMtoylDQgfpqZDhm4jjVM%3D&ip=10.14.0.2#${infoRemark}`;
      }

      const noObfs = params.get("obfs") === "0" || params.get("noobfs") === "1" || params.get("preset") === "none";
      const encodedDeviceKey = encodeURIComponent(deviceKey);
      const processedNodes = lines.map(line => {
        let node = line;
        if (deviceKey) {
          node = node.replace(/privateKey=[^&]+/, `privateKey=${encodedDeviceKey}`);
        }
        if (noObfs) {
          node = node.replace(/&obfs=[^&]+/, "").replace(/&obfsParam=[^&#]+/, "");
        }
        return node;
      });

      const allNodes = infoNode ? [infoNode, ...processedNodes] : processedNodes;

      // Subscription standard headers
      const standardHeaders = {
        "Subscription-Userinfo": userinfoStr,
        "Profile-Update-Interval": "6",
        "Profile-Title": btoa(unescape(encodeURIComponent(`Surfshark AmneziaWG${quotaGb > 0 ? ` (${quotaGb}GB)` : ""}`))),
        "X-Subscription-Quota-GB": String(quotaGb > 0 ? quotaGb : "Unlimited"),
        "X-Nodes-Count": String(processedNodes.length),
        "X-Detected-ISP": detectedIsp || "Universal",
        "Cache-Control": "public, max-age=180"
      };

      // Format 1: Native WireGuard Configuration (.conf)
      if (format === "conf" || format === "wgconf") {
        const firstNode = processedNodes[0] ? parseWgNode(processedNodes[0]) : null;
        if (!firstNode) return textResponse("Unable to parse WireGuard node.", 400);
        return textResponse(generateWireguardConf(firstNode), 200, {
          ...standardHeaders,
          "Content-Type": "application/x-wireguard-profile",
          "Content-Disposition": 'attachment; filename="Surfshark_AmneziaWG.conf"'
        });
      }

      // Format 2: Clash Meta YAML Configuration
      if (format === "clash" || format === "clashmeta") {
        return textResponse(generateClashMetaYaml(allNodes), 200, {
          ...standardHeaders,
          "Content-Disposition": 'attachment; filename="Surfshark_ClashMeta.yaml"'
        });
      }

      // Format 3: Sing-Box JSON Configuration
      if (format === "singbox") {
        return jsonResponse(JSON.parse(generateSingBoxJson(allNodes)), 200);
      }

      // Format 4: Standard Raw or Base64 (V2rayNG, Shadowrocket)
      const finalBody = allNodes.join("\n") + "\n";
      const returnB64 = format === "base64" || params.get("b64") === "1" || params.get("format") === "base64";
      const outputPayload = returnB64 ? btoa(unescape(encodeURIComponent(finalBody))) : finalBody;

      return textResponse(outputPayload, 200, standardHeaders);

    } catch (err) {
      return textResponse(`Worker internal error: ${err.message}`, 500);
    }
  },
};

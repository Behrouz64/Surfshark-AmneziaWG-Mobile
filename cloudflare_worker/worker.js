/**
 * Cloudflare Worker for Surfshark AmneziaWG
 * - Multi-User Management with Cloudflare KV
 * - Role-Based Access (Admin & Standard Users)
 * - Cloud Device Synchronization across Mobile & Desktop
 * - Password Reset with Master Recovery Key
 * - Dynamic Private Key & Expiry Subscriptions for Shadowrocket
 */

const GITHUB_PAGES_BASE = "https://behrouz64.github.io/Surfshark-AmneziaWG-Mobile";
const JWT_SECRET = "surfshark_awg_secret_salt_2026";

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
      
      // If admin already exists, don't allow re-setup
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

      const targetUsername = (auth.role === "admin" && params.has("user")) ? params.get("user") : auth.username;
      const kvKey = `devices:${targetUsername}`;

      // GET: Retrieve user devices from Cloudflare KV
      if (request.method === "GET") {
        const devJson = await env.SURFSHARK_KV.get(kvKey);
        const devices = devJson ? JSON.parse(devJson) : [];
        return jsonResponse({ devices, username: targetUsername });
      }

      // POST: Save or append device to Cloudflare KV
      if (request.method === "POST") {
        const newDev = await request.json();
        if (!newDev || !newDev.name || !newDev.key) {
          return jsonResponse({ error: "Invalid device data" }, 400);
        }

        const devJson = await env.SURFSHARK_KV.get(kvKey);
        let devices = devJson ? JSON.parse(devJson) : [];

        // Check if device with same ID exists, update or add to front
        const existingIdx = devices.findIndex(d => d.id === newDev.id);
        if (existingIdx !== -1) {
          devices[existingIdx] = newDev;
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
    const continent = (params.get("continent") || params.get("region") || "all").toLowerCase();
    const returnB64 = params.get("b64") === "1" || params.get("format") === "base64";

    const nowSeconds = Math.floor(Date.now() / 1000);
    const expTimestamp = parseInt(expParam, 10) || 0;

    // Check expiration
    const isExpired = expTimestamp > 0 && nowSeconds > expTimestamp;
    if (isExpired) {
      const expDateStr = new Date(expTimestamp * 1000).toISOString().split("T")[0];
      const expiredRemark = encodeURIComponent(`⚠️ Subscription Expired on ${expDateStr} — Contact Admin`);
      const alertNode = `wg://127.0.0.1:51820?publicKey=dZNq48noPkey9rwSbAU%2BmasbafpDSaAmtAMaP%2BgzLxA%3D&privateKey=GJfG1b7zCubnBHQHdNyJVKDMtoylDQgfpqZDhm4jjVM%3D&ip=10.14.0.2#${expiredRemark}`;
      
      const payload = returnB64 ? btoa(alertNode) : alertNode;
      return textResponse(payload, 200, { "X-Subscription-Status": "Expired" });
    }

    // Determine target subscription file from GitHub Pages
    let cleanContinent = continent.replace(/[\s\-]+/g, "_");
    if (cleanContinent === "na" || cleanContinent === "northamerica") cleanContinent = "north_america";
    if (cleanContinent === "sa" || cleanContinent === "southamerica") cleanContinent = "south_america";

    let sourceFileName = "sub.txt";
    if (["europe", "north_america", "south_america", "asia", "americas", "africa", "oceania"].includes(cleanContinent)) {
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
      const finalBody = allNodes.join("\n") + "\n";
      const outputPayload = returnB64 ? btoa(unescape(encodeURIComponent(finalBody))) : finalBody;

      return textResponse(outputPayload, 200, {
        "Cache-Control": "public, max-age=180",
        "X-Nodes-Count": String(processedNodes.length),
      });

    } catch (err) {
      return textResponse(`Worker internal error: ${err.message}`, 500);
    }
  },
};

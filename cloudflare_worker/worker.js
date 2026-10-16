/**
 * Cloudflare Worker for Surfshark AmneziaWG Dynamic Multi-Device Subscriptions
 * 
 * Features:
 * - Dynamic Private Key injection per device (?key=...)
 * - Device Name branding (?name=...)
 * - Expiration enforcement (?exp=UNIX_TIMESTAMP)
 * - Per-Continent filtering (?continent=europe|asia|americas|africa|oceania|all)
 * - Base64 output support (?b64=1)
 * - Informative status nodes inside Shadowrocket
 * - Edge CDN caching (5 minutes) for maximum speed and zero load
 */

const GITHUB_PAGES_BASE = "https://behrouz64.github.io/Surfshark-AmneziaWG-Mobile";

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const params = url.searchParams;

    // Handle CORS preflight
    if (request.method === "OPTIONS") {
      return new Response(null, {
        headers: {
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
          "Access-Control-Allow-Headers": "*",
        },
      });
    }

    // Default home/info page if accessed directly in a browser without parameters
    if (url.pathname === "/" && !params.has("key") && !params.has("sub")) {
      return new Response(
        `Surfshark AmneziaWG Dynamic Subscription Worker\n\n` +
        `Usage:\n` +
        `  ${url.origin}/sub?key=<PRIVATE_KEY>&name=<DEVICE_NAME>&exp=<UNIX_TIMESTAMP>&continent=<REGION>\n\n` +
        `Parameters:\n` +
        `  - key: Device WireGuard private key (Required)\n` +
        `  - name: Optional label for the device (e.g. iPhone-User)\n` +
        `  - exp: Expiration timestamp in seconds (0 or omitted for unlimited)\n` +
        `  - continent: all | europe | asia | americas | africa | oceania\n` +
        `  - b64: 1 to return Base64 encoded payload\n`,
        {
          headers: { "Content-Type": "text/plain; charset=utf-8" },
        }
      );
    }

    const deviceKey = params.get("key") || "";
    const deviceName = params.get("name") || "";
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
      // Return a visible expired alert node so Shadowrocket users clearly see it in the list
      const alertNode = `wg://127.0.0.1:51820?publicKey=dZNq48noPkey9rwSbAU%2BmasbafpDSaAmtAMaP%2BgzLxA%3D&privateKey=GJfG1b7zCubnBHQHdNyJVKDMtoylDQgfpqZDhm4jjVM%3D&ip=10.14.0.2#${expiredRemark}`;
      
      const payload = returnB64 ? btoa(alertNode) : alertNode;
      return new Response(payload, {
        status: 200,
        headers: {
          "Content-Type": "text/plain; charset=utf-8",
          "Access-Control-Allow-Origin": "*",
          "X-Subscription-Status": "Expired",
        },
      });
    }

    // Determine target subscription file from GitHub Pages
    let sourceFileName = "sub.txt";
    if (["europe", "asia", "americas", "africa", "oceania"].includes(continent)) {
      sourceFileName = `sub_${continent}.txt`;
    }

    const targetUrl = `${GITHUB_PAGES_BASE}/${sourceFileName}`;

    try {
      // Fetch fresh upstream nodes with Cloudflare Edge caching
      const upstreamResp = await fetch(targetUrl, {
        cf: {
          cacheTtl: 300, // Cache for 5 minutes at edge
          cacheEverything: true,
        },
      });

      if (!upstreamResp.ok) {
        return new Response(`Error fetching subscription from upstream: ${upstreamResp.status}`, {
          status: 502,
          headers: { "Content-Type": "text/plain; charset=utf-8" },
        });
      }

      const rawContent = await upstreamResp.text();
      const lines = rawContent.split("\n").map(l => l.trim()).filter(l => l.startsWith("wg://"));

      if (lines.length === 0) {
        return new Response("No active nodes found in subscription.", { status: 500 });
      }

      // Calculate days remaining info if expiry is set
      let infoNode = null;
      if (expTimestamp > 0) {
        const daysLeft = Math.ceil((expTimestamp - nowSeconds) / 86400);
        const expDateStr = new Date(expTimestamp * 1000).toISOString().split("T")[0];
        const infoRemark = encodeURIComponent(`⏳ Subscription Active until ${expDateStr} (${daysLeft} days left)`);
        // Dummy non-routable node that acts as a visible status banner in Shadowrocket
        infoNode = `wg://10.255.255.1:51820?publicKey=dZNq48noPkey9rwSbAU%2BmasbafpDSaAmtAMaP%2BgzLxA%3D&privateKey=GJfG1b7zCubnBHQHdNyJVKDMtoylDQgfpqZDhm4jjVM%3D&ip=10.14.0.2#${infoRemark}`;
      }

      // Format target private key for URL query substitution
      const encodedDeviceKey = encodeURIComponent(deviceKey);

      // Process nodes: substitute privateKey without altering server names
      const processedNodes = lines.map(line => {
        let node = line;

        // Replace private key if specified
        if (deviceKey) {
          node = node.replace(/privateKey=[^&]+/, `privateKey=${encodedDeviceKey}`);
        }

        return node;
      });

      const allNodes = infoNode ? [infoNode, ...processedNodes] : processedNodes;
      const finalBody = allNodes.join("\n") + "\n";

      const outputPayload = returnB64 ? btoa(unescape(encodeURIComponent(finalBody))) : finalBody;

      return new Response(outputPayload, {
        status: 200,
        headers: {
          "Content-Type": "text/plain; charset=utf-8",
          "Access-Control-Allow-Origin": "*",
          "Cache-Control": "public, max-age=180",
          "X-Device-Name": deviceName,
          "X-Nodes-Count": String(processedNodes.length),
        },
      });

    } catch (err) {
      return new Response(`Worker internal error: ${err.message}`, {
        status: 500,
        headers: { "Content-Type": "text/plain; charset=utf-8" },
      });
    }
  },
};

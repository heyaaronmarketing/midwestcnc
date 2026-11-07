// Cloudflare Worker entry for midwestcncservices.com (Workers + Static Assets).
//
// Static files are served directly by the assets binding; this Worker only
// runs for requests that do not match a static asset — i.e. /api/quote.
//
// Deploy pattern mirrors bandrproduction: worker.js + wrangler.jsonc +
// .assetsignore at the site root. Cloudflare Git integration builds on push.
//
// Email routing:
//   To:       ken@midwestcncservices.com (production default, override
//             with NOTIFY_EMAIL env var — comma-separated for multiple).
//   From:     verified sender you own — CANNOT be the customer's email
//             (SPF/DKIM/DMARC would reject it as spoofing). Default is
//             quotes@midwestcncservices.com — override with FROM_EMAIL.
//   Reply-To: the customer's email, so a plain Reply in Ken's client
//             goes straight back to them. Not configurable — always
//             the submitter's email.
//
// Required Cloudflare env vars (Workers > Settings > Variables and Secrets):
//   RESEND_API_KEY    — secret, from https://resend.com/api-keys
//
// Optional (defaults live in the code below):
//   NOTIFY_EMAIL      — comma-separated list of inboxes to notify.
//                       Default: ken@midwestcncservices.com
//   FROM_EMAIL        — verified Resend sender.
//                       Default: "Midwest CNC Quote Form <quotes@midwestcncservices.com>"
//                       (requires midwestcncservices.com verified in Resend).
//                       For a first test before the domain is verified,
//                       override to "Midwest CNC <onboarding@resend.dev>" —
//                       Resend's shared sender only delivers to the Resend
//                       account owner's own address, so also set
//                       NOTIFY_EMAIL to that same address while testing.
//   TURNSTILE_SECRET  — server-side secret for the Turnstile widget on the
//                       form (widget site key 0x4AAAAAADXY93Hw7DfP3PQJ is
//                       already public in the HTML). If unset, Turnstile
//                       verification is skipped — useful for a first-pass
//                       Resend-only test.

const SUCCESS_PATH = "/get-a-quote/thank-you/";
const ERROR_PATH = "/get-a-quote/";
const REQUIRED_FIELDS = ["name", "company", "phone", "email", "service", "message"];
const PHONE = "319-610-4341";

// D1 schema — created lazily on first write. Idempotent so it's safe
// to CREATE TABLE IF NOT EXISTS on every request; SQLite short-circuits
// if the table already exists.
const QUOTES_SCHEMA = `
CREATE TABLE IF NOT EXISTS quotes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT NOT NULL,
  name TEXT NOT NULL,
  company TEXT NOT NULL,
  phone TEXT NOT NULL,
  email TEXT NOT NULL,
  machine_brand TEXT,
  machine_model TEXT,
  service TEXT NOT NULL,
  message TEXT NOT NULL,
  ip TEXT,
  user_agent TEXT,
  status TEXT NOT NULL DEFAULT 'new',
  notes TEXT DEFAULT '',
  email_sent INTEGER NOT NULL DEFAULT 0,
  email_error TEXT DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_quotes_status ON quotes(status);
CREATE INDEX IF NOT EXISTS idx_quotes_created_at ON quotes(created_at DESC);
`;

export default {
  // Weekly cron: pulls Google Search Console (and later Bing WMT) data
  // into the case-study D1 tables. Cron schedule set in wrangler.jsonc:
  // 0 13 * * 1 → Monday 13:00 UTC = 7 AM Central (CST, 8 AM CDT).
  //
  // Also callable ad-hoc from the admin page's "Refresh now" button.
  async scheduled(event, env, ctx) {
    ctx.waitUntil(runCaseStudyRefresh(env, { source: "cron", trigger: event.cron }));
  },

  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === "/api/quote") {
      if (request.method === "POST") return handleQuote(request, env);
      if (request.method === "GET") {
        return new Response("This endpoint accepts POST only.", {
          status: 405,
          headers: { "content-type": "text/plain; charset=utf-8" },
        });
      }
      return new Response("Method not allowed", { status: 405 });
    }

    if (url.pathname === "/api/case-study.json") {
      if (request.method === "GET") return handleCaseStudyJson(env);
      return new Response("Method not allowed", { status: 405 });
    }

    if (url.pathname === "/admin" || url.pathname.startsWith("/admin/")) {
      return handleAdmin(request, env, url);
    }

    // Trailing-slash normalization — 301 Permanent Redirect so Google
    // consolidates ranking signals. Cloudflare Workers Static Assets
    // defaults to a 307 Temporary Redirect, which Google does not treat
    // as permanent — resulting in duplicate URLs ranking separately.
    //
    // Scope: GET/HEAD only, extensionless paths (never /foo.webp or /foo.xml),
    // and not already-slashed. Preserves query string + fragment.
    if (
      (request.method === "GET" || request.method === "HEAD") &&
      !url.pathname.endsWith("/") &&
      !url.pathname.slice(url.pathname.lastIndexOf("/")).includes(".")
    ) {
      return Response.redirect(
        url.origin + url.pathname + "/" + url.search + url.hash,
        301,
      );
    }

    return env.ASSETS.fetch(request);
  },
};

async function handleQuote(request, env) {
  const url = new URL(request.url);

  let form;
  try {
    form = await request.formData();
  } catch (e) {
    return seeOther(url, `${ERROR_PATH}?error=bad-request`);
  }

  // Honeypot — bots fill this; humans never see it. Silently pretend
  // success so the bot doesn't retry.
  const honeypot = (form.get("botcheck") || "").toString().trim();
  if (honeypot !== "") return seeOther(url, SUCCESS_PATH);

  // Turnstile verification (skipped when TURNSTILE_SECRET is not set,
  // so the form works for a Resend-only first test).
  if (env.TURNSTILE_SECRET) {
    const token = (form.get("cf-turnstile-response") || "").toString();
    if (!token) return seeOther(url, `${ERROR_PATH}?error=captcha-missing`);
    const ok = await verifyTurnstile(
      env.TURNSTILE_SECRET,
      token,
      request.headers.get("cf-connecting-ip"),
    );
    if (!ok) return seeOther(url, `${ERROR_PATH}?error=captcha-failed`);
  }

  for (const f of REQUIRED_FIELDS) {
    const v = (form.get(f) || "").toString().trim();
    if (!v) return seeOther(url, `${ERROR_PATH}?error=missing-${f}`);
  }

  const payload = {
    name: trim(form, "name"),
    company: trim(form, "company"),
    phone: trim(form, "phone"),
    email: trim(form, "email"),
    machine_brand: trim(form, "machine_brand") || "—",
    machine_model: trim(form, "machine_model") || "—",
    service: trim(form, "service"),
    message: trim(form, "message"),
    timestamp: new Date().toISOString(),
    ip: request.headers.get("cf-connecting-ip") || "unknown",
    ua: request.headers.get("user-agent") || "unknown",
  };

  // Persist the submission to D1 before attempting delivery so nothing
  // is lost if email fails. Guarded — if the DB binding isn't wired yet,
  // this is a no-op and we still send the email.
  const saved = await saveToD1(env, payload);
  if (!saved.ok && saved.error !== "no-db-binding") {
    console.log("D1 save failed:", saved.error);
  }

  const sent = await sendNotificationEmail(env, payload);

  // Best-effort: annotate the D1 row with the email result so admins
  // can see delivery status alongside the submission.
  if (saved.ok) {
    await updateEmailStatus(env, saved.id, sent.ok, sent.error || "")
      .catch((e) => console.log("D1 status update failed:", e && e.message));
  }

  if (!sent.ok) {
    console.log("Resend send failed:", sent.error);
    return seeOther(url, `${ERROR_PATH}?error=email-failed`);
  }

  return seeOther(url, SUCCESS_PATH);
}

async function saveToD1(env, p) {
  if (!env.DB) return { ok: false, error: "no-db-binding" };
  try {
    await env.DB.exec(QUOTES_SCHEMA.replace(/\n/g, " "));
    const result = await env.DB.prepare(
      `INSERT INTO quotes
        (created_at, name, company, phone, email, machine_brand,
         machine_model, service, message, ip, user_agent)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
    )
      .bind(
        p.timestamp,
        p.name,
        p.company,
        p.phone,
        p.email,
        p.machine_brand,
        p.machine_model,
        p.service,
        p.message,
        p.ip,
        p.ua,
      )
      .run();
    return { ok: true, id: result.meta.last_row_id };
  } catch (e) {
    return { ok: false, error: String(e && e.message || e) };
  }
}

async function updateEmailStatus(env, id, sent, error) {
  if (!env.DB || !id) return;
  await env.DB.prepare(
    "UPDATE quotes SET email_sent = ?, email_error = ? WHERE id = ?",
  )
    .bind(sent ? 1 : 0, error || "", id)
    .run();
}

function trim(form, key) {
  return (form.get(key) || "").toString().trim();
}

function seeOther(originUrl, path) {
  return new Response(null, {
    status: 303,
    headers: { Location: new URL(path, originUrl).toString() },
  });
}

async function verifyTurnstile(secret, token, ip) {
  const body = new URLSearchParams();
  body.set("secret", secret);
  body.set("response", token);
  if (ip) body.set("remoteip", ip);
  try {
    const resp = await fetch(
      "https://challenges.cloudflare.com/turnstile/v0/siteverify",
      { method: "POST", body },
    );
    const data = await resp.json();
    return data && data.success === true;
  } catch (e) {
    console.log("Turnstile verify error:", e && e.message);
    return false;
  }
}

async function sendNotificationEmail(env, p) {
  if (!env.RESEND_API_KEY) return { ok: false, error: "RESEND_API_KEY not configured" };

  // From: verified Resend sender you own. Cannot be the customer's email
  // (would fail SPF/DKIM/DMARC). Customer's email goes in reply_to below.
  const fromEmail = env.FROM_EMAIL ||
    "Midwest CNC Quote Form <quotes@midwestcncservices.com>";

  // To: Ken by default. NOTIFY_EMAIL env var can override (comma-separated
  // to CC additional recipients, e.g. "ken@...,aaron@...").
  const recipients = (env.NOTIFY_EMAIL || "ken@midwestcncservices.com")
    .split(",").map((s) => s.trim()).filter(Boolean);
  if (recipients.length === 0) return { ok: false, error: "NOTIFY_EMAIL empty" };

  const subject = `Quote request: ${p.machine_brand} ${p.service}`.trim();

  const text = [
    `New quote request from the Midwest CNC Services website.`,
    ``,
    `Name:           ${p.name}`,
    `Company:        ${p.company}`,
    `Phone:          ${p.phone}`,
    `Email:          ${p.email}`,
    `Machine brand:  ${p.machine_brand}`,
    `Machine model:  ${p.machine_model}`,
    `Service needed: ${p.service}`,
    ``,
    `--- Message ---`,
    p.message,
    `---`,
    ``,
    `Submitted: ${p.timestamp}`,
    `IP:        ${p.ip}`,
    `Browser:   ${p.ua}`,
  ].join("\n");

  const html = [
    `<p><strong>New quote request from the Midwest CNC Services website.</strong></p>`,
    `<table style="border-collapse:collapse;font-family:system-ui,sans-serif;">`,
    `<tr><td style="padding:4px 12px 4px 0;color:#666;">Name:</td><td>${esc(p.name)}</td></tr>`,
    `<tr><td style="padding:4px 12px 4px 0;color:#666;">Company:</td><td>${esc(p.company)}</td></tr>`,
    `<tr><td style="padding:4px 12px 4px 0;color:#666;">Phone:</td><td><a href="tel:${esc(p.phone)}">${esc(p.phone)}</a></td></tr>`,
    `<tr><td style="padding:4px 12px 4px 0;color:#666;">Email:</td><td><a href="mailto:${esc(p.email)}">${esc(p.email)}</a></td></tr>`,
    `<tr><td style="padding:4px 12px 4px 0;color:#666;">Machine brand:</td><td>${esc(p.machine_brand)}</td></tr>`,
    `<tr><td style="padding:4px 12px 4px 0;color:#666;">Machine model:</td><td>${esc(p.machine_model)}</td></tr>`,
    `<tr><td style="padding:4px 12px 4px 0;color:#666;">Service needed:</td><td>${esc(p.service)}</td></tr>`,
    `</table>`,
    `<h3 style="margin:24px 0 4px 0;font-family:system-ui,sans-serif;">Message</h3>`,
    `<p style="font-family:system-ui,sans-serif;white-space:pre-wrap;">${esc(p.message)}</p>`,
    `<hr style="border:none;border-top:1px solid #eee;margin:24px 0;">`,
    `<p style="font-family:system-ui,sans-serif;color:#888;font-size:12px;">`,
    `Submitted ${esc(p.timestamp)} from ${esc(p.ip)}<br>`,
    `User agent: ${esc(p.ua)}`,
    `</p>`,
  ].join("");

  try {
    const resp = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${env.RESEND_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        from: fromEmail,
        to: recipients,
        reply_to: p.email,
        subject,
        text,
        html,
      }),
    });
    if (!resp.ok) {
      const body = await resp.text();
      return { ok: false, error: `Resend HTTP ${resp.status}: ${body}` };
    }
    return { ok: true };
  } catch (e) {
    return { ok: false, error: String(e && e.message || e) };
  }
}

function esc(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

// =====================================================================
// Admin UI — /admin/*
// =====================================================================
// Auth: single ADMIN_PASSWORD secret. Login POST verifies password
// (constant-time), issues a signed cookie (HMAC-SHA256 over expiry
// timestamp, key = SESSION_SECRET). Session length: 7 days.
//
// Storage: reads from the D1 'quotes' table. Read-only, list, detail,
// and mutation endpoints for status + notes. CSV export. Origin-checked
// on every state-changing POST (CSRF defense).
// =====================================================================

const SESSION_COOKIE = "mwc_admin";
const SESSION_TTL_SECONDS = 60 * 60 * 24 * 7; // 7 days
const STATUS_OPTIONS = ["new", "contacted", "quoted", "won", "dead"];

async function handleAdmin(request, env, url) {
  // Config sanity check before any auth. If secrets aren't set, show
  // a clear config-error page rather than a mysterious 500.
  if (!env.ADMIN_PASSWORD || !env.SESSION_SECRET) {
    return htmlResponse(
      renderConfigError(!env.ADMIN_PASSWORD, !env.SESSION_SECRET),
      500,
    );
  }

  const path = url.pathname;
  const method = request.method;

  // Login page — the only /admin path reachable without a session.
  if (path === "/admin/login") {
    if (method === "GET") return htmlResponse(renderLogin(""));
    if (method === "POST") return handleLogin(request, env, url);
    return new Response("Method not allowed", { status: 405 });
  }

  // Logout — clears the cookie, redirects to the login page.
  if (path === "/admin/logout") {
    return new Response(null, {
      status: 303,
      headers: {
        Location: new URL("/admin/login", url).toString(),
        "Set-Cookie": `${SESSION_COOKIE}=; Path=/admin; Max-Age=0; HttpOnly; Secure; SameSite=Lax`,
      },
    });
  }

  // Everything else requires a valid session.
  const session = await getSession(request, env);
  if (!session) {
    return new Response(null, {
      status: 303,
      headers: { Location: new URL("/admin/login", url).toString() },
    });
  }

  // Origin check for state-changing methods (CSRF defense).
  if (method === "POST") {
    const origin = request.headers.get("origin") || "";
    if (origin && !origin.startsWith(`${url.protocol}//${url.host}`)) {
      return new Response("Bad origin", { status: 403 });
    }
  }

  // Routes
  if (path === "/admin" || path === "/admin/") {
    return handleAdminList(request, env, url);
  }
  if (path === "/admin/export.csv") {
    return handleAdminExport(env);
  }
  if (path === "/admin/case-study") {
    if (method === "GET") return handleCaseStudyAdminPage(env);
    if (method === "POST") return handleCaseStudyUpload(request, env, url);
    return new Response("Method not allowed", { status: 405 });
  }
  if (path === "/admin/case-study/refresh") {
    if (method !== "POST") return new Response("Method not allowed", { status: 405 });
    const result = await runCaseStudyRefresh(env, { source: "manual" });
    const q = result.skipped
      ? `?rate_limited=${encodeURIComponent(result.retry_after_min + " min")}`
      : "?refreshed=1";
    return new Response(null, {
      status: 303,
      headers: { Location: new URL(`/admin/case-study${q}`, url).toString() },
    });
  }
  const detailMatch = path.match(/^\/admin\/quote\/(\d+)$/);
  if (detailMatch) {
    const id = parseInt(detailMatch[1], 10);
    if (method === "GET") return handleAdminDetail(env, url, id);
    if (method === "POST") return handleAdminUpdate(request, env, url, id);
    return new Response("Method not allowed", { status: 405 });
  }

  return htmlResponse(renderLayout("Not found", `<p>Not found.</p>`), 404);
}

// ---------- Login + session cookie ----------

async function handleLogin(request, env, url) {
  const form = await request.formData().catch(() => null);
  if (!form) return htmlResponse(renderLogin("Bad request."));
  const password = (form.get("password") || "").toString();
  if (!password) return htmlResponse(renderLogin("Enter a password."));

  const ok = await constantTimeStringEquals(password, env.ADMIN_PASSWORD);
  if (!ok) {
    // Small delay to slow a brute force on the login route itself.
    await new Promise((r) => setTimeout(r, 500));
    return htmlResponse(renderLogin("Wrong password."), 401);
  }

  const cookie = await mintSessionCookie(env.SESSION_SECRET);
  return new Response(null, {
    status: 303,
    headers: {
      Location: new URL("/admin", url).toString(),
      "Set-Cookie":
        `${SESSION_COOKIE}=${cookie}; Path=/admin; Max-Age=${SESSION_TTL_SECONDS}; ` +
        `HttpOnly; Secure; SameSite=Lax`,
    },
  });
}

async function getSession(request, env) {
  const cookieHeader = request.headers.get("cookie") || "";
  const match = cookieHeader.match(new RegExp(`(?:^|;\\s*)${SESSION_COOKIE}=([^;]+)`));
  if (!match) return null;
  return verifySessionCookie(match[1], env.SESSION_SECRET);
}

async function mintSessionCookie(secret) {
  const expiry = Math.floor(Date.now() / 1000) + SESSION_TTL_SECONDS;
  const payload = String(expiry);
  const sig = await hmacSha256B64(secret, payload);
  return `${payload}.${sig}`;
}

async function verifySessionCookie(cookie, secret) {
  const dot = cookie.lastIndexOf(".");
  if (dot < 0) return null;
  const payload = cookie.slice(0, dot);
  const providedSig = cookie.slice(dot + 1);
  const expectedSig = await hmacSha256B64(secret, payload);
  if (!(await constantTimeStringEquals(providedSig, expectedSig))) return null;
  const expiry = parseInt(payload, 10);
  if (!Number.isFinite(expiry) || expiry < Math.floor(Date.now() / 1000)) return null;
  return { expiry };
}

async function hmacSha256B64(secret, message) {
  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey(
    "raw", enc.encode(secret),
    { name: "HMAC", hash: "SHA-256" }, false, ["sign"],
  );
  const sig = await crypto.subtle.sign("HMAC", key, enc.encode(message));
  return b64UrlEncode(new Uint8Array(sig));
}

function b64UrlEncode(bytes) {
  let s = "";
  for (let i = 0; i < bytes.length; i++) s += String.fromCharCode(bytes[i]);
  return btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

async function constantTimeStringEquals(a, b) {
  // Hash both first so we never leak length via early return.
  const enc = new TextEncoder();
  const [ha, hb] = await Promise.all([
    crypto.subtle.digest("SHA-256", enc.encode(a)),
    crypto.subtle.digest("SHA-256", enc.encode(b)),
  ]);
  const av = new Uint8Array(ha), bv = new Uint8Array(hb);
  let diff = 0;
  for (let i = 0; i < av.length; i++) diff |= av[i] ^ bv[i];
  return diff === 0;
}

// ---------- Admin list ----------

async function handleAdminList(request, env, url) {
  if (!env.DB) {
    return htmlResponse(renderLayout(
      "Admin — no database",
      `<p class="empty">The D1 database binding isn't wired. Ask engineering to add
       <code>d1_databases</code> to <code>wrangler.jsonc</code>.</p>`,
    ));
  }
  // Ensure schema exists so a fresh DB doesn't throw before any writes.
  await env.DB.exec(QUOTES_SCHEMA.replace(/\n/g, " ")).catch(() => {});

  const q = url.searchParams.get("q") || "";
  const status = url.searchParams.get("status") || "";

  let sql = "SELECT id, created_at, name, company, phone, email, service, status, email_sent FROM quotes";
  const where = [];
  const args = [];
  if (status) {
    where.push("status = ?");
    args.push(status);
  }
  if (q) {
    where.push("(name LIKE ? OR company LIKE ? OR email LIKE ? OR phone LIKE ?)");
    const wc = `%${q}%`;
    args.push(wc, wc, wc, wc);
  }
  if (where.length) sql += " WHERE " + where.join(" AND ");
  sql += " ORDER BY datetime(created_at) DESC LIMIT 500";

  const { results } = await env.DB.prepare(sql).bind(...args).all();
  return htmlResponse(renderList(results || [], { q, status }));
}

// ---------- Admin detail ----------

async function handleAdminDetail(env, url, id) {
  const row = await env.DB.prepare("SELECT * FROM quotes WHERE id = ?").bind(id).first();
  if (!row) return htmlResponse(renderLayout("Not found", `<p>Quote #${id} not found.</p>`), 404);
  const saved = url.searchParams.get("saved") === "1";
  return htmlResponse(renderDetail(row, saved));
}

// ---------- Admin update (status + notes) ----------

async function handleAdminUpdate(request, env, url, id) {
  const form = await request.formData().catch(() => null);
  if (!form) return new Response("Bad request", { status: 400 });

  const newStatus = (form.get("status") || "").toString();
  const notes = (form.get("notes") || "").toString();

  if (!STATUS_OPTIONS.includes(newStatus)) {
    return new Response("Invalid status", { status: 400 });
  }

  await env.DB.prepare("UPDATE quotes SET status = ?, notes = ? WHERE id = ?")
    .bind(newStatus, notes, id)
    .run();

  return new Response(null, {
    status: 303,
    headers: { Location: new URL(`/admin/quote/${id}?saved=1`, url).toString() },
  });
}

// ---------- CSV export ----------

async function handleAdminExport(env) {
  const { results } = await env.DB.prepare(
    "SELECT id, created_at, name, company, phone, email, machine_brand, machine_model, " +
    "service, message, status, notes, email_sent, email_error FROM quotes " +
    "ORDER BY datetime(created_at) DESC",
  ).all();
  const header = [
    "id","created_at","name","company","phone","email","machine_brand",
    "machine_model","service","message","status","notes","email_sent","email_error",
  ];
  const rows = [header.join(",")];
  for (const r of results || []) {
    rows.push(header.map((k) => csvCell(r[k])).join(","));
  }
  return new Response(rows.join("\n"), {
    headers: {
      "Content-Type": "text/csv; charset=utf-8",
      "Content-Disposition": `attachment; filename="midwestcnc-quotes-${todayStamp()}.csv"`,
      "Cache-Control": "no-store",
    },
  });
}

function csvCell(v) {
  if (v === null || v === undefined) return "";
  const s = String(v);
  if (/[,"\n\r]/.test(s)) return `"${s.replace(/"/g, '""')}"`;
  return s;
}

function todayStamp() {
  return new Date().toISOString().slice(0, 10);
}

// ---------- Rendering ----------

function htmlResponse(body, status = 200) {
  return new Response(body, {
    status,
    headers: {
      "Content-Type": "text/html; charset=utf-8",
      "Cache-Control": "no-store",
      "X-Content-Type-Options": "nosniff",
      "X-Frame-Options": "DENY",
      "Referrer-Policy": "same-origin",
    },
  });
}

const BASE_CSS = `
  :root {
    --accent: #b8341a; --accent-dark: #8f2814; --line: #e4e2df;
    --surface: #ffffff; --surface-2: #f7f5f2; --bg: #fbf9f6;
    --fg: #1a1a1a; --muted: #6b6b6b;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; font: 16px/1.55 -apple-system, BlinkMacSystemFont,
      "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    background: var(--bg); color: var(--fg);
  }
  a { color: var(--accent-dark); }
  header.admin-nav {
    background: #1a1a1a; color: #fff; padding: 12px 24px;
    display: flex; align-items: center; gap: 20px;
  }
  header.admin-nav a { color: #fff; text-decoration: none; opacity: 0.85; }
  header.admin-nav a:hover { opacity: 1; }
  header.admin-nav .brand { font-weight: 700; letter-spacing: 0.02em; }
  header.admin-nav .spacer { flex: 1; }
  main.admin {
    max-width: 1200px; margin: 0 auto; padding: 24px;
  }
  h1 { margin: 0 0 16px 0; font-size: 1.5rem; }
  h2 { margin: 24px 0 8px 0; font-size: 1.1rem; }
  .filters {
    display: flex; gap: 12px; margin-bottom: 16px; align-items: center;
    flex-wrap: wrap;
  }
  .filters input, .filters select {
    padding: 8px 10px; border: 1px solid var(--line); border-radius: 6px;
    font: inherit; background: #fff;
  }
  .filters .grow { flex: 1; min-width: 200px; }
  .btn {
    display: inline-block; padding: 8px 14px; background: var(--accent);
    color: #fff; text-decoration: none; border: 0; border-radius: 6px;
    cursor: pointer; font: inherit; font-weight: 600;
  }
  .btn:hover { background: var(--accent-dark); }
  .btn.secondary { background: #fff; color: var(--fg); border: 1px solid var(--line); }
  .btn.secondary:hover { background: var(--surface-2); }
  table.admin-table {
    width: 100%; border-collapse: collapse; background: #fff;
    border-radius: 8px; overflow: hidden; box-shadow: 0 1px 2px rgba(0,0,0,0.04);
  }
  table.admin-table th, table.admin-table td {
    padding: 10px 12px; border-bottom: 1px solid var(--line); text-align: left;
    vertical-align: top;
  }
  table.admin-table th {
    background: var(--surface-2); font-weight: 600; font-size: 0.85rem;
    text-transform: uppercase; letter-spacing: 0.05em; color: var(--muted);
  }
  table.admin-table tr:last-child td { border-bottom: 0; }
  table.admin-table tr:hover { background: #fafafa; }
  .status {
    display: inline-block; padding: 3px 8px; border-radius: 10px;
    font-size: 0.8rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  .status.new       { background: #fff4e6; color: #a55b00; }
  .status.contacted { background: #e6f2ff; color: #0057b3; }
  .status.quoted    { background: #efe6ff; color: #5a2ea6; }
  .status.won       { background: #e6f9ee; color: #1b7a3a; }
  .status.dead      { background: #f0f0f0; color: #6b6b6b; }
  .empty {
    padding: 40px; text-align: center; color: var(--muted); background: #fff;
    border-radius: 8px; border: 1px dashed var(--line);
  }
  .toast {
    padding: 10px 14px; background: #e6f9ee; border: 1px solid #b8e6c5;
    border-radius: 6px; color: #1b7a3a; margin-bottom: 16px;
  }
  .detail {
    background: #fff; border-radius: 8px; padding: 24px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
  }
  .kv { display: grid; grid-template-columns: 160px 1fr; gap: 8px 16px; }
  .kv dt { color: var(--muted); font-weight: 600; }
  .kv dd { margin: 0; word-break: break-word; }
  .message-block {
    background: var(--surface-2); border-left: 3px solid var(--accent);
    padding: 12px 16px; border-radius: 4px; white-space: pre-wrap;
    margin: 4px 0;
  }
  form.update-form {
    margin-top: 24px; padding-top: 24px; border-top: 1px solid var(--line);
    display: flex; flex-direction: column; gap: 12px;
  }
  form.update-form label { font-weight: 600; font-size: 0.9rem; }
  form.update-form select, form.update-form textarea {
    font: inherit; padding: 8px 10px; border: 1px solid var(--line);
    border-radius: 6px; background: #fff;
  }
  form.update-form textarea { min-height: 120px; resize: vertical; }
  .email-badge {
    display: inline-block; padding: 3px 8px; border-radius: 10px;
    font-size: 0.75rem; font-weight: 600;
  }
  .email-badge.ok { background: #e6f9ee; color: #1b7a3a; }
  .email-badge.fail { background: #ffe6e6; color: #a11616; }
  .login-wrap {
    max-width: 380px; margin: 80px auto; padding: 32px;
    background: #fff; border-radius: 12px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.06);
  }
  .login-wrap h1 { text-align: center; margin-bottom: 24px; }
  .login-wrap form { display: flex; flex-direction: column; gap: 12px; }
  .login-wrap input {
    font: inherit; font-size: 1rem; padding: 12px;
    border: 1px solid var(--line); border-radius: 6px;
  }
  .login-wrap .btn { padding: 12px; font-size: 1rem; }
  .login-wrap .error {
    color: #a11616; background: #ffe6e6; padding: 10px;
    border-radius: 6px; text-align: center; font-size: 0.9rem;
  }
`;

function renderLayout(title, body, opts = {}) {
  const nav = opts.hideNav ? "" : `
    <header class="admin-nav">
      <span class="brand">Midwest CNC — Admin</span>
      <a href="/admin">Leads</a>
      <a href="/admin/case-study">Case Study</a>
      <a href="/admin/export.csv">Export CSV</a>
      <span class="spacer"></span>
      <a href="/admin/logout">Sign out</a>
    </header>`;
  return `<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>${esc(title)}</title>
<style>${BASE_CSS}</style>
</head><body>
${nav}
<main class="admin">${body}</main>
</body></html>`;
}

function renderLogin(errorMsg) {
  return renderLayout("Sign in", `
    <div class="login-wrap">
      <h1>Sign in</h1>
      ${errorMsg ? `<div class="error">${esc(errorMsg)}</div>` : ""}
      <form method="POST" action="/admin/login" autocomplete="off">
        <input type="password" name="password" placeholder="Admin password"
               required autofocus autocomplete="current-password">
        <button type="submit" class="btn">Sign in</button>
      </form>
    </div>
  `, { hideNav: true });
}

function renderConfigError(missingPassword, missingSecret) {
  const items = [];
  if (missingPassword) items.push("<code>ADMIN_PASSWORD</code>");
  if (missingSecret)   items.push("<code>SESSION_SECRET</code>");
  return renderLayout("Admin — configuration error", `
    <div class="empty">
      <p><strong>Admin is not fully configured.</strong></p>
      <p>Missing Cloudflare Worker secret${items.length > 1 ? "s" : ""}:
      ${items.join(" and ")}.</p>
      <p>Add ${items.length > 1 ? "them" : "it"} in the Cloudflare dashboard
      under Workers &amp; Pages → midwestcnc → Settings → Variables and Secrets.</p>
    </div>
  `, { hideNav: true });
}

function renderList(rows, params) {
  const statusOptions = ["", ...STATUS_OPTIONS]
    .map((s) => `<option value="${esc(s)}"${s === params.status ? " selected" : ""}>${s || "All statuses"}</option>`)
    .join("");

  const body = `
    <h1>Leads <span style="color:var(--muted);font-weight:400;">(${rows.length}${rows.length === 500 ? "+, showing latest 500" : ""})</span></h1>

    <form class="filters" method="GET" action="/admin">
      <input type="search" name="q" class="grow" value="${esc(params.q)}"
             placeholder="Search name, company, email, phone…">
      <select name="status">${statusOptions}</select>
      <button type="submit" class="btn">Filter</button>
      ${params.q || params.status ? `<a href="/admin" class="btn secondary">Reset</a>` : ""}
    </form>

    ${rows.length === 0 ? `
      <div class="empty">
        <p>No leads yet.</p>
        <p style="font-size:0.9rem;">Submissions to the quote form will appear here.</p>
      </div>
    ` : `
      <table class="admin-table">
        <thead>
          <tr>
            <th>Date</th><th>Name</th><th>Company</th><th>Phone</th>
            <th>Service</th><th>Status</th><th>Email</th><th></th>
          </tr>
        </thead>
        <tbody>
          ${rows.map((r) => `
            <tr>
              <td>${esc(formatDate(r.created_at))}</td>
              <td>${esc(r.name)}</td>
              <td>${esc(r.company)}</td>
              <td><a href="tel:${esc(r.phone)}">${esc(r.phone)}</a></td>
              <td>${esc(r.service)}</td>
              <td><span class="status ${esc(r.status)}">${esc(r.status)}</span></td>
              <td>${r.email_sent
                ? '<span class="email-badge ok">sent</span>'
                : '<span class="email-badge fail">no</span>'}</td>
              <td><a href="/admin/quote/${r.id}" class="btn secondary">View</a></td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    `}
  `;
  return renderLayout("Leads — Midwest CNC Admin", body);
}

function renderDetail(r, saved) {
  const statusOptions = STATUS_OPTIONS
    .map((s) => `<option value="${esc(s)}"${s === r.status ? " selected" : ""}>${s}</option>`)
    .join("");

  const body = `
    <p><a href="/admin">&larr; All leads</a></p>
    <h1>Quote #${r.id} &mdash; ${esc(r.name)}</h1>
    ${saved ? `<div class="toast">Changes saved.</div>` : ""}

    <div class="detail">
      <dl class="kv">
        <dt>Submitted</dt>            <dd>${esc(formatDate(r.created_at))}</dd>
        <dt>Name</dt>                 <dd>${esc(r.name)}</dd>
        <dt>Company</dt>              <dd>${esc(r.company)}</dd>
        <dt>Phone</dt>                <dd><a href="tel:${esc(r.phone)}">${esc(r.phone)}</a></dd>
        <dt>Email</dt>                <dd><a href="mailto:${esc(r.email)}">${esc(r.email)}</a></dd>
        <dt>Machine brand</dt>        <dd>${esc(r.machine_brand || "—")}</dd>
        <dt>Machine model</dt>        <dd>${esc(r.machine_model || "—")}</dd>
        <dt>Service needed</dt>       <dd>${esc(r.service)}</dd>
        <dt>Message</dt>              <dd><div class="message-block">${esc(r.message)}</div></dd>
        <dt>Email delivery</dt>       <dd>${r.email_sent
          ? '<span class="email-badge ok">sent to Ken</span>'
          : `<span class="email-badge fail">not sent</span> ${r.email_error ? `<br><small style="color:var(--muted);">${esc(r.email_error)}</small>` : ""}`}</dd>
        <dt>Source IP</dt>            <dd style="font-family:monospace;font-size:0.85rem;color:var(--muted);">${esc(r.ip || "—")}</dd>
      </dl>

      <form class="update-form" method="POST" action="/admin/quote/${r.id}">
        <label for="status-select">Status</label>
        <select id="status-select" name="status">${statusOptions}</select>

        <label for="notes-field">Notes (called, quoted, follow-up dates, etc.)</label>
        <textarea id="notes-field" name="notes" placeholder="Freeform notes on this lead…">${esc(r.notes || "")}</textarea>

        <button type="submit" class="btn">Save changes</button>
      </form>
    </div>
  `;
  return renderLayout(`Quote #${r.id} — Midwest CNC Admin`, body);
}

function formatDate(iso) {
  if (!iso) return "—";
  const d = new Date(iso);
  if (isNaN(d.getTime())) return iso;
  return d.toLocaleString("en-US", {
    year: "numeric", month: "short", day: "numeric",
    hour: "numeric", minute: "2-digit",
  });
}

// =====================================================================
// Case study data — /api/case-study.json + /admin/case-study
// =====================================================================
// Public JSON endpoint consumed by heyaaronmarketing.com case study
// pages. Data lives in D1 (gsc_daily, gsc_queries, gsc_pages, ai_daily).
// Admin page lets Aaron paste CSV exports from GSC + the AI Performance
// Overview to refresh the data until API crons are wired up.
// =====================================================================

const CASE_STUDY_SCHEMA = `
CREATE TABLE IF NOT EXISTS cs_gsc_daily (
  date TEXT PRIMARY KEY,
  clicks INTEGER NOT NULL DEFAULT 0,
  impressions INTEGER NOT NULL DEFAULT 0,
  ctr REAL NOT NULL DEFAULT 0,
  position REAL NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS cs_gsc_queries (
  query TEXT PRIMARY KEY,
  clicks INTEGER NOT NULL DEFAULT 0,
  impressions INTEGER NOT NULL DEFAULT 0,
  ctr REAL NOT NULL DEFAULT 0,
  position REAL NOT NULL DEFAULT 0,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS cs_gsc_pages (
  page TEXT PRIMARY KEY,
  clicks INTEGER NOT NULL DEFAULT 0,
  impressions INTEGER NOT NULL DEFAULT 0,
  ctr REAL NOT NULL DEFAULT 0,
  position REAL NOT NULL DEFAULT 0,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS cs_ai_daily (
  date TEXT PRIMARY KEY,
  citations INTEGER NOT NULL DEFAULT 0,
  cited_pages INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS cs_meta (
  k TEXT PRIMARY KEY,
  v TEXT,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
`;

async function ensureCaseStudySchema(env) {
  if (!env.DB) return false;
  await env.DB.exec(CASE_STUDY_SCHEMA.replace(/\n/g, " ")).catch(() => {});
  return true;
}

async function handleCaseStudyJson(env) {
  if (!env.DB) {
    return jsonResponse({ error: "database not configured" }, 503);
  }
  await ensureCaseStudySchema(env);

  const [daily, queries, pages, ai, metaRows, leadRow] = await Promise.all([
    env.DB.prepare("SELECT date, clicks, impressions, position FROM cs_gsc_daily ORDER BY date").all(),
    env.DB.prepare("SELECT query, clicks, position FROM cs_gsc_queries WHERE clicks > 0 ORDER BY clicks DESC LIMIT 25").all(),
    env.DB.prepare("SELECT page, clicks, impressions, position FROM cs_gsc_pages WHERE clicks > 0 ORDER BY clicks DESC LIMIT 25").all(),
    env.DB.prepare("SELECT date, citations, cited_pages FROM cs_ai_daily ORDER BY date").all(),
    env.DB.prepare("SELECT k, v FROM cs_meta").all(),
    env.DB.prepare("SELECT COUNT(*) AS total, SUM(email_sent) AS delivered FROM quotes").first().catch(() => null),
  ]);

  const meta = {};
  for (const row of metaRows.results || []) meta[row.k] = row.v;

  const dailyRows = daily.results || [];
  const gsc = summarizeGsc(dailyRows);
  const aiRows = ai.results || [];
  const aiSummary = summarizeAi(aiRows);

  // All-time GSC totals — the biggest case-study numbers
  const allTime = totals(dailyRows);
  const firstDate = dailyRows.length ? dailyRows[0].date : null;
  const lastDate = dailyRows.length ? dailyRows[dailyRows.length - 1].date : null;

  // Headline stats — null-safe (deltas only appear when prior window exists)
  const headline = [];
  if (aiSummary.delta.citations_pct !== null && aiSummary.delta.citations_pct !== undefined) {
    headline.push({ label: "AI citations, last 30d vs prior 30d", value: aiSummary.last30.citations, delta_pct: aiSummary.delta.citations_pct, source: "Bing AI Performance Overview" });
  }
  if (gsc.delta.clicks_pct !== null && gsc.delta.clicks_pct !== undefined) {
    headline.push({ label: "Google clicks, last 90d vs prior 90d", value: gsc.last90.clicks, delta_pct: gsc.delta.clicks_pct, source: "Google Search Console" });
  }
  headline.push(
    { label: "AI citations, all-time", value: aiSummary.total, source: "Bing AI Performance Overview" },
    { label: "Google clicks, all-time", value: allTime.clicks, source: "Google Search Console" },
    { label: "Google impressions, all-time", value: allTime.impressions, source: "Google Search Console" },
    { label: "Avg Google rank, last 90d", value: round(gsc.last90.position, 1), source: "Google Search Console" },
    { label: "Lead form submissions", value: leadRow ? (leadRow.total || 0) : 0, source: "D1 (quotes table)" },
  );

  return jsonResponse({
    schema_version: "1.1",
    slug: "midwestcnc",
    last_updated: new Date().toISOString(),
    data_as_of: meta.data_as_of || null,
    client: {
      name: "Midwest CNC Services",
      industry: "CNC machine repair · spindle rebuild · way covers",
      location: "Waterloo, Iowa",
      service_area_states: 7,
      website: "https://midwestcncservices.com",
      launched: "2026-07-06",
      bing_portfolio_topic: {
        primary: meta.bing_topic_primary || null,
        volume_range: meta.bing_topic_volume_range || null,
        queries_range: meta.bing_topic_queries_range || null,
        sites_range: meta.bing_topic_sites_range || null,
      },
    },
    headline_stats: headline,
    google_search: {
      all_time: {
        clicks: allTime.clicks,
        impressions: allTime.impressions,
        avg_position: round(allTime.position, 1),
        days: dailyRows.length,
        first_date: firstDate,
        last_date: lastDate,
      },
      last_90d: {
        clicks: gsc.last90.clicks,
        impressions: gsc.last90.impressions,
        avg_position: round(gsc.last90.position, 1),
      },
      prior_90d: {
        clicks: gsc.prior90.clicks,
        impressions: gsc.prior90.impressions,
        avg_position: round(gsc.prior90.position, 1),
      },
      delta_90d: {
        clicks_pct: gsc.delta.clicks_pct,
        impressions_pct: gsc.delta.impressions_pct,
      },
      queries_ranking: (queries.results || []).length,
      top_queries: (queries.results || []).slice(0, 25).map((q) => ({
        query: q.query, clicks: q.clicks, position: round(q.position, 1),
      })),
      top_pages: (pages.results || []).slice(0, 25).map((p) => ({
        page: p.page, clicks: p.clicks, position: round(p.position, 1),
      })),
      daily: dailyRows.map((d) => ({ date: d.date, clicks: d.clicks, impressions: d.impressions })),
      source: "Google Search Console",
      updated: meta.gsc_updated || null,
      last_error: meta.gsc_last_error || null,
    },
    ai_search: {
      all_time: {
        total_citations: aiSummary.total,
        days: aiRows.length,
        first_date: aiRows.length ? aiRows[0].date : null,
        last_date: aiRows.length ? aiRows[aiRows.length - 1].date : null,
      },
      last_30d: {
        citations: aiSummary.last30.citations,
        pages_cited: aiSummary.last30.pages,
      },
      prior_30d_citations: aiSummary.prior30,
      delta_30d_pct: aiSummary.delta.citations_pct,
      best_day: aiSummary.best_day,
      monthly: aiSummary.monthly,
      daily: aiRows.map((d) => ({ date: d.date, citations: d.citations, cited_pages: d.cited_pages })),
      source: "Bing — AI Performance Overview",
      updated: meta.ai_updated || null,
      last_error: meta.ai_last_error || null,
    },
    leads: {
      total_submissions: leadRow ? (leadRow.total || 0) : 0,
      emails_delivered: leadRow ? (leadRow.delivered || 0) : 0,
      delivery_rate_pct: leadRow && leadRow.total ? Math.round((leadRow.delivered / leadRow.total) * 100) : null,
      source: "Cloudflare D1 (quotes table)",
    },
    site_structure: {
      pages: 297,
      schema_nodes: 1768,
      faq_qa_pairs: 442,
      insight_articles_auto_drafted: 22,
      image_size_savings_pct: 86,
      broken_links: 0,
    },
    capabilities_shown: [
      "Durable → Cloudflare Workers rebuild",
      "D1 lead database + admin UI with HMAC session cookies",
      "GitHub Actions weekly AI-drafted articles with 12 quality gates",
      "llms.txt + 442 FAQ Q&A pairs + 1,768 schema nodes",
      "Full form pipeline (Turnstile + Resend + D1 + Reply-To routing)",
      "IndexNow protocol pings Bing/Yandex on every content refresh",
    ],
  });
}

function jsonResponse(obj, status = 200) {
  return new Response(JSON.stringify(obj, null, 2), {
    status,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "public, max-age=300, s-maxage=300",
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, OPTIONS",
    },
  });
}

function round(n, dp) {
  if (n === null || n === undefined || !isFinite(n)) return null;
  const f = Math.pow(10, dp);
  return Math.round(n * f) / f;
}

function summarizeGsc(rows) {
  if (!rows.length) {
    return {
      last90:  { clicks: 0, impressions: 0, position: 0 },
      prior90: { clicks: 0, impressions: 0, position: 0 },
      delta:   { clicks_pct: 0, impressions_pct: 0 },
    };
  }
  const last90 = totals(rows.slice(-90));
  const prior90 = totals(rows.slice(-180, -90));
  return {
    last90, prior90,
    delta: {
      clicks_pct: prior90.clicks ? Math.round(((last90.clicks - prior90.clicks) / prior90.clicks) * 100) : null,
      impressions_pct: prior90.impressions ? Math.round(((last90.impressions - prior90.impressions) / prior90.impressions) * 100) : null,
    },
  };
}

function totals(rows) {
  if (!rows.length) return { clicks: 0, impressions: 0, position: 0 };
  let c = 0, i = 0, p = 0;
  for (const r of rows) { c += r.clicks; i += r.impressions; p += r.position; }
  return { clicks: c, impressions: i, position: p / rows.length };
}

function summarizeAi(rows) {
  if (!rows.length) {
    return {
      total: 0,
      last30: { citations: 0, pages: 0 },
      prior30: 0,
      delta: { citations_pct: null },
      best_day: null,
      monthly: [],
    };
  }
  const last30 = rows.slice(-30);
  const prior30 = rows.slice(-60, -30);
  const sumC = (rs) => rs.reduce((a, r) => a + r.citations, 0);
  const total = sumC(rows);
  const l30 = sumC(last30);
  const p30 = sumC(prior30);
  const bestDay = rows.reduce((best, r) => (r.citations > (best?.citations || 0) ? r : best), null);
  const byMonth = {};
  for (const r of rows) {
    const m = r.date.slice(0, 7);
    if (!byMonth[m]) byMonth[m] = { month: m, citations: 0, days: 0 };
    byMonth[m].citations += r.citations;
    byMonth[m].days += 1;
  }
  return {
    total,
    last30: { citations: l30, pages: Math.max(0, ...last30.map((r) => r.cited_pages)) },
    prior30: p30,
    delta: { citations_pct: p30 ? Math.round(((l30 - p30) / p30) * 100) : null },
    best_day: bestDay
      ? { date: bestDay.date, citations: bestDay.citations, cited_pages: bestDay.cited_pages }
      : null,
    monthly: Object.values(byMonth),
  };
}

// ---------- Admin case-study page ----------

async function handleCaseStudyAdminPage(env) {
  if (!env.DB) {
    return htmlResponse(renderLayout("Case Study", `<p>DB not configured.</p>`));
  }
  await ensureCaseStudySchema(env);
  const [daily, ai, meta] = await Promise.all([
    env.DB.prepare("SELECT COUNT(*) AS n, MIN(date) AS first, MAX(date) AS last FROM cs_gsc_daily").first(),
    env.DB.prepare("SELECT COUNT(*) AS n, MIN(date) AS first, MAX(date) AS last FROM cs_ai_daily").first(),
    env.DB.prepare("SELECT k, v FROM cs_meta").all(),
  ]);
  const metaMap = {};
  for (const r of meta.results || []) metaMap[r.k] = r.v;

  const body = `
    <p><a href="/admin">&larr; All leads</a></p>
    <h1>Case Study Data</h1>
    <p style="color:var(--muted);">
      Powers <code>/api/case-study.json</code>. Weekly cron (Mon 7 AM Central)
      pulls GSC + Bing automatically. Paste CSVs below for one-off AI
      Overview refreshes or manual catch-up.
    </p>

    <div class="detail">
      <h2>Current data</h2>
      <dl class="kv">
        <dt>GSC daily rows</dt>   <dd>${daily?.n || 0} ${daily?.first ? `(${daily.first} → ${daily.last})` : ""}</dd>
        <dt>AI daily rows</dt>    <dd>${ai?.n || 0} ${ai?.first ? `(${ai.first} → ${ai.last})` : ""}</dd>
        <dt>GSC last updated</dt> <dd>${esc(metaMap.gsc_updated || "never")} ${metaMap.gsc_last_error ? `<span class="email-badge fail">error</span> <small style="color:var(--muted);">${esc(metaMap.gsc_last_error)}</small>` : ""}</dd>
        <dt>Bing last updated</dt><dd>${esc(metaMap.bing_updated || "never")} ${metaMap.bing_last_error ? `<span class="email-badge fail">error</span> <small style="color:var(--muted);">${esc(metaMap.bing_last_error)}</small>` : ""}</dd>
        <dt>Data as of</dt>       <dd>${esc(metaMap.data_as_of || "never")}</dd>
        <dt>Live JSON</dt>        <dd><a href="/api/case-study.json" target="_blank">/api/case-study.json</a></dd>
      </dl>

      <form method="POST" action="/admin/case-study/refresh" style="margin-top:16px;">
        <button type="submit" class="btn">Refresh GSC + Bing now</button>
        <small style="color:var(--muted);margin-left:12px;">Pulls latest 90 days. Runs automatically every Monday.</small>
      </form>

      <form class="update-form" method="POST" action="/admin/case-study" enctype="multipart/form-data">
        <label for="csv_type">Which CSV is this?</label>
        <select id="csv_type" name="csv_type">
          <option value="gsc_chart">GSC — Chart.csv (daily clicks/impressions/CTR/position)</option>
          <option value="gsc_queries">GSC — Queries.csv (query / clicks / impressions / CTR / position)</option>
          <option value="gsc_pages">GSC — Pages.csv (page / clicks / impressions / CTR / position)</option>
          <option value="ai_overview">AI Performance Overview (Date / Citations / Cited Pages)</option>
        </select>

        <label for="csv_text">Paste CSV content here:</label>
        <textarea id="csv_text" name="csv_text" placeholder="Copy the CSV file contents and paste here.&#10;First row = headers, same as GSC exports."></textarea>

        <button type="submit" class="btn">Upload &amp; refresh</button>
      </form>
    </div>
  `;
  return htmlResponse(renderLayout("Case Study — Admin", body));
}

async function handleCaseStudyUpload(request, env, url) {
  await ensureCaseStudySchema(env);
  const form = await request.formData().catch(() => null);
  if (!form) return new Response("Bad request", { status: 400 });
  const csvType = (form.get("csv_type") || "").toString();
  const csvText = (form.get("csv_text") || "").toString().trim();
  if (!csvText) {
    return htmlResponse(renderLayout("Case Study", `<p>No CSV content.</p><p><a href="/admin/case-study">Back</a></p>`));
  }

  const rows = parseCsv(csvText);
  if (rows.length < 2) {
    return htmlResponse(renderLayout("Case Study", `<p>CSV had no data rows.</p><p><a href="/admin/case-study">Back</a></p>`));
  }
  const header = rows[0].map((h) => h.toLowerCase().trim());
  const dataRows = rows.slice(1);
  let inserted = 0;

  if (csvType === "gsc_chart") {
    const stmts = dataRows
      .filter((r) => r[0])
      .map((r) => env.DB.prepare(
        "INSERT INTO cs_gsc_daily (date, clicks, impressions, ctr, position) VALUES (?, ?, ?, ?, ?) " +
        "ON CONFLICT(date) DO UPDATE SET clicks=excluded.clicks, impressions=excluded.impressions, ctr=excluded.ctr, position=excluded.position"
      ).bind(r[0], intOr0(r[1]), intOr0(r[2]), pctOr0(r[3]), floatOr0(r[4])));
    await env.DB.batch(stmts);
    inserted = stmts.length;
  } else if (csvType === "gsc_queries") {
    await env.DB.exec("DELETE FROM cs_gsc_queries");
    const stmts = dataRows
      .filter((r) => r[0])
      .map((r) => env.DB.prepare(
        "INSERT OR REPLACE INTO cs_gsc_queries (query, clicks, impressions, ctr, position) VALUES (?, ?, ?, ?, ?)"
      ).bind(r[0], intOr0(r[1]), intOr0(r[2]), pctOr0(r[3]), floatOr0(r[4])));
    await env.DB.batch(stmts);
    inserted = stmts.length;
  } else if (csvType === "gsc_pages") {
    await env.DB.exec("DELETE FROM cs_gsc_pages");
    const stmts = dataRows
      .filter((r) => r[0])
      .map((r) => env.DB.prepare(
        "INSERT OR REPLACE INTO cs_gsc_pages (page, clicks, impressions, ctr, position) VALUES (?, ?, ?, ?, ?)"
      ).bind(r[0], intOr0(r[1]), intOr0(r[2]), pctOr0(r[3]), floatOr0(r[4])));
    await env.DB.batch(stmts);
    inserted = stmts.length;
  } else if (csvType === "ai_overview") {
    const stmts = dataRows
      .filter((r) => r[0])
      .map((r) => env.DB.prepare(
        "INSERT INTO cs_ai_daily (date, citations, cited_pages) VALUES (?, ?, ?) " +
        "ON CONFLICT(date) DO UPDATE SET citations=excluded.citations, cited_pages=excluded.cited_pages"
      ).bind(normalizeDate(r[0]), intOr0(r[1]), intOr0(r[2])));
    await env.DB.batch(stmts);
    inserted = stmts.length;
  } else {
    return new Response("Unknown csv_type", { status: 400 });
  }

  const now = new Date().toISOString();
  const metaKey = csvType.startsWith("gsc_") ? "gsc_updated" : "ai_updated";
  await env.DB.prepare(
    "INSERT INTO cs_meta (k, v) VALUES (?, ?) ON CONFLICT(k) DO UPDATE SET v=excluded.v, updated_at=CURRENT_TIMESTAMP"
  ).bind(metaKey, now).run();
  await env.DB.prepare(
    "INSERT INTO cs_meta (k, v) VALUES ('data_as_of', ?) ON CONFLICT(k) DO UPDATE SET v=excluded.v, updated_at=CURRENT_TIMESTAMP"
  ).bind(now).run();

  return new Response(null, {
    status: 303,
    headers: { Location: new URL(`/admin/case-study?uploaded=${inserted}`, url).toString() },
  });
}

function parseCsv(text) {
  // Minimal RFC-4180 parser: handles quoted fields with embedded commas/quotes.
  const rows = [];
  let row = [], field = "", inQuotes = false, i = 0;
  while (i < text.length) {
    const c = text[i];
    if (inQuotes) {
      if (c === '"' && text[i + 1] === '"') { field += '"'; i += 2; continue; }
      if (c === '"') { inQuotes = false; i++; continue; }
      field += c; i++; continue;
    }
    if (c === '"') { inQuotes = true; i++; continue; }
    if (c === ',') { row.push(field); field = ""; i++; continue; }
    if (c === '\r') { i++; continue; }
    if (c === '\n') { row.push(field); rows.push(row); row = []; field = ""; i++; continue; }
    field += c; i++;
  }
  if (field.length || row.length) { row.push(field); rows.push(row); }
  return rows.filter((r) => r.length > 1 || (r.length === 1 && r[0]));
}

function intOr0(v) { const n = parseInt(String(v || "").replace(/,/g, ""), 10); return isNaN(n) ? 0 : n; }
function floatOr0(v) { const n = parseFloat(String(v || "").replace(/,/g, "")); return isNaN(n) ? 0 : n; }
function pctOr0(v) {
  const s = String(v || "").replace(/,/g, "").replace("%", "").trim();
  const n = parseFloat(s);
  return isNaN(n) ? 0 : (n > 1 ? n / 100 : n);
}
function normalizeDate(v) {
  // Accepts "YYYY-MM-DD", "M/D/YYYY", "M/D/YYYY 12:00:00 AM" → YYYY-MM-DD
  const s = String(v || "").trim().split(" ")[0];
  if (/^\d{4}-\d{2}-\d{2}$/.test(s)) return s;
  const m = s.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})$/);
  if (m) return `${m[3]}-${m[1].padStart(2, "0")}-${m[2].padStart(2, "0")}`;
  return s;
}

// =====================================================================
// Case-study refresh — pulls GSC + Bing via their APIs on cron
// =====================================================================
// Called by scheduled() weekly, and by POST /admin/case-study/refresh
// for manual triggering. Each source is independent — one failing does
// not block the other. Errors are written to cs_meta.last_error_<src>
// so the admin page can show them.
// =====================================================================

const GSC_PROPERTY = "sc-domain:midwestcncservices.com";
const BING_SITE_URL = "https://midwestcncservices.com";

// IndexNow — Microsoft/Bing + Yandex + others' push-crawl protocol.
// Instead of waiting for crawlers to discover new/updated URLs, we
// POST a list of URLs to the IndexNow API and participating engines
// re-crawl within minutes. Key verification file lives at
// public/<KEY>.txt and must return the key with no whitespace or BOM.
const INDEXNOW_KEY = "4f95325123d5ab94c51aeb25a7a78a21";
const INDEXNOW_HOST = "midwestcncservices.com";

async function runCaseStudyRefresh(env, meta = {}) {
  await ensureCaseStudySchema(env);
  const results = { source: meta.source || "manual", started: new Date().toISOString() };

  // Rate-limit guard: refuse to refresh if we ran successfully in the
  // last 60 minutes. Prevents Bing ThrottleIP + IndexNow 429 errors
  // from someone clicking "Refresh now" repeatedly. Cron trigger
  // bypasses this (source === "cron") since it fires weekly.
  if (meta.source !== "cron") {
    const lastRow = await env.DB.prepare(
      "SELECT v FROM cs_meta WHERE k = 'last_refresh_ok_at'"
    ).first();
    if (lastRow && lastRow.v) {
      const lastMs = Date.parse(lastRow.v);
      const ageMin = Math.floor((Date.now() - lastMs) / 60000);
      if (ageMin < 60) {
        results.skipped = `rate-limited: last successful refresh was ${ageMin} min ago (60 min minimum)`;
        results.retry_after_min = 60 - ageMin;
        results.finished = new Date().toISOString();
        return results;
      }
    }
  }

  try {
    const g = await pullGsc(env);
    results.gsc = g;
    await setMeta(env, "gsc_updated", new Date().toISOString());
    await setMeta(env, "gsc_last_error", "");
  } catch (e) {
    results.gsc = { error: String(e && e.message || e) };
    await setMeta(env, "gsc_last_error", results.gsc.error);
    console.log("GSC pull failed:", results.gsc.error);
  }

  try {
    const b = await pullBing(env);
    results.bing = b;
    await setMeta(env, "bing_updated", new Date().toISOString());
    await setMeta(env, "bing_last_error", "");
  } catch (e) {
    results.bing = { error: String(e && e.message || e) };
    await setMeta(env, "bing_last_error", results.bing.error);
    console.log("Bing pull failed:", results.bing.error);
  }

  try {
    const inx = await pingIndexNow(env);
    results.indexnow = inx;
    await setMeta(env, "indexnow_updated", new Date().toISOString());
    await setMeta(env, "indexnow_last_error", "");
  } catch (e) {
    results.indexnow = { error: String(e && e.message || e) };
    await setMeta(env, "indexnow_last_error", results.indexnow.error);
    console.log("IndexNow push failed:", results.indexnow.error);
  }

  await setMeta(env, "data_as_of", new Date().toISOString());
  // Only mark a successful refresh when GSC actually pulled (the money
  // source). Bing or IndexNow throttles don't block subsequent retries.
  if (results.gsc && !results.gsc.error) {
    await setMeta(env, "last_refresh_ok_at", new Date().toISOString());
  }
  results.finished = new Date().toISOString();
  return results;
}

// ---------- IndexNow ----------

async function pingIndexNow(env) {
  // Parse the sitemap at /sitemap.xml and push every URL to IndexNow.
  // Bing + Yandex + Seznam.cz + Naver all participate and re-crawl
  // within minutes. Google does not participate yet — GSC's own
  // "URL inspection" tool is Google's equivalent (manual only).
  const sitemapReq = new Request(`https://${INDEXNOW_HOST}/sitemap.xml`, { method: "GET" });
  const smResp = await env.ASSETS.fetch(sitemapReq);
  if (!smResp.ok) {
    throw new Error(`sitemap fetch failed: ${smResp.status}`);
  }
  const xml = await smResp.text();
  const urls = Array.from(xml.matchAll(/<loc>([^<]+)<\/loc>/g)).map((m) => m[1]);
  if (!urls.length) return { skipped: "no URLs in sitemap" };

  const resp = await fetch("https://api.indexnow.org/IndexNow", {
    method: "POST",
    headers: { "Content-Type": "application/json; charset=utf-8" },
    body: JSON.stringify({
      host: INDEXNOW_HOST,
      key: INDEXNOW_KEY,
      keyLocation: `https://${INDEXNOW_HOST}/${INDEXNOW_KEY}.txt`,
      urlList: urls,
    }),
  });
  // IndexNow accepted codes: 200 (ok), 202 (accepted, processing),
  // 422 (invalid URLs — partial success). 400+ else is an error.
  if (resp.status === 200 || resp.status === 202) {
    return { urls_submitted: urls.length, status: resp.status };
  }
  const body = await resp.text().catch(() => "");
  throw new Error(`IndexNow HTTP ${resp.status}: ${body.slice(0, 200)}`);
}

async function setMeta(env, k, v) {
  await env.DB.prepare(
    "INSERT INTO cs_meta (k, v) VALUES (?, ?) ON CONFLICT(k) DO UPDATE SET v=excluded.v, updated_at=CURRENT_TIMESTAMP"
  ).bind(k, v).run();
}

// ---------- GSC ----------

async function pullGsc(env) {
  if (!env.GSC_SERVICE_ACCOUNT_JSON) {
    return { skipped: "GSC_SERVICE_ACCOUNT_JSON not set" };
  }
  const sa = JSON.parse(env.GSC_SERVICE_ACCOUNT_JSON);
  const token = await mintGoogleAccessToken(sa, "https://www.googleapis.com/auth/webmasters.readonly");

  // Pull the full 16-month window the GSC API allows (480 days to
  // stay well under the 490-day ceiling). cs_gsc_daily upserts, so
  // historic rows outside the window are preserved.
  const today = new Date();
  const start = new Date(today.getTime() - 480 * 86400000);
  const fmt = (d) => d.toISOString().slice(0, 10);
  const startDate = fmt(start);
  const endDate = fmt(today);

  const daily = await gscQuery(token, { startDate, endDate, dimensions: ["date"], rowLimit: 500 });
  const queries = await gscQuery(token, { startDate, endDate, dimensions: ["query"], rowLimit: 1000 });
  const pages = await gscQuery(token, { startDate, endDate, dimensions: ["page"], rowLimit: 1000 });

  // Upsert daily (preserves older rows outside the 90-day window)
  if (daily.rows?.length) {
    const stmts = daily.rows.map((r) => env.DB.prepare(
      "INSERT INTO cs_gsc_daily (date, clicks, impressions, ctr, position) VALUES (?, ?, ?, ?, ?) " +
      "ON CONFLICT(date) DO UPDATE SET clicks=excluded.clicks, impressions=excluded.impressions, ctr=excluded.ctr, position=excluded.position"
    ).bind(r.keys[0], r.clicks, r.impressions, r.ctr, r.position));
    await env.DB.batch(stmts);
  }

  // Replace queries + pages (they're a point-in-time top-N snapshot)
  if (queries.rows?.length) {
    await env.DB.exec("DELETE FROM cs_gsc_queries");
    const stmts = queries.rows.map((r) => env.DB.prepare(
      "INSERT INTO cs_gsc_queries (query, clicks, impressions, ctr, position) VALUES (?, ?, ?, ?, ?)"
    ).bind(r.keys[0], r.clicks, r.impressions, r.ctr, r.position));
    await env.DB.batch(stmts);
  }
  if (pages.rows?.length) {
    await env.DB.exec("DELETE FROM cs_gsc_pages");
    const stmts = pages.rows.map((r) => env.DB.prepare(
      "INSERT INTO cs_gsc_pages (page, clicks, impressions, ctr, position) VALUES (?, ?, ?, ?, ?)"
    ).bind(r.keys[0], r.clicks, r.impressions, r.ctr, r.position));
    await env.DB.batch(stmts);
  }

  return {
    daily_rows: daily.rows?.length || 0,
    query_rows: queries.rows?.length || 0,
    page_rows: pages.rows?.length || 0,
    window: `${startDate} → ${endDate}`,
  };
}

async function gscQuery(token, body) {
  const url =
    "https://searchconsole.googleapis.com/webmasters/v3/sites/" +
    encodeURIComponent(GSC_PROPERTY) + "/searchAnalytics/query";
  const resp = await fetch(url, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!resp.ok) {
    const t = await resp.text();
    throw new Error(`GSC ${resp.status}: ${t.slice(0, 300)}`);
  }
  return resp.json();
}

async function mintGoogleAccessToken(sa, scope) {
  const now = Math.floor(Date.now() / 1000);
  const header = { alg: "RS256", typ: "JWT" };
  const claims = {
    iss: sa.client_email,
    scope,
    aud: "https://oauth2.googleapis.com/token",
    exp: now + 3600,
    iat: now,
  };
  const b64url = (bytes) => b64UrlEncode(typeof bytes === "string" ? new TextEncoder().encode(bytes) : bytes);
  const hb = b64url(JSON.stringify(header));
  const cb = b64url(JSON.stringify(claims));
  const signingInput = `${hb}.${cb}`;

  // Import PEM private key
  const pem = sa.private_key
    .replace("-----BEGIN PRIVATE KEY-----", "")
    .replace("-----END PRIVATE KEY-----", "")
    .replace(/\s+/g, "");
  const der = Uint8Array.from(atob(pem), (c) => c.charCodeAt(0));
  const key = await crypto.subtle.importKey(
    "pkcs8", der, { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" }, false, ["sign"],
  );
  const sigBytes = new Uint8Array(await crypto.subtle.sign("RSASSA-PKCS1-v1_5", key, new TextEncoder().encode(signingInput)));
  const jwt = `${signingInput}.${b64url(sigBytes)}`;

  const tokResp = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      grant_type: "urn:ietf:params:oauth:grant-type:jwt-bearer",
      assertion: jwt,
    }).toString(),
  });
  if (!tokResp.ok) {
    throw new Error(`OAuth exchange failed ${tokResp.status}: ${(await tokResp.text()).slice(0, 300)}`);
  }
  const tok = await tokResp.json();
  return tok.access_token;
}

// ---------- Bing ----------

async function pullBing(env) {
  if (!env.BING_API_KEY) {
    return { skipped: "BING_API_KEY not set" };
  }
  // Bing Webmaster Tools API v1. GetRankAndTrafficStats returns daily
  // clicks + impressions for the site. GetQueryStats returns top queries.
  const base =
    "https://ssl.bing.com/webmaster/api.svc/json/" +
    "GetRankAndTrafficStats?siteUrl=" + encodeURIComponent(BING_SITE_URL) +
    "&apikey=" + encodeURIComponent(env.BING_API_KEY);
  const resp = await fetch(base);
  if (!resp.ok) {
    throw new Error(`Bing ${resp.status}: ${(await resp.text()).slice(0, 300)}`);
  }
  const data = await resp.json();
  const stats = (data && data.d) || [];
  // Upsert into cs_bing_daily (table created lazily below)
  await env.DB.exec(
    "CREATE TABLE IF NOT EXISTS cs_bing_daily (" +
    "date TEXT PRIMARY KEY, clicks INTEGER NOT NULL DEFAULT 0, " +
    "impressions INTEGER NOT NULL DEFAULT 0, position REAL NOT NULL DEFAULT 0);"
  );
  if (stats.length) {
    const stmts = stats.map((s) => {
      // Bing returns "Date":"/Date(1234567890000)/" epoch-ms
      const ms = parseInt(String(s.Date).replace(/[^0-9]/g, ""), 10);
      const date = new Date(ms).toISOString().slice(0, 10);
      return env.DB.prepare(
        "INSERT INTO cs_bing_daily (date, clicks, impressions, position) VALUES (?, ?, ?, ?) " +
        "ON CONFLICT(date) DO UPDATE SET clicks=excluded.clicks, impressions=excluded.impressions, position=excluded.position"
      ).bind(date, s.Clicks || 0, s.Impressions || 0, s.AvgImpressionPosition || 0);
    });
    await env.DB.batch(stmts);
  }
  return { bing_daily_rows: stats.length };
}

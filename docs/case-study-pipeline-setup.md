# Case-Study Pipeline — Portable Setup Guide

A runbook for replicating the full SEO/AEO + case-study measurement
pipeline that lives on `midwestcncservices.com` onto a new client site.

This guide is hand-off ready: paste it to a Claude Code session with
access to the new client's repo, and work through it top to bottom.
Reference implementation lives at `github.com/heyaaronmarketing/midwestcnc`.

---

## What you're building

A single Cloudflare Worker that:

1. **Serves the static site** (via ASSETS binding)
2. **Handles form submissions** → D1 + email (optional, skip if no form)
3. **Pulls weekly stats from Google Search Console** via service-account OAuth
4. **Pulls weekly stats from Bing Webmaster Tools** via REST API
5. **Pings IndexNow** on every refresh to push URL updates to Bing + Yandex
6. **Logs server-side traffic** (AI bot crawls + AI engine referrals) that GA4 is blind to
7. **Exposes `/api/case-study.json`** — public endpoint that heyaaronmarketing.com case-study pages fetch
8. **Provides an admin UI** at `/admin` with password login, HMAC session cookies, lead list, CSV upload for AI Overview data, "Refresh now" button

Plus a weekly cron that fires the pulls automatically.

---

## Prerequisites — what the client needs before you start

| | Required | Why |
|---|---|---|
| Cloudflare account with Workers paid plan OR Free tier | ✓ | Free tier is fine for < 100k requests/day |
| Site deployed on Cloudflare Workers + Static Assets | ✓ | OR Cloudflare Pages — same patterns work |
| GitHub repo with Cloudflare Git integration | ✓ | So push-to-deploy works |
| Site verified in Google Search Console | ✓ | For GSC data pull |
| Site verified in Bing Webmaster Tools | ✓ | For Bing data pull + IndexNow |
| Google account for creating a Google Cloud project | ✓ | For service account (GSC API) |
| Resend account | only if form | For transactional email |

---

## Phase 1 — Cloudflare prep

### 1.1 Create a D1 database

```bash
# From a terminal with wrangler installed:
npx wrangler d1 create <client-slug>-case-study
# → copies out a database_id like bf690c6e-eca6-4033-b1de-db5d375c5ffb
```

OR via the dashboard: **Workers & Pages → D1 → Create database**.

Name it `<client-slug>-case-study`. Save the database ID.

### 1.2 Wire the binding

Edit `public/wrangler.jsonc` (or wherever the Worker root sits):

```jsonc
{
  "$schema": "node_modules/wrangler/config-schema.json",
  "name": "<client-slug>",
  "compatibility_date": "2026-05-26",
  "main": "worker.js",
  "observability": { "enabled": true },
  "assets": { "directory": ".", "binding": "ASSETS" },
  "compatibility_flags": ["nodejs_compat"],
  "d1_databases": [
    {
      "binding": "DB",
      "database_name": "<client-slug>-case-study",
      "database_id": "<paste-database-id-here>"
    }
  ],
  "triggers": {
    "crons": [
      "0 13 * * 1"
    ]
  }
}
```

**If the Worker is deployed by the old Pages-style convention**, you'll also need `public/.assetsignore`:

```
.git
.gitignore
.assetsignore
worker.js
wrangler.jsonc
```

### 1.3 Required secrets

Set these in the Cloudflare dashboard → **Workers & Pages → `<worker-name>` → Settings → Variables and Secrets**:

| Secret name | Required for | Value |
|---|---|---|
| `GSC_SERVICE_ACCOUNT_JSON` | GSC cron | Full JSON of the Google Cloud service account key |
| `BING_API_KEY` | Bing cron | 32-char hex key from Bing Webmaster → Settings → API Access |
| `ADMIN_PASSWORD` | Admin UI | Strong password you'll use to log into `/admin` |
| `SESSION_SECRET` | Admin UI | 64+ random bytes — use `openssl rand -hex 32` |
| `RESEND_API_KEY` | Form (if used) | From resend.com/api-keys |
| `TURNSTILE_SECRET` | Form captcha (optional) | From Cloudflare Turnstile widget settings |

You can set secrets via API (faster for multiple sites):

```bash
curl -sS -X PUT \
  -H "Authorization: Bearer $CF_TOKEN" \
  -H "Content-Type: application/json" \
  "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/workers/scripts/<worker-name>/secrets" \
  --data '{"name":"GSC_SERVICE_ACCOUNT_JSON","text":"<paste-json-here>","type":"secret_text"}'
```

---

## Phase 2 — The Worker code

Full working source: **[midwestcnc/public/worker.js](https://github.com/heyaaronmarketing/midwestcnc/blob/main/public/worker.js)**.

Copy that file verbatim into the new client's repo as `worker.js`. Then make these site-specific edits:

### 2.1 Top-of-file constants

```js
// Form routing — change if the client has different email expectations
const SUCCESS_PATH = "/get-a-quote/thank-you/";
const ERROR_PATH = "/get-a-quote/";
const PHONE = "<client-phone-number>";
const REQUIRED_FIELDS = ["name", "company", "phone", "email", "service", "message"];

// Analytics sources
const GSC_PROPERTY = "sc-domain:<client-domain>.com";    // sc-domain: for domain-verified; https://... for URL-verified
const BING_SITE_URL = "https://<client-domain>.com";

// IndexNow — generate ONCE per domain (see Phase 3.3)
const INDEXNOW_KEY = "<32-char-hex-key>";
const INDEXNOW_HOST = "<client-domain>.com";
```

### 2.2 handleCaseStudyJson()

Edit the `client` object inside the JSON response to match the new client:

```js
client: {
  name: "<Client Business Name>",
  industry: "<e.g. roofing · gutters · siding>",
  location: "<City, State>",
  service_area_states: <number>,
  website: "https://<client-domain>.com",
  launched: "<YYYY-MM-DD>",
  bing_portfolio_topic: {
    primary: meta.bing_topic_primary || null,
    volume_range: meta.bing_topic_volume_range || null,
    queries_range: meta.bing_topic_queries_range || null,
    sites_range: meta.bing_topic_sites_range || null,
  },
},
// ... further down:
site_structure: {
  pages: <approx>, schema_nodes: <approx>, faq_qa_pairs: <approx>,
  // measure these for the actual client site
},
capabilities_shown: [
  // list 3-5 specific capabilities shown by this client's site
],
```

Everything else (query logic, bot classification, admin UI, CSV upload, cron handler, IndexNow ping, rate-limit guard) works unchanged across clients.

### 2.3 Email sender (if forms used)

Change the Reply-To routing:

```js
const fromEmail = env.FROM_EMAIL || "<Client Name> Quote Form <quotes@<client-domain>.com>";
const recipients = (env.NOTIFY_EMAIL || "<client-owner-email>").split(",").map((s) => s.trim());
```

---

## Phase 3 — External service setup

### 3.1 Google Search Console service account

1. **[console.cloud.google.com](https://console.cloud.google.com)** → New Project → name it `<client>-case-studies`
2. **APIs & Services → Library** → search `Search Console API` → **Enable**
3. **APIs & Services → Credentials** → **+ Create Credentials** → **Service Account**
4. Name: `gsc-reader` → Create → skip the two "grant access" steps → Done
5. Click the service account row → **Keys** tab → **Add Key** → **Create new key** → **JSON** → Create
6. Downloads a JSON file. **This is the GSC_SERVICE_ACCOUNT_JSON secret.** Save its full contents.
7. Open the JSON, copy the `client_email` field (looks like `gsc-reader@<project>.iam.gserviceaccount.com`)
8. **[search.google.com/search-console](https://search.google.com/search-console)** → pick the property → **Settings → Users and permissions → Add user**
9. Paste the `client_email` → permission **Owner** (required for API access, not just Full)
10. Push the full JSON content as the `GSC_SERVICE_ACCOUNT_JSON` Worker secret.

### 3.2 Bing Webmaster Tools API key

1. **[bing.com/webmasters](https://bing.com/webmasters)** → sign in with the Microsoft account that owns the property
2. Click the site in the list
3. Top-right gear icon → **API Access** → **Generate** → copy the 32-char hex key
4. Push as the `BING_API_KEY` Worker secret.

### 3.3 Generate the IndexNow key

```bash
# Deterministic (recommended — reproducible if you lose track):
python3 -c "import hashlib; print(hashlib.sha256('<client-zone-id>-indexnow-v1'.encode()).hexdigest()[:32])"

# Or random:
openssl rand -hex 16
```

That 32-char hex string is the `INDEXNOW_KEY`. Two places it needs to appear:

1. **In the Worker constant** (`const INDEXNOW_KEY = "..."`)
2. **As a verification file** at `public/<the-key>.txt` containing exactly the key bytes (no whitespace, no BOM):

```bash
printf '%s' "<the-key>" > public/<the-key>.txt
```

Commit both. IndexNow verifies ownership by fetching `https://<domain>/<the-key>.txt` and comparing content to what was POSTed.

---

## Phase 4 — Verify end-to-end

After deploying:

```bash
# 1. GSC + Bing cron trigger (log into /admin/case-study, click "Refresh now")
# OR via API:
curl -X POST https://<client-domain>.com/admin/case-study/refresh \
  -H "Cookie: <admin-session-cookie>"

# 2. Verify JSON endpoint returns data
curl https://<client-domain>.com/api/case-study.json | jq '.google_search.all_time'

# 3. Verify IndexNow key file serves
curl https://<client-domain>.com/<the-key>.txt
# Should return exactly the 32-char hex key, no whitespace

# 4. Verify admin login works
curl -sI https://<client-domain>.com/admin/login
# Should return 200
```

---

## Phase 5 — Site-wide SEO/AEO patterns to apply

These aren't Worker code — they're patterns that need to be applied in the site's HTML generation (whether that's a Python generator, Astro, Next.js, etc.).

### 5.1 robots.txt — explicit AI bot allowlist

Generate `public/robots.txt`:

```
# Default: allow all
User-agent: *
Allow: /

# AI crawlers — explicit allowlist (trust signal for bots that check)
User-agent: GPTBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: OAI-SearchBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Claude-Web
Allow: /

User-agent: anthropic-ai
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Perplexity-User
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: GoogleOther
Allow: /

User-agent: Applebot-Extended
Allow: /

User-agent: meta-externalagent
Allow: /

User-agent: FacebookBot
Allow: /

User-agent: Amazonbot
Allow: /

User-agent: cohere-ai
Allow: /

User-agent: CCBot
Allow: /

User-agent: Bytespider
Allow: /

User-agent: MistralAI-User
Allow: /

User-agent: Diffbot
Allow: /

Sitemap: https://<client-domain>.com/sitemap.xml
```

### 5.2 llms.txt + llms-full.txt

**`llms.txt`** at the site root (per [llmstxt.org](https://llmstxt.org)) — the brief index. Lists hub pages and authoritative starting points.

**`llms-full.txt`** at the site root — the long-form content index. Every FAQPage Q&A in plain text with source URLs.

Generator pattern (works with any static site that emits HTML):

```python
# Walk every HTML file, extract FAQPage schema JSON-LD blocks,
# emit as plain text with Q: / A: pairs, grouped by page.
# Reference implementation: midwestcnc/scripts/generate_site_shell.py
# → see gen_llms_full_txt()
```

### 5.3 Trailing-slash 307 → 301

Workers Static Assets defaults non-slashed HTML URLs to a **307 Temporary Redirect** to the slashed version. Google treats 307 as non-permanent → does NOT consolidate ranking signals → you end up with duplicate URLs ranking separately.

Fix in `worker.js` dispatcher, BEFORE `env.ASSETS.fetch(request)`:

```js
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
```

### 5.4 Security headers

`public/_headers`:

```
/*
  X-Content-Type-Options: nosniff
  X-Frame-Options: SAMEORIGIN
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: geolocation=(), microphone=(), camera=()
  Content-Security-Policy-Report-Only: default-src 'self'; script-src 'self' 'unsafe-inline' <per-site-allowlist>; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; object-src 'none'; base-uri 'self'; form-action 'self'

/assets/*
  Cache-Control: public, max-age=604800

/*.webp
  Cache-Control: public, max-age=604800
```

Start with Report-Only. After a week of clean browser-console reports, change to `Content-Security-Policy:` (enforcing).

### 5.5 FAQPage schema everywhere

**Target: 4+ FAQPage Q&A entries per page** across hubs, service pages, brand pages, city pages. Include "near me" queries + cost queries verbatim — the exact phrases people type.

Example pattern (money-query Q&As):

```
Q: Where can I find <service> near me?
A: <Business> is based in <city, state> and services shops across
   <n> states — <list>. Call <phone> or use the quote form.

Q: How much does <service> cost?
A: <Service> cost depends on <scoping details>. We quote after
   reviewing <inputs>. Most quotes within one business day.
```

Phrased answer-first for AEO extraction.

---

## Phase 6 — Cloudflare zone settings to flip

Via dashboard or API for each new zone:

| Setting | Value | Why |
|---|---|---|
| **SSL mode** | `Full` | Not Flexible — flexible leaves Cloudflare→origin HTTP |
| **Min TLS version** | `1.2` | 1.0/1.1 are deprecated, security scanners ding |
| **Early Hints** | `on` | Free LCP boost (100-300ms) |
| **Browser Cache TTL** | `86400` (24h) | Static sites change weekly at best |
| **HSTS** | `enabled`, `max_age=31536000`, `include_subdomains`, `preload`, `nosniff` | After this is live, submit to [hstspreload.org](https://hstspreload.org) |
| **Bot Fight Mode** | `off` | Over-blocks legit AI bots |
| **AI Scrapers block toggle** | `off` | AEO requires AI bots to crawl |
| **Rocket Loader** | `off` | Breaks things |
| **Auto Minify** | `off` | Static sites already optimize at build time |

API calls (bulk-apply after swapping `$ZONE_ID`):

```bash
# SSL Full
curl -X PATCH -H "Authorization: Bearer $CF_TOKEN" -H "Content-Type: application/json" \
  "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/settings/ssl" \
  --data '{"value":"full"}'

# Min TLS 1.2
curl -X PATCH -H "Authorization: Bearer $CF_TOKEN" -H "Content-Type: application/json" \
  "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/settings/min_tls_version" \
  --data '{"value":"1.2"}'

# Early Hints
curl -X PATCH -H "Authorization: Bearer $CF_TOKEN" -H "Content-Type: application/json" \
  "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/settings/early_hints" \
  --data '{"value":"on"}'

# Browser Cache 24h
curl -X PATCH -H "Authorization: Bearer $CF_TOKEN" -H "Content-Type: application/json" \
  "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/settings/browser_cache_ttl" \
  --data '{"value":86400}'

# HSTS 1yr + preload + subdomains
curl -X PATCH -H "Authorization: Bearer $CF_TOKEN" -H "Content-Type: application/json" \
  "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/settings/security_header" \
  --data '{"value":{"strict_transport_security":{"enabled":true,"max_age":31536000,"include_subdomains":true,"preload":true,"nosniff":true}}}'
```

Required API token scopes for the above: `Zone Settings:Edit`, `Account Analytics:Read`.

---

## Phase 7 — Known gotchas (things that will bite you)

1. **GSC API `/user/tokens/verify` returns "Invalid API Token" even for valid tokens** — the verify endpoint needs different scope than your actual data-pull scopes. Test with the real endpoint (`/zones/{id}` or `/sites/{prop}/searchAnalytics/query`), not verify.

2. **Bing API throttles aggressively per IP** — if you test the key 5-10 times in a row, you'll get `ErrorCode:17 ThrottleIP`. Clears in 30-60 min. Rate-limit guard on manual refresh (the Worker code does this, 60 min minimum) prevents accidental triggering.

3. **IndexNow HTTP 429 for same URL submission** — IndexNow blocks re-submission of the same URL set too frequently. Guard with the same 60-min rate limit as the Bing cron. In practice: don't ping IndexNow on every deploy, only on content changes.

4. **GSC "AI Performance Overview" is NOT in the API** — you can see it in GSC UI, but there's no `AI_OVERVIEW` filter exposed via `searchAppearance`. Fall back to monthly manual CSV upload via `/admin/case-study`. This is a Google product gap, not fixable in code.

5. **Cloudflare Git integration project-reset wipes build config** — if you ever disconnect-and-reconnect the Git integration (e.g. after moving a repo between GitHub orgs), you lose Root Directory + Build Command settings. Re-set them in **Settings → Builds**.

6. **Cloudflare's new UI hides D1 permission under "Developer Platform"** — when creating an API token, D1 won't appear under a "Specified Domains" scope. Must add a separate policy with Account-level scope.

7. **Cloudflare API tokens start with `cfat_`** as of mid-2024, ~53 chars total. If a token comes out shorter, it's a token ID or name, not the actual token value.

8. **Workers Static Assets serves `_headers` and `_redirects`** correctly, BUT `functions/*` Pages Function convention does NOT execute. If you need server-side logic, use `worker.js` with the `ASSETS` binding fallthrough.

9. **Bot Fight Mode blocks legit AI bots** — if the client has Pro plan or higher, verify under Security → Bots that it's off. Super Bot Fight Mode (Business/Enterprise) has per-bot allow controls.

10. **`maybeLogTraffic()` must only be called with ctx** — the fetch handler signature is `async fetch(request, env, ctx)`. Some older examples use `(request, env)` and will break on `ctx.waitUntil(...)`.

---

## Phase 8 — One-sentence sanity test (after full deploy)

```bash
curl https://<client-domain>.com/api/case-study.json | jq '{
  gsc: .google_search.all_time.clicks,
  ai: .ai_search.all_time.total_citations,
  leads: .leads.total_submissions,
  updated: .last_updated
}'
```

If all four fields have non-null values and `updated` is recent, you're done.

---

## Phase 9 — Feeding the case-study page

On `heyaaronmarketing.com`, each client's case-study page does:

```js
// Build time or render time:
const res = await fetch("https://<client-domain>.com/api/case-study.json");
const data = await res.json();

// Render headline_stats, google_search.*, ai_search.*, leads.*, etc.
```

The JSON is CORS-enabled (`Access-Control-Allow-Origin: *`) so cross-origin fetch works.

Schema is stable at `schema_version: "1.1"`. If you need to change the shape in the future, bump the version and keep the old shape readable so existing case-study pages don't break.

---

## Reference implementation

**Repo**: https://github.com/heyaaronmarketing/midwestcnc

**Key files**:

- `public/worker.js` — the full Worker (1900+ lines, extensively commented)
- `public/wrangler.jsonc` — bindings + cron config
- `public/_headers` — security headers + CSP
- `public/robots.txt` — AI bot allowlist (generator pattern in `scripts/generate_site_shell.py` → `gen_robots()`)
- `public/llms.txt` + `public/llms-full.txt` — AI engine citation files
- `.github/workflows/insights-auto-draft.yml` — the weekly (now 2×daily) article auto-draft workflow
- `scripts/insights_auto_draft.py` — the draft orchestrator with 12 quality gates
- `scripts/insights_validators.py` — the 12 validation gates themselves

**Key endpoints**:

- `GET /api/case-study.json` — public, CORS-enabled
- `GET /<indexnow-key>.txt` — IndexNow verification file
- `GET /admin/login` → `POST` → session cookie
- `GET /admin` — leads list
- `GET /admin/case-study` — stats dashboard + CSV upload + "Refresh now"
- `GET /admin/traffic` — bot crawl + AI referral log
- `POST /api/quote` — form handler (redirects 303 on success/error)
- `POST /admin/case-study/refresh` — manual pipeline trigger

---

**Document version**: 1.0 — 2026-11-07
**Reference client**: Midwest CNC Services
**Maintainer**: Hey Aaron! Marketing

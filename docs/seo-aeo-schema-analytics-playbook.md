# SEO / AEO / Schema / Analytics Playbook

Portable patterns, all proven on midwestcncservices.com, ready to apply
to any other client site. Every item here was validated by the Bing
SEO audit + the Nov 2026 case-study pipeline work.

Hand this to a Claude Code session or an engineer. Reference
implementation: `heyaaronmarketing/midwestcnc`.

---

## Part 1 — SEO fundamentals

These aren't optional. Every page every client site must get right.

### 1.1 Title tags

- **Length: 50-60 characters.** 61+ gets truncated in SERPs. Bing flags
  at ~65; Google at ~60.
- **Pattern: `{Specific topic} | {Brand}`** — lets the specific part
  survive truncation when the brand gets cut.
- **No " | Midwest CNC Services" style brand suffix** on pages where
  the specific title is already long — drop the suffix entirely rather
  than let it push past 60ch.
- **Each page unique.** Zero duplicates. Audit with:
  ```bash
  grep -h "<title>" public/**/*.html | sort | uniq -c | sort -rn | head
  ```

### 1.2 Meta descriptions

- **Length: 120-160 characters.** 161+ gets truncated.
- **Each page unique.** Duplicates are a direct Bing audit flag. One
  midwestcnc commit cleared 119 duplicate pages by rewriting the
  per-vertical descriptions.
- **Include the target query verbatim** in the first 100 characters
  — AI engines quote descriptions when they match the query intent.
- **Avoid boilerplate suffixes** like "Common faults, parts
  availability..." that pad every page. Specificity beats length.

### 1.3 Canonical URLs

- **Every page** has `<link rel="canonical" href="https://domain.com/path/">`
- **Trailing slash: pick one convention site-wide.** We use trailing
  slash. Non-matching URLs 301-redirect to the canonical form.
- **Canonical matches the URL actually indexed.** If you serve
  `/foo` and `/foo/` both, canonical must point to one. Google treats
  mismatches as a signal you don't know your own URL structure.

### 1.4 The trailing-slash 307 → 301 trap

**Critical for Cloudflare Workers Static Assets sites.**

Default behavior: `GET /path` → 307 Temporary Redirect → `/path/`.
Google treats 307 as "non-permanent — don't consolidate ranking."
Result: duplicate URLs rank separately, splitting link equity.

**Fix** (`worker.js`, before `env.ASSETS.fetch`):
```javascript
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

Verify:
```bash
curl -sI https://domain.com/some-page   # Should return 301, not 307
```

Google reconsolidates duplicate rankings within 2-6 weeks of first
re-crawling the 301.

### 1.5 Sitemap

- **`public/sitemap.xml`** at site root, exclude draft/noindex pages
- **Submit to Google Search Console** at property setup
- **Submit to Bing Webmaster Tools** at property setup
- **Match disk reality:** every indexable HTML file should appear;
  intentional exclusions (`/get-a-quote/thank-you/`, drafts) explicitly
  omitted.
- **Validate with:**
  ```bash
  python3 -c "
  import xml.etree.ElementTree as ET
  from pathlib import Path
  sitemap_urls = set(e.text for e in ET.parse('public/sitemap.xml').findall('.//{*}loc'))
  disk_urls = set(f'https://domain.com/{p.relative_to(\"public\")}'.replace('/index.html','/') for p in Path('public').rglob('index.html'))
  print('In sitemap only:', len(sitemap_urls - disk_urls))
  print('On disk only:',   len(disk_urls - sitemap_urls))
  "
  ```

### 1.6 Internal linking — the money moves

- **Every article/page has at least 3-5 in-body internal links** to
  other site content (hubs, service pages, related articles).
- **Anchor text matches the target page's primary query.** Not "click
  here" — the words people would type to find the target.
- **Deliberate cross-hub links.** Every service hub links to every
  other service hub with the anchor text matching how prospects search:
  - `/spindle-grinding/` → `<a href="/repairs/">CNC repair near me</a>`
  - `/way-covers/` → `<a href="/repairs/">CNC machine repair</a>`
  - This directly lifted midwestcnc's close-to-page-1 queries.

### 1.7 Heading hierarchy

- **Exactly one `<h1>` per page.** Multiple h1s = Google treats first as
  canonical, others as noise. Audit:
  ```bash
  for f in $(find public -name "*.html"); do
    n=$(grep -c "<h1" "$f"); [ "$n" != "1" ] && echo "$n in $f"
  done
  ```
- **H2s are descriptive and definitional.** Not "Introduction" or
  "Overview" — "What a CNC Spindle Rebuild Costs" (a real H2).
- **Every H2 opens with a declarative-definitional first sentence.**
  Covered more in AEO section.

### 1.8 Image optimization

- **Every `<img>` has `alt` populated.** Zero missing. Decorative
  images use `alt=""` (empty, not missing).
- **WebP everywhere.** PNG/JPG sources stay in repo as source of truth;
  a build-time optimizer converts to WebP and rewrites HTML references.
  midwestcnc saved **23 MB (86%)** this way.
- **Pattern: WebP + HTML rewrite** (`scripts/optimize_images.py`):
  - Walks `public/assets/`, converts raster → WebP sibling
  - Rewrites every `.png`/`.jpg` reference in `public/**/*.html` to
    `.webp`
  - Idempotent, safe to re-run on every build

### 1.9 Redirects

- **`public/_redirects`** at site root for Cloudflare Workers Static
  Assets to honor
- **Format:**
  ```
  /old-path    /new-path    301
  ```
- **301, not 302 or 307** for anything permanent. Only 302 for
  genuinely temporary routes.

---

## Part 2 — AEO (AI Engine Optimization)

### 2.1 The AEO stack (what AI engines actually consume)

In priority order:

1. **FAQPage schema** — direct Q&A extraction target
2. **`llms.txt` + `llms-full.txt`** — machine-readable site index
3. **Definitional H2 first sentences** — answer-first format AI quotes
4. **Key Takeaways block** at the top of long articles
5. **Explicit AI bot allow-list in robots.txt** — trust signal
6. **LocalBusiness schema with openingHours** — fact grounding

### 2.2 FAQPage schema everywhere

- **Target: 4+ FAQPage Q&A entries per page** on hubs, service pages,
  brand pages, city pages.
- **Phrase Q&A verbatim to match SERP queries:**
  ```
  Q: Where can I find {service} near me?
  A: {Business} is based in {city, state} and services shops across
     {n} states — {list}. Call {phone} or use the quote form.

  Q: How much does {service} cost?
  A: {Service} cost depends on {scoping details}. We quote after
     reviewing {inputs}. Most quotes within one business day.
  ```
- **Schema markup:**
  ```json
  {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "The exact question phrasing",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Full answer in prose, 2-4 sentences, specific facts."
        }
      }
    ]
  }
  ```
- **One `<script type="application/ld+json">` per FAQPage block.**
  Validate at [search.google.com/test/rich-results](https://search.google.com/test/rich-results).
- **midwestcnc: 522 Q&A pairs across 101 pages** — the bulk of the
  AEO citation growth (5,028 AI citations in 112 days, +135% MoM in
  October) came from doubling this.

### 2.3 llms.txt + llms-full.txt

Per [llmstxt.org](https://llmstxt.org):

- **`llms.txt`** — brief, authoritative index. Hub pages, service
  descriptions, content licensing statement. Reference implementation
  at `public/llms.txt`.
- **`llms-full.txt`** — long-form. Every FAQ Q&A compiled into plain
  text with source URLs. midwestcnc's file is 145 KB with 522 Q&As,
  regenerated on every build.

Build pattern (Python, generates from existing HTML):
```python
def gen_llms_full_txt():
    pages = []
    for p in PUBLIC.rglob("index.html"):
        s = p.read_text()
        faqs = []
        for schema in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
            body = schema.group(1)
            if '"FAQPage"' not in body: continue
            data = json.loads(body)
            for e in data.get("mainEntity", []):
                q = e.get("name", "").strip()
                a = (e.get("acceptedAnswer") or {}).get("text", "").strip()
                if q and a: faqs.append((q, a))
        if faqs:
            pages.append((title, url, faqs))
    # Emit grouped-by-page plain text Q: / A: format
```

### 2.4 Definitional H2s

Every H2's first sentence must be a declarative statement, not a
question. AI engines quote these verbatim.

**BAD:** `## Why do spindles fail?`
**GOOD:** `## Spindle Failure Modes` → first sentence: "Spindle failure
in production CNC machines traces to one of four root causes: bearing
wear, taper damage, preload loss, or coolant intrusion."

### 2.5 Explicit AI bot robots.txt

Many AI engines look for their own user-agent before crawling. Naming
each explicitly is a trust signal (plus it survives a future
"default-block-unknown-bots" change on your part).

```
# Default: allow all
User-agent: *
Allow: /

# AI crawlers — explicit allow-list
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

Sitemap: https://domain.com/sitemap.xml
```

### 2.6 Content format for AI extraction

- **Short sentences.** Flesch reading ease ≥ 60.
- **Named entities early.** First 300 words of any article should
  contain at least one specific number AND 2+ named entities (brands,
  models, places).
- **Specific numbers, not hedges where you can help it.** "2-6 weeks"
  not "a few weeks"; "$12,000-$35,000" not "mid five-figures." AI
  engines prefer quotable specifics.
- **Key Takeaways block at the top of long articles.** 3-5 bullets,
  each a complete sentence with at least one specific number or named
  entity. AI engines extract these as answer summaries.

### 2.7 Validating you're being cited

- **Bing Webmaster Tools → AI Performance Overview** (manually export
  CSV monthly — no API yet)
- **GA4 referrer tracking** for `chat.openai.com`, `perplexity.ai`,
  `gemini.google.com`, `copilot.microsoft.com`, `claude.ai`
- **Server-side traffic log** (see Part 4) — catches AI bot *crawls*
  which GA4 is blind to

### 2.8 Verify no AI bots are being blocked

Run this on every client site after setup — one line per bot that returns anything other than 200 is a problem:

```bash
for ua in "GPTBot/1.0" "ChatGPT-User/1.0" "ClaudeBot/1.0" "PerplexityBot/1.0" \
          "Google-Extended" "CCBot/2.0" "anthropic-ai/1.0" "Amazonbot/0.1"; do
  code=$(curl -sS -o /dev/null -w "%{http_code}" -A "$ua" https://domain.com/)
  echo "  $code  $ua"
done
```

Also check Cloudflare dashboard **Security → Bots → AI Crawl Control**
— make sure the following are set to `disabled`:
- `ai_bots_protection`
- `ai_training`
- `ai_search`
- `ai_user`
- All of `ai_agents.*` (anthropic, google, openai, instinct, muse)

---

## Part 3 — Schema graph

The full schema inventory, in order of per-page importance.

### 3.1 LocalBusiness — site-wide

On every page that represents the business (homepage, service hubs,
city pages, service pages). One of these minimum:

```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "Midwest CNC Services",
  "url": "https://midwestcncservices.com",
  "telephone": "+1-319-610-4341",
  "priceRange": "$$",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "123 Industrial Way",
    "addressLocality": "Waterloo",
    "addressRegion": "IA",
    "postalCode": "50701",
    "addressCountry": "US"
  },
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": 42.4928,
    "longitude": -92.3426
  },
  "openingHoursSpecification": [
    {
      "@type": "OpeningHoursSpecification",
      "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday"],
      "opens": "07:00",
      "closes": "15:30"
    }
  ],
  "areaServed": [
    {"@type": "State", "name": "Iowa"},
    {"@type": "State", "name": "Illinois"},
    // ...
  ]
}
```

- **Phone with `tel:` format in markup, `+1-NNN-NNN-NNNN` in schema.**
- **openingHours is a HUGE AEO trust signal.** AI engines cite "open
  Mon-Fri 7am-3:30pm Central" directly from this.
- **areaServed** is how AI engines know you serve a specific state/city.

### 3.2 Service — per service page

```json
{
  "@context": "https://schema.org",
  "@type": "Service",
  "serviceType": "CNC Spindle Rebuild",
  "provider": { "@type": "LocalBusiness", "name": "Midwest CNC Services" },
  "areaServed": { "@type": "State", "name": "Iowa" },
  "description": "Full rebuild of CNC spindles across 18 OEM platforms..."
}
```

### 3.3 BreadcrumbList — every page except homepage

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "Home",
     "item": "https://domain.com/"},
    {"@type": "ListItem", "position": 2, "name": "Repairs",
     "item": "https://domain.com/repairs/"},
    {"@type": "ListItem", "position": 3, "name": "Mazak CNC Repair"}
  ]
}
```
Last item has no `item` URL — it's the current page.

### 3.4 FAQPage — covered in Part 2.2

### 3.5 City / State — on geo pages

```json
{"@type": "City", "name": "Waterloo", "containedInPlace": {"@type":"State","name":"Iowa"}}
```

### 3.6 Person — author credit on articles

```json
{
  "@type": "Person",
  "name": "Ken Ehlers",
  "jobTitle": "Shop Owner",
  "worksFor": {"@type": "Organization", "name": "Midwest CNC Services"}
}
```

### 3.7 WebPage — minimum for utility pages (404, thank-you, etc.)

```json
{
  "@context": "https://schema.org",
  "@type": "WebPage",
  "name": "Page Not Found",
  "url": "https://domain.com/404.html",
  "isPartOf": {"@type": "WebSite", "name": "...", "url": "..."}
}
```

### 3.8 Review — editorial reviews of products/services

For pages that review a single third-party product or service (software,
a lead platform, a tool). Editorial reviews of things you do NOT sell can
carry `Review` + `reviewRating` legitimately — star-snippet eligible and a
clean structured verdict AI engines quote directly. Map an honest verdict to
the rating; never inflate it.

```json
{
  "@type": "Review",
  "name": "Jobber Review (2026): Honest Pricing, Pros & Cons",
  "itemReviewed": {"@type": "SoftwareApplication", "name": "Jobber"},
  "author": {"@type": "Organization", "name": "Booked Job"},
  "reviewRating": {"@type": "Rating", "ratingValue": 4.5, "bestRating": 5, "worstRating": 1},
  "reviewBody": "Best first software for a small shop...",
  "datePublished": "2026-11-10"
}
```

- **`itemReviewed` type matters:** `SoftwareApplication` for apps, `Service`
  for lead/answering services, `Product` for physical goods.
- **ONLY on single-item review pages.** Category round-ups, "best X" guides,
  and "A vs B" comparisons are NOT single reviews — leave them Article-only,
  or Google ignores (or penalizes) the markup.
- **Never self-serving:** don't put `Review`/`aggregateRating` on your OWN
  product/service pages — Google strips those. Third-party editorial only.

### 3.9 VideoObject — the single biggest video-AEO move

AI engines can't watch video; they read the transcript. A self-hosted or
embedded clip earns nothing until it has `VideoObject` + an on-page transcript.

```json
{
  "@type": "VideoObject",
  "name": "AI receptionist mishears the address and books the wrong job",
  "description": "A dramatization of the transcription failure...",
  "thumbnailUrl": "https://domain.com/reels/clip.jpg",
  "contentUrl": "https://domain.com/reels/clip.mp4",
  "uploadDate": "2026-11-10",
  "duration": "PT14S",
  "transcript": "Customer: leak at 14 Oak Street... AI bot: Booked! 40 Elm Street, Sunday 2 AM..."
}
```

- **Always ship the transcript twice:** in the `transcript` property AND as
  real on-page text (a `<details>` block counts — it's in the DOM). The on-page
  copy is what gets cited; the property makes it video-rich-result eligible.
- **Poster frame** (`thumbnailUrl`) via one ffmpeg frame-grab at ~35% in.
- **`duration` is ISO-8601** (`PT14S`, `PT6M30S`), not seconds.

### 3.10 Validate every schema block

- **Google Rich Results Test:** [search.google.com/test/rich-results](https://search.google.com/test/rich-results)
- **Schema.org validator:** [validator.schema.org](https://validator.schema.org)
- **Site-wide count:**
  ```bash
  find public -name "*.html" | xargs grep -h '"@type"' | \
    grep -oE '"@type":\s*"[A-Za-z]+"' | sort | uniq -c | sort -rn
  ```
- **midwestcnc baseline:** 1,768+ schema nodes across 297 pages.
  Target this density on every new site.

---

## Part 4 — Analytics stack

Four independent layers, each catches what the others miss.

### 4.1 Google Analytics 4

- **Install via gtag.js** in `<head>` on every page
- **Measurement ID** in config (e.g. `G-XXXXXXXXXX`)
- **Install AFTER any CMP (ConsentResolve, Termageddon)** so consent
  gating works correctly
- **Only load on production hostname** — gate the CMP loader so
  preview URLs don't prompt:
  ```javascript
  if (location.hostname !== 'midwestcncservices.com' &&
      location.hostname !== 'www.midwestcncservices.com') return;
  ```

### 4.2 Google Search Console

- **Verify domain property** at [search.google.com/search-console](https://search.google.com/search-console)
- **Submit sitemap**
- **Create service account** in Google Cloud for automated API pulls
  (see case-study-pipeline-setup.md Phase 3.1 for click path)
- **Add service account as Owner** on the GSC property (not just Full
  — Owner is required for API access)
- **Weekly API pull** writes to D1 for case-study JSON

### 4.3 Bing Webmaster Tools

- **Verify** at [bing.com/webmasters](https://bing.com/webmasters)
- **Generate API key** (Settings → API Access → Generate)
- **AI Performance Overview** — monthly manual CSV export (no API
  access to this specific view yet)

### 4.4 Server-side traffic logging — the one GA4 can't do

**Captures AI bot crawls and AI engine referral clicks that GA4 is
100% blind to** (bots don't execute JavaScript).

Pattern (`worker.js`, called from main `fetch` handler):

```javascript
async fetch(request, env, ctx) {
  const url = new URL(request.url);
  // Fire-and-forget traffic logging
  maybeLogTraffic(request, env, ctx, url);
  // ... rest of routing
}

function maybeLogTraffic(request, env, ctx, url) {
  const path = url.pathname;
  // Skip assets, API endpoints, admin, static files
  if (path.startsWith("/assets/") || path.startsWith("/api/") ||
      path.startsWith("/admin") || path.endsWith(".webp")) return;

  const ua = request.headers.get("user-agent") || "";
  const ref = request.headers.get("referer") || "";
  const bot = classifyBot(ua);          // regex match against AI_BOT_PATTERNS
  const refererHost = extractRefererHost(ref, SELF_HOST);

  if (!bot && !refererHost) return;     // Nothing interesting to log

  ctx.waitUntil(
    env.DB.prepare(
      "INSERT INTO traffic_log (ts, path, bot, referer_host, country, user_agent) " +
      "VALUES (?, ?, ?, ?, ?, ?)"
    ).bind(new Date().toISOString(), path, bot, refererHost,
           request.cf?.country || null, ua.slice(0, 500)).run()
  );
}
```

D1 schema:
```sql
CREATE TABLE traffic_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts TEXT NOT NULL,
  path TEXT NOT NULL,
  bot TEXT,
  referer_host TEXT,
  country TEXT,
  user_agent TEXT
);
CREATE INDEX idx_traffic_ts ON traffic_log(ts DESC);
CREATE INDEX idx_traffic_bot ON traffic_log(bot);
```

AI bot patterns to classify on:
`GPTBot`, `ChatGPT-User`, `OAI-SearchBot`, `ClaudeBot`, `Claude-Web`,
`anthropic-ai`, `PerplexityBot`, `Perplexity-User`, `Google-Extended`,
`GoogleOther`, `Applebot-Extended`, `meta-externalagent`, `FacebookBot`,
`Amazonbot`, `cohere-ai`, `CCBot`, `Bytespider`, `MistralAI-User`,
`Diffbot`, plus traditional: `Googlebot`, `Bingbot`, `DuckDuckBot`,
`YandexBot`, `Baiduspider`.

AI engine referer hosts to flag:
`chat.openai.com`, `chatgpt.com`, `perplexity.ai`, `gemini.google.com`,
`bard.google.com`, `copilot.microsoft.com`, `claude.ai`, `poe.com`,
`you.com`, `andisearch.com`, `phind.com`, `deepseek.com`, `mistral.ai`,
`huggingface.co`.

### 4.5 GA4 Custom Report for AI referrers (5-min setup)

GA4 → **Explore** → **Free form** template:
- **Rows**: Session source
- **Values**: Sessions, Active users, Average session duration
- **Filter**: `Session source` **matches regex**:
  ```
  chatgpt\.com|chat\.openai\.com|perplexity\.ai|gemini\.google\.com|copilot\.microsoft\.com|claude\.ai|poe\.com|you\.com|andisearch\.com|phind\.com|deepseek\.com|mistral\.ai|huggingface\.co
  ```
- Save as "AI Engine Referrals"
- Bookmark the URL

### 4.6 IndexNow (Bing + Yandex instant-recrawl protocol)

- **Generate 32-char hex key** (deterministic from zone ID is cleanest)
- **Serve key verification file** at `public/<key>.txt`
- **Ping on every content refresh** (`worker.js`):
  ```javascript
  async function pingIndexNow(env) {
    const sitemapResp = await env.ASSETS.fetch(
      new Request(`https://${INDEXNOW_HOST}/sitemap.xml`)
    );
    const xml = await sitemapResp.text();
    const urls = Array.from(xml.matchAll(/<loc>([^<]+)<\/loc>/g)).map(m => m[1]);
    return fetch("https://api.indexnow.org/IndexNow", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        host: INDEXNOW_HOST, key: INDEXNOW_KEY,
        keyLocation: `https://${INDEXNOW_HOST}/${INDEXNOW_KEY}.txt`,
        urlList: urls,
      }),
    });
  }
  ```
- Google doesn't participate; this is Bing + Yandex + Seznam + Naver.
- **Bing (and `api.indexnow.org`) return `403 UserForbiddedToAccessSite`
  until the host is claimed in Bing Webmaster Tools** — even with a valid,
  served key file. This is an ownership check, NOT a code bug. **Yandex
  accepts regardless and fans the URLs across the IndexNow network**, so
  submit to `yandex.com/indexnow` first and treat the Bing 403 as expected
  noise until someone verifies the site in Bing WMT (a one-time manual step).
- Submit the key with a consistent `host` — apex vs `www` must match the
  host in your submitted URLs and the `keyLocation`, or the engine 403s.

---

## Part 5 — Cloudflare zone settings to flip

Every new client site, same 8 toggles. See the setup-pipeline doc's
Phase 6 for the bulk-API-call block. TL;DR:

| Setting | Value | Why |
|---|---|---|
| **SSL mode** | Full | Not Flexible |
| **Min TLS version** | 1.2 | Security scanners penalize 1.0/1.1 |
| **Early Hints** | on | Free LCP boost |
| **Browser Cache TTL** | 86400 | 24h, static sites change weekly at best |
| **HSTS** | max_age=31536000, include_subdomains, preload, nosniff | After live, submit to hstspreload.org |
| **Bot Fight Mode** | off | Over-blocks legit AI bots |
| **AI Scrapers block toggle** | off | AEO requires AI bots to crawl |
| **Rocket Loader** | off | Breaks things |

---

## Part 6 — Content quality gates (for AI-authored pages)

When auto-drafting content, enforce automated gates before publish.
midwestcnc uses 12 gates in `scripts/insights_validators.py`:

1. **word_count** — 1200-2000 words for article clusters
2. **flesch** — reading ease ≥ 60
3. **ban_list** — no "photo-verified", "factory-trained",
   "24/7", "ISO certified", "flat-rate", "guaranteed", "warranty",
   "same-day" (modify per client)
4. **hype_words** — no "premier", "world-class", "best-in-class",
   "leading", "unparalleled", "cutting-edge", "unmatched"
5. **exclamations** — zero exclamation points
6. **key_takeaways** — 3-5 bullet points at the top
7. **definitional_h2** — every H2 first sentence declarative, not a
   question
8. **cosine_similarity** — ≤ 0.3 vs any existing page (TF-IDF cosine)
9. **first_300_words** — ≥ 1 specific number + ≥ 2 named entities
10. **proprietary_signal** — specified phrases appear verbatim
11. **internal_links** — ≥ 5 in-body markdown links from the
    suggester-provided list of related URLs
12. **placeholders** — no `[TODO]`, `[FIXME]`, `<placeholder>`, etc.

**Gate behavior:** fail → retry with the specific failure listed in
the retry prompt → up to 3 attempts → promote on first pass; save a
review file + skip if all 3 fail.

**The `internal_links` gate is the one Opus/Claude most commonly
fails** on first draft. Mitigations:
- Pad suggested URLs with 7 evergreen hub URLs (hubs + /about/ + /get-a-quote/)
- Dedicated "⚠ CRITICAL" section in retry prompt with example markdown
  link syntax

---

## Part 7 — The Bing SEO Audit cheat sheet

Common issues Bing WMT's SEO Analysis Summary flags, with fixes:

| Issue | Root cause | Fix |
|---|---|---|
| **Too many pages with identical meta descriptions** | Generators sharing description boilerplate across page verticals | Rewrite with service-vertical-specific prefix. See midwestcnc commit history for the 119-page fix. |
| **Title too long** | Auto-generated `{specific} \| {brand suffix}` patterns pushing >60ch | Strip the brand suffix. Shorten specific titles where possible. |
| **Missing `<h1>`** | Template oversight | Add `<h1>` to every page. Audit as in Part 1.7. |
| **Site lacks inbound links from high-quality domains** | Not fixable in code | Industry trade publications, OEM reseller directories, chamber of commerce listings, LinkedIn outreach |
| **IndexNow not set up** | Missing key file + ping endpoint | See Part 4.6 |

---

## Part 8 — Measurement + reporting

Once it's all in place, measurements worth tracking per client:

### Weekly
- GSC clicks / impressions / avg position (API pull via service account)
- Bing clicks / impressions (API pull)
- Worker traffic_log: bot crawls per bot, AI engine referrals, unique pages crawled
- Lead form submissions (from D1 or your CRM)

### Monthly
- Bing AI Performance Overview (manual CSV upload — no API yet)
- GSC AI Overviews filter export (also manual)
- Position changes on target keywords
- New insights articles shipped (if auto-draft is running)

### Rolled up into `/api/case-study.json`
- Served per-client from each site's Worker
- Consumed by heyaaronmarketing.com for live case-study pages
- Full spec in `docs/case-study-pipeline-setup.md`

---

## Part 9 — Known gotchas

Things that will bite you on client site N+1, documented so you don't
rediscover them:

1. **Cloudflare Workers Static Assets default = 307 trailing-slash
   redirect.** Fix with Worker-level 301 (Part 1.4).

2. **Bing API throttles IPs aggressively.** Test 10 times in a row →
   ThrottleIP error 17 → clears in 30-60 min. Build a 60-min rate limit
   guard into any manual refresh endpoint.

3. **IndexNow HTTP 429** for same URL set re-submitted too frequently.
   Same 60-min guard applies.

4. **GSC "AI Performance" view is NOT in the API.** Fall back to monthly
   manual CSV upload. Known product gap.

5. **GSC verify endpoint (`/user/tokens/verify`) needs different scope
   than data endpoints.** "Invalid token" from verify doesn't mean the
   token's dead — test against the actual resource endpoint.

6. **Cloudflare API tokens** start with `cfat_` as of mid-2024,
   ~53 chars total. Shorter = you have the token ID/name, not the value.

7. **Cloudflare's new Zone API UI hides D1 under "Developer Platform"**
   — when creating an API token, D1 appears only under Account-level
   scope, not under Specified Domains.

8. **Workers Static Assets serves `_headers` and `_redirects`** —
   BUT the Pages Functions convention (`functions/*.js`) does NOT
   execute. Use `worker.js` with the ASSETS binding fallthrough.

9. **GitHub Actions can't create PRs on new orgs by default.** Settings
   → Actions → "Allow GitHub Actions to create and approve pull
   requests." Bites every freshly-transferred repo.

10. **`maybeLogTraffic()` requires `ctx` parameter.** Fetch handler
    signature must be `async fetch(request, env, ctx)`, not just
    `(request, env)`. Older examples use the latter and break.

11. **Cloudflare's bot protection blocks Python's default User-Agent**
    (Cloudflare error 1010) when calling external APIs like Resend from
    Python scripts. Set a custom `User-Agent: client-name/version`.

12. **GA4 `gtag` snippet inside a Python f-string template crashes the
    renderer.** `function gtag(){dataLayer.push(arguments);}` has literal
    `{}` that an f-string reads as fields → `SyntaxError: f-string: invalid
    syntax`, so the module won't import and the whole generator silently dies.
    Escape them: `function gtag(){{dataLayer.push(arguments);}}`. (Killed a
    blog pipeline for ~8 runs before anyone noticed — it only shows at import.)

13. **IndexNow `403 UserForbiddedToAccessSite` is a Bing ownership check,
    not a bug** — see Part 4.6. Yandex still fans out; claim the host in Bing
    Webmaster Tools to unlock Bing direct.

---

## Reference implementation

**Repo**: https://github.com/heyaaronmarketing/midwestcnc

**Key files**:

- `public/worker.js` — 1,900+ line Worker with traffic logging, form,
  admin UI, email relay, GSC/Bing cron
- `public/_headers` — security headers + CSP
- `public/robots.txt` — AI bot allow-list
- `public/llms.txt` + `public/llms-full.txt` — AI engine indexes
- `scripts/generate_site_shell.py` — the main page generator (shows
  the gen_robots, gen_headers, gen_llms_txt, gen_llms_full_txt patterns)
- `scripts/optimize_images.py` — WebP optimizer with HTML rewrite
- `scripts/insights_validators.py` — the 12 content quality gates
- `.github/workflows/insights-auto-draft.yml` — the AI content engine
- `.github/workflows/weekly-digest.yml` — the Monday email summary
- `docs/case-study-pipeline-setup.md` — the measurement-pipeline
  playbook (GSC + Bing + case-study JSON + admin UI)

**Companion doc**: `docs/case-study-pipeline-setup.md` covers the full
Cloudflare + GSC + Bing + IndexNow + admin UI + case-study JSON setup.
This doc covers the SEO/AEO/Schema/Analytics patterns those pipelines
measure.

---

**Document version**: 1.1 — 2026-11-12  (added 3.8 Review + 3.9 VideoObject schema; IndexNow Bing-WMT gotcha; gotchas 12-13)
**Reference client**: Midwest CNC Services
**Maintainer**: Hey Aaron! Marketing

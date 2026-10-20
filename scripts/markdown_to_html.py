#!/usr/bin/env python3
"""
Convert a generated brand markdown (src/content/spindle-brands/{slug}.md)
into a standalone HTML page. CSS lives in a single <style> block inside
<head> — we'll extract to /assets/css/ later once the design is locked.

This is a deliberately small, dependency-free Markdown converter that only
handles the constructs our generator emits:
  - YAML-ish front matter (one level of nesting + tiny inline objects)
  - Headings: `#`, `##`
  - Italic eyebrow: `_text_` on its own line
  - Paragraphs
  - Bulleted lists (single + 2-space-indented sublist)
  - Bold: `**text**`
  - Links: `[text](url)`
  - Blockquote: `> text`
  - Italic placeholders: `*text*`
"""

import html
import json
import os
import re
import sys

# Coverage-map loader script — kept as a module-level constant so its
# JS braces don't conflict with the f-string templates below.
from _coverage_map_loader import COVERAGE_MAP_LOADER


REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Three content directories — bulk runs scan all of them.
CONTENT_DIRS = [
    os.path.join(REPO, "src", "content", "spindle-brands"),
    os.path.join(REPO, "src", "content", "machine-repair"),
    os.path.join(REPO, "src", "content", "way-covers"),
]
# Back-compat alias — used by older tests + the targeted-by-slug code path.
CONTENT = CONTENT_DIRS[0]
OUTDIR  = os.path.join(REPO, "public")


# ---------- Front-matter parser ----------

def parse_frontmatter(src):
    """Pull the YAML-like header out of `src`. Returns (data, body)."""
    if not src.startswith("---\n"):
        return {}, src
    end = src.find("\n---\n", 4)
    if end < 0:
        return {}, src
    raw = src[4:end]
    body = src[end + 5:]

    # Tiny YAML reader. Handles:
    #   key: "string"
    #   key: number
    #   key:               <- nested object follows
    #     subkey: ...
    #   key:               <- list of (scalar | inline-object) follows
    #     - item
    #     - { k: v, k2: "v2" }
    lines = raw.split("\n")
    data = {}
    stack = [(data, -1)]  # (container, indent)

    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1; continue
        indent = len(line) - len(line.lstrip())
        # Pop stack to current indent
        while stack and indent <= stack[-1][1]:
            stack.pop()
        if not stack:
            stack = [(data, -1)]
        parent, _ = stack[-1]

        stripped = line.lstrip()

        # List item under previous key
        if stripped.startswith("- "):
            item_raw = stripped[2:].strip()
            if isinstance(parent, list):
                parent.append(_parse_scalar_or_inline(item_raw))
            i += 1; continue

        # key: value
        m = re.match(r"([^:]+):\s*(.*)$", stripped)
        if not m:
            i += 1; continue
        key, val = m.group(1).strip(), m.group(2).strip()
        # Strip wrapping quotes from the key ("@type" → @type)
        if (key.startswith('"') and key.endswith('"')) or (key.startswith("'") and key.endswith("'")):
            key = key[1:-1]

        if val == "":
            # Look ahead: list or nested object?
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines):
                next_line = lines[j]
                next_indent = len(next_line) - len(next_line.lstrip())
                if next_indent > indent:
                    if next_line.lstrip().startswith("- "):
                        new_container = []
                    else:
                        new_container = {}
                    parent[key] = new_container
                    stack.append((new_container, indent))
                    i += 1; continue
            parent[key] = ""
        else:
            parent[key] = _parse_scalar_or_inline(val)
        i += 1

    return data, body


def _parse_scalar_or_inline(v):
    """Parse one YAML scalar or inline object/array literal."""
    v = v.strip()
    # Strip quotes
    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
        return v[1:-1]
    # Inline object: { key: val, key2: "val2" }
    if v.startswith("{") and v.endswith("}"):
        inner = v[1:-1].strip()
        obj = {}
        # Split by commas not inside quotes
        parts = _split_smart(inner, ",")
        for part in parts:
            if not part.strip():
                continue
            m = re.match(r"([^:]+):\s*(.*)$", part.strip())
            if m:
                k = m.group(1).strip()
                if (k.startswith('"') and k.endswith('"')) or (k.startswith("'") and k.endswith("'")):
                    k = k[1:-1]
                obj[k] = _parse_scalar_or_inline(m.group(2))
        return obj
    # Number?
    if re.match(r"^-?\d+$", v):
        return int(v)
    return v


def _split_smart(s, delim):
    """Split on delim, respecting quoted strings and {}/[] nesting."""
    out, buf, depth, q = [], [], 0, None
    for c in s:
        if q:
            buf.append(c)
            if c == q: q = None
            continue
        if c in ('"', "'"):
            buf.append(c); q = c; continue
        if c in "{[":
            buf.append(c); depth += 1; continue
        if c in "}]":
            buf.append(c); depth -= 1; continue
        if c == delim and depth == 0:
            out.append("".join(buf)); buf = []
            continue
        buf.append(c)
    if buf:
        out.append("".join(buf))
    return out


# ---------- Markdown body converter ----------

def md_inline(s):
    """Apply inline markdown to a string. Returns HTML-safe markup."""
    # Escape any raw HTML first.
    s = html.escape(s, quote=False)
    # Images: ![alt](src) — must run before the [text](url) link rule
    s = re.sub(
        r"!\[([^\]]*)\]\(([^)]+)\)",
        lambda m: (
            f'<figure class="hero-figure">'
            f'<img src="{m.group(2)}" alt="{m.group(1)}" loading="lazy">'
            f'</figure>'
        ),
        s,
    )
    # Links: [text](url)
    s = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>',
        s,
    )
    # Bold: **text**
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    # Italic: *text* (single asterisk) — must run after bold
    s = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", s)
    # Italic: _text_ (underscore) — only matches when delimited by word boundaries
    s = re.sub(r"(?<!\w)_([^_\n]+)_(?!\w)", r"<em>\1</em>", s)
    return s


def md_body_to_html(body):
    """Convert the body (after front matter) into structured HTML.

    Produces top-level <p>, <h1>, <h2>, <ul>, <blockquote>, and a sentinel
    HTML comment per H2 so the wrapping template can group sections.
    """
    out = []
    paragraph_buf = []

    def flush_para():
        nonlocal paragraph_buf
        if paragraph_buf:
            joined = " ".join(paragraph_buf).strip()
            if joined:
                out.append(f"<p>{md_inline(joined)}</p>")
            paragraph_buf = []

    lines = body.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Blank line — paragraph break
        if not stripped:
            flush_para()
            i += 1; continue

        # Raw HTML block passthrough.
        # The generators emit polished HTML components (<h2 id="faq">,
        # <div class="faq-list">, <details class="faq-item">, <aside>,
        # <ol class="process-steps">, <script>) directly in the markdown
        # body. We pass them through verbatim and skip the markdown rules.
        #
        # Logic: if a line starts with one of these known block tags, take
        # the root tag-name. If the opening line also contains its own close,
        # emit one line. Otherwise consume lines (counting open/close of the
        # root tag) until balance, then emit.
        if stripped.startswith("<") and not stripped.startswith("</"):
            m_tag = re.match(r"<([a-zA-Z][a-zA-Z0-9]*)", stripped)
            tag = m_tag.group(1).lower() if m_tag else ""
            BLOCK_TAGS = {
                "script", "details", "div", "aside", "section",
                "h1", "h2", "h3", "h4", "h5", "h6",
                "ol", "ul", "p", "table", "figure",
            }
            if tag in BLOCK_TAGS:
                flush_para()
                close_tag = f"</{tag}>"
                open_tag_re = re.compile(rf"<{tag}\b", re.IGNORECASE)
                close_tag_re = re.compile(rf"</{tag}\s*>", re.IGNORECASE)
                # Self-closed or balanced on a single line?
                depth = len(open_tag_re.findall(line)) - len(close_tag_re.findall(line))
                block_lines = [line]
                i += 1
                while depth > 0 and i < len(lines):
                    block_lines.append(lines[i])
                    depth += len(open_tag_re.findall(lines[i])) - len(close_tag_re.findall(lines[i]))
                    i += 1
                out.append("\n".join(block_lines))
                continue

        # Standalone image — render as a figure outside any <p>
        if stripped.startswith("!["):
            flush_para()
            out.append(md_inline(stripped))
            i += 1; continue

        # Headings
        if stripped.startswith("# "):
            flush_para()
            out.append(f"<h1>{md_inline(stripped[2:].strip())}</h1>")
            i += 1; continue
        if stripped.startswith("## "):
            flush_para()
            heading = stripped[3:].strip()
            slug = re.sub(r"[^a-z0-9]+", "-", heading.lower()).strip("-")
            out.append(f'<h2 id="{slug}">{md_inline(heading)}</h2>')
            i += 1; continue
        if stripped.startswith("### "):
            flush_para()
            heading = stripped[4:].strip()
            slug = re.sub(r"[^a-z0-9]+", "-", heading.lower()).strip("-")
            out.append(f'<h3 id="{slug}">{md_inline(heading)}</h3>')
            i += 1; continue
        if stripped.startswith("#### "):
            flush_para()
            heading = stripped[5:].strip()
            out.append(f"<h4>{md_inline(heading)}</h4>")
            i += 1; continue

        # Blockquote
        if stripped.startswith("> "):
            flush_para()
            quote_lines = []
            while i < len(lines) and lines[i].lstrip().startswith("> "):
                quote_lines.append(lines[i].lstrip()[2:].strip())
                i += 1
            out.append(f'<blockquote><p>{md_inline(" ".join(quote_lines))}</p></blockquote>')
            continue

        # Bullet list (with optional one-level nested sublist)
        if stripped.startswith("- "):
            flush_para()
            out.append("<ul>")
            while i < len(lines) and lines[i].lstrip().startswith("- "):
                raw = lines[i]
                indent = len(raw) - len(raw.lstrip())
                item_text = raw.lstrip()[2:].strip()
                if indent == 0:
                    out.append(f"<li>{md_inline(item_text)}")
                    # Check for nested items
                    nested_start = i + 1
                    nested_items = []
                    while (nested_start < len(lines)
                           and lines[nested_start].lstrip().startswith("- ")
                           and (len(lines[nested_start]) - len(lines[nested_start].lstrip())) > 0):
                        nested_items.append(lines[nested_start].lstrip()[2:].strip())
                        nested_start += 1
                    if nested_items:
                        out.append("<ul>")
                        for ni in nested_items:
                            out.append(f"<li>{md_inline(ni)}</li>")
                        out.append("</ul>")
                        i = nested_start
                    else:
                        i += 1
                    out.append("</li>")
                else:
                    # Stray nested item with no parent at indent 0; treat as flat.
                    out.append(f"<li>{md_inline(item_text)}</li>")
                    i += 1
            out.append("</ul>")
            continue

        # Default — accumulate into paragraph
        paragraph_buf.append(stripped)
        i += 1

    flush_para()
    return "\n".join(out)


# ---------- Shared <head> snippets (analytics, social cards) ----------

# Third-party tracking pixel injected as the first child of <head> on
# every page by all three generators. Positioned above the charset/
# viewport meta per the user's install instruction. Charset is still
# well within the first 1024 bytes required by the HTML5 spec.
TRACKING_HEAD = (
    '<script async="async" '
    'src="https://mm-uxrv.com/js/mm_3b1133e8-9d62-4d76-bca2-ed8b11f21cf9-40876802.js">'
    '</script>'
)

# Google Analytics (GA4) + ConsentResolve CMP. Plain (non-f) string so
# the JS braces don't collide with f-string parsing. Injected into the
# <head> of every page by all three generators (this module,
# generate_site_shell, generate_insights_pages).
#
# CMP gating: ConsentResolve/Usercentrics writes its consent state as a
# cookie on the domain it is registered for (midwestcncservices.com).
# Loading the CMP on midwestcnc.aironz.workers.dev (the current preview
# URL) or on local files causes the banner to re-prompt on every reload
# because the cookie lookup fails. So we only inject the CMP loader
# when the browser is running on the production hostname. GA4 stays on
# for all environments so preview traffic is still tracked.
ANALYTICS_HEAD = """<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-3G003SQE93"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-3G003SQE93');
</script>
<script>
  // Only load the ConsentResolve CMP on the production domain. On
  // preview URLs the CMP cannot persist consent, so the banner would
  // reappear on every page load.
  (function() {
    if (location.hostname !== 'midwestcncservices.com' &&
        location.hostname !== 'www.midwestcncservices.com') return;
    var s = document.createElement('script');
    s.src = 'https://cdn.consentresolve.com/consentresolve.js';
    s.onload = function() {
      ConsentResolve.init({
        siteId: '89378cf0-e275-41af-a5ab-5836c6647c93',
        usercentricsSettingsId: 'NtX5STrPifLEMi'
      });
      ConsentResolve.page();
    };
    document.head.appendChild(s);
  })();
</script>"""

# Default Open Graph / Twitter card image used site-wide unless a page
# supplies its own. Absolute URL required by OG. The highway shot is
# already WebP-optimized and reads as a strong brand image.
DEFAULT_OG_IMAGE = "https://midwestcncservices.com/assets/images/general/midwest-cnc-highway-shot.webp"


def social_meta(title, description, canonical, image=None):
    """Return the og:image + twitter card meta tags shared by all
    generators. The og:title / og:description / og:type tags stay in
    each generator's head template; this adds the image + twitter set."""
    img = image or DEFAULT_OG_IMAGE
    return (
        f'<meta property="og:image" content="{html.escape(img)}">\n'
        f'<meta property="og:url" content="{html.escape(canonical)}">\n'
        f'<meta property="og:site_name" content="Midwest CNC Services">\n'
        f'<meta name="twitter:card" content="summary_large_image">\n'
        f'<meta name="twitter:title" content="{html.escape(title)}">\n'
        f'<meta name="twitter:description" content="{html.escape(description)}">\n'
        f'<meta name="twitter:image" content="{html.escape(img)}">'
    )


# Minimal site-wide LocalBusiness identity. Injected into any page that
# has a Service schema but no LocalBusiness of its own (the 165 brand
# spoke pages), so the structured-data graph is complete site-wide.
LOCAL_BUSINESS_SCHEMA = {
    "@context": "https://schema.org",
    "@type": "LocalBusiness",
    "@id": "#org",
    "name": "Midwest CNC Services",
    "telephone": "+13196104341",
}


# ---------- Schema JSON-LD ----------

def schema_jsonld(fm):
    """Emit the schema_data front-matter block as one or more JSON-LD scripts.

    If the page declares a Service but no LocalBusiness, inject the
    minimal site-wide LocalBusiness (#org) so brand spoke pages carry
    the same business identity the hub pages do."""
    schema = fm.get("schema_data", {}) or {}
    scripts = []
    for key in ("service", "local_business", "breadcrumb"):
        if key not in schema:
            continue
        block = _expand_schema_block(schema[key], key, fm)
        json_str = json.dumps(block, indent=2, ensure_ascii=False)
        scripts.append(
            f'<script type="application/ld+json">\n{json_str}\n</script>'
        )
    # Backfill LocalBusiness on service pages that don't define one.
    if "service" in schema and "local_business" not in schema:
        json_str = json.dumps(LOCAL_BUSINESS_SCHEMA, indent=2, ensure_ascii=False)
        scripts.append(
            f'<script type="application/ld+json">\n{json_str}\n</script>'
        )
    return "\n".join(scripts)


def _expand_schema_block(block, key, fm):
    """Convert a parsed schema_data sub-block into a JSON-LD-shaped dict."""
    if not isinstance(block, dict):
        return block
    out = {"@context": "https://schema.org"}
    # Reorder to put @type / @id first
    if "@type" in block:
        out["@type"] = block["@type"]
    if "@id" in block:
        out["@id"] = block["@id"]
    for k, v in block.items():
        if k in ("@type", "@id"):
            continue
        out[k] = v
    return out


# ---------- Page template ----------

CSS = """\
/* =================================================================
   Midwest CNC Services — modern design system
   Tokens: color (preserved), spacing, type, radius, shadow, motion.
   Accessibility: WCAG AA contrast, focus-visible rings, reduced motion.
   ================================================================= */

:root {
  /* Color (unchanged) */
  --bg: #ffffff;
  --fg: #1a1a1a;
  --muted: #5a5a5a;
  --accent: #b8341a;
  --accent-dark: #8c2510;
  --line: #e5e5e5;
  --soft: #f6f4f1;

  /* Surfaces */
  --surface: #ffffff;
  --surface-2: #faf8f5;
  --surface-3: #f1ede7;
  --ring: rgba(184, 52, 26, 0.35);
  --ring-strong: rgba(184, 52, 26, 0.55);
  --success-bg: #e8f5e8;
  --success-fg: #1e5e22;
  --warning-bg: #fff4e3;
  --warning-fg: #8a5400;

  /* Spacing scale (rem) */
  --s-1: 0.25rem;
  --s-2: 0.5rem;
  --s-3: 0.75rem;
  --s-4: 1rem;
  --s-5: 1.5rem;
  --s-6: 2rem;
  --s-7: 3rem;
  --s-8: 4rem;
  --s-9: 6rem;

  /* Radius scale */
  --r-1: 4px;
  --r-2: 8px;
  --r-3: 12px;
  --r-4: 16px;
  --r-pill: 999px;

  /* Shadow scale */
  --sh-1: 0 1px 2px rgba(15, 18, 22, 0.05);
  --sh-2: 0 1px 3px rgba(15, 18, 22, 0.06), 0 2px 8px rgba(15, 18, 22, 0.04);
  --sh-3: 0 4px 12px rgba(15, 18, 22, 0.08), 0 2px 4px rgba(15, 18, 22, 0.04);
  --sh-4: 0 12px 32px rgba(15, 18, 22, 0.10), 0 4px 12px rgba(15, 18, 22, 0.06);
  --sh-focus: 0 0 0 3px var(--ring);

  /* Motion */
  --t-fast: 120ms cubic-bezier(0.2, 0.6, 0.3, 1);
  --t-base: 200ms cubic-bezier(0.2, 0.6, 0.3, 1);
  --t-slow: 320ms cubic-bezier(0.2, 0.6, 0.3, 1);

  /* Layout */
  --max: 72ch;
  --max-wide: 1140px;
  --sticky-cta-height: 64px;
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
}

* { box-sizing: border-box; }

html { -webkit-text-size-adjust: 100%; scroll-behavior: smooth; }

html, body {
  margin: 0;
  font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  font-size: 17px;
  line-height: 1.6;
  color: var(--fg);
  background: var(--bg);
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}

/* Skip link for keyboard users */
.skip-link {
  position: absolute;
  left: -9999px;
  top: 0;
  z-index: 9999;
  background: var(--accent);
  color: #fff !important;
  padding: 0.75rem 1.25rem;
  border-radius: 0 0 var(--r-2) 0;
  font-weight: 600;
  text-decoration: none !important;
}
.skip-link:focus { left: 0; }

/* Global focus ring — only on keyboard, not mouse click */
*:focus { outline: none; }
*:focus-visible {
  outline: none;
  box-shadow: var(--sh-focus);
  border-radius: var(--r-1);
}

a { color: var(--accent); text-decoration: underline; text-underline-offset: 3px; text-decoration-thickness: 1px; transition: color var(--t-fast); }
a:hover { color: var(--accent-dark); text-decoration-thickness: 2px; }
a:focus-visible { box-shadow: var(--sh-focus); border-radius: var(--r-1); outline: none; }

::selection { background: var(--accent); color: #fff; }

/* =================================================================
   Header + primary navigation
   ================================================================= */
.site-header {
  position: sticky;
  top: 0;
  z-index: 50;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: saturate(180%) blur(10px);
  -webkit-backdrop-filter: saturate(180%) blur(10px);
  border-bottom: 1px solid var(--line);
  padding: var(--s-2) var(--s-5);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--s-4);
}
.site-header .brand {
  font-weight: 700;
  letter-spacing: -0.01em;
  display: inline-flex;
  align-items: center;
  text-decoration: none;
  color: var(--fg);
  transition: transform var(--t-fast);
}
.site-header .brand:hover { transform: translateY(-1px); }
.site-header .brand img {
  height: 72px;
  width: auto;
  display: block;
}
.site-header nav { display: flex; align-items: center; gap: var(--s-2); }
.site-header nav > ul {
  display: flex;
  align-items: center;
  list-style: none;
  margin: 0;
  padding: 0;
  gap: var(--s-1);
}
.site-header nav > ul > li { position: relative; }
.site-header nav > ul > li > a,
.site-header nav > ul > li > .menu-label {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.55rem 0.85rem;
  text-decoration: none;
  color: var(--fg);
  font-weight: 600;
  font-size: 0.95rem;
  border-radius: var(--r-2);
  cursor: pointer;
  white-space: nowrap;
  transition: color var(--t-fast), background var(--t-fast);
}
.site-header nav > ul > li > a:hover,
.site-header nav > ul > li > .menu-label:hover,
.site-header nav > ul > li:hover > a,
.site-header nav > ul > li:hover > .menu-label,
.site-header nav > ul > li:focus-within > a,
.site-header nav > ul > li:focus-within > .menu-label {
  color: var(--accent);
  background: var(--surface-2);
}
.site-header nav > ul > li.has-dropdown > .menu-label::after {
  content: "";
  display: inline-block;
  width: 8px;
  height: 8px;
  border-right: 2px solid currentColor;
  border-bottom: 2px solid currentColor;
  transform: rotate(45deg) translateY(-1px);
  margin-left: 2px;
  opacity: 0.6;
  transition: transform var(--t-fast), opacity var(--t-fast);
}
.site-header nav > ul > li.has-dropdown:hover > .menu-label::after,
.site-header nav > ul > li.has-dropdown:focus-within > .menu-label::after {
  transform: rotate(-135deg) translateY(2px);
  opacity: 1;
}
.site-header nav .dropdown {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  min-width: 240px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--r-3);
  box-shadow: var(--sh-4);
  padding: var(--s-2) 0;
  margin: 0;
  list-style: none;
  opacity: 0;
  visibility: hidden;
  transform: translateY(-6px);
  transition: opacity var(--t-fast), transform var(--t-fast), visibility var(--t-fast);
  z-index: 100;
}
.site-header nav > ul > li:hover > .dropdown,
.site-header nav > ul > li:focus-within > .dropdown {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}
.site-header nav .dropdown li { margin: 0; }
.site-header nav .dropdown a {
  display: block;
  padding: 0.5rem 1.1rem;
  text-decoration: none;
  color: var(--fg);
  font-size: 0.92rem;
  font-weight: 500;
  white-space: nowrap;
  transition: background var(--t-fast), color var(--t-fast), padding-left var(--t-fast);
}
.site-header nav .dropdown a:hover,
.site-header nav .dropdown a:focus { background: var(--surface-2); color: var(--accent); padding-left: 1.35rem; }
.site-header nav .dropdown .dropdown-section {
  padding: 0.55rem 1.1rem 0.3rem;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted);
  font-weight: 700;
}
.site-header nav .dropdown .dropdown-divider {
  height: 1px;
  background: var(--line);
  margin: var(--s-2) 0;
  list-style: none;
}
.site-header nav .dropdown a.dropdown-all {
  color: var(--accent);
  font-weight: 600;
}
.site-header nav a.cta-nav {
  background: var(--accent);
  color: #fff !important;
  padding: 0.6rem 1.1rem;
  border-radius: var(--r-pill);
  margin-left: var(--s-2);
  box-shadow: var(--sh-2);
  transition: background var(--t-fast), transform var(--t-fast), box-shadow var(--t-fast);
}
.site-header nav a.cta-nav:hover { background: var(--accent-dark); color: #fff !important; transform: translateY(-1px); box-shadow: var(--sh-3); }
.site-header nav a.cta-nav:active { transform: translateY(0); box-shadow: var(--sh-1); }

/* =================================================================
   Breadcrumbs — subtle pill row
   ================================================================= */
nav.breadcrumbs {
  font-size: 0.85rem;
  color: var(--muted);
  padding: var(--s-3) var(--s-5);
  background: var(--surface-2);
  border-bottom: 1px solid var(--line);
}
nav.breadcrumbs ol { list-style: none; margin: 0 auto; padding: 0; display: flex; flex-wrap: wrap; gap: var(--s-2); align-items: center; max-width: var(--max-wide); }
nav.breadcrumbs li { display: inline-flex; align-items: center; }
nav.breadcrumbs li:not(:last-child)::after {
  content: "";
  display: inline-block;
  width: 5px;
  height: 5px;
  border-right: 1.5px solid var(--muted);
  border-top: 1.5px solid var(--muted);
  transform: rotate(45deg);
  margin-left: var(--s-2);
  opacity: 0.6;
}
nav.breadcrumbs a {
  color: var(--muted);
  text-decoration: none;
  padding: 0.15rem 0.5rem;
  border-radius: var(--r-pill);
  transition: background var(--t-fast), color var(--t-fast);
}
nav.breadcrumbs a:hover { color: var(--accent); background: var(--surface); }
nav.breadcrumbs li:last-child { color: var(--fg); font-weight: 600; padding: 0.15rem 0.5rem; }

/* =================================================================
   Article + alternating section bands
   ================================================================= */
main { padding: 0; }

article {
  max-width: none;
  margin: 0;
  padding: 0;
}

/* Each <section class="page-section"> is a full-bleed band.
   The .section-inner inside centers content at the readable width. */
.page-section {
  padding: var(--s-7) var(--s-5);
  position: relative;
}
.page-section + .page-section { border-top: 1px solid transparent; }

.page-section-0 { background: var(--bg); }
.page-section-1 { background: var(--surface-2); }
.page-section-hero { background: var(--bg); padding-top: var(--s-5); padding-bottom: 0; }
.page-section-intro { padding-top: var(--s-6); }

.section-inner {
  max-width: var(--max);
  margin: 0 auto;
  width: 100%;
}
.section-inner.wide { max-width: var(--max-wide); }

/* When section content starts with an h2, kill its top margin since the
   section already provides the breathing room. */
.page-section > .section-inner > h2:first-child,
.page-section > .section-inner > .eyebrow:first-child + h2 {
  margin-top: 0;
}
.page-section > .section-inner > .eyebrow:first-child { margin-top: 0; }

/* Headings should be scrollable-into-view past the sticky header */
h2 { scroll-margin-top: 100px; }

@media (max-width: 800px) {
  .page-section { padding: var(--s-6) var(--s-4); }
  .page-section-hero { padding-top: var(--s-4); }
}
@media (max-width: 600px) {
  .page-section { padding: var(--s-5) var(--s-4); }
}

.eyebrow {
  color: var(--accent);
  font-size: 0.78rem;
  font-style: normal;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  margin: 0 0 var(--s-3) 0;
  display: inline-block;
  padding: 0.3rem 0.7rem;
  background: rgba(184, 52, 26, 0.08);
  border-radius: var(--r-pill);
}

h1 {
  font-size: clamp(2rem, 4.5vw, 3rem);
  line-height: 1.12;
  letter-spacing: -0.025em;
  margin: 0 0 var(--s-5) 0;
  font-weight: 700;
}

h2 {
  font-size: clamp(1.4rem, 2.5vw, 1.7rem);
  line-height: 1.25;
  margin: var(--s-7) 0 var(--s-4) 0;
  letter-spacing: -0.015em;
  font-weight: 700;
  position: relative;
  padding-top: 0;
  border-top: 0;
}
h2::before {
  content: "";
  display: block;
  width: 36px;
  height: 3px;
  background: var(--accent);
  border-radius: 3px;
  margin-bottom: var(--s-3);
}
h2:first-of-type { margin-top: var(--s-5); }

h3 {
  font-size: 1.15rem;
  line-height: 1.3;
  margin: var(--s-5) 0 var(--s-3) 0;
  letter-spacing: -0.01em;
  font-weight: 700;
}

h4 {
  font-size: 1rem;
  line-height: 1.4;
  margin: var(--s-4) 0 var(--s-2) 0;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--muted);
}

p { margin: var(--s-3) 0; }
p strong { color: var(--fg); font-weight: 700; }

ul, ol { padding-left: 1.5rem; margin: var(--s-3) 0; }
li { margin: var(--s-2) 0; }
li::marker { color: var(--accent); }

article ul li {
  position: relative;
  padding-left: var(--s-1);
}

hr {
  border: 0;
  border-top: 1px solid var(--line);
  margin: var(--s-7) 0;
}

blockquote {
  margin: var(--s-5) 0;
  padding: var(--s-4) var(--s-5);
  background: var(--surface-2);
  border-left: 4px solid var(--accent);
  border-radius: 0 var(--r-3) var(--r-3) 0;
  color: var(--fg);
  font-style: normal;
  position: relative;
  box-shadow: var(--sh-1);
}
blockquote::before {
  content: "“";
  position: absolute;
  top: -0.5rem;
  left: var(--s-4);
  font-size: 3rem;
  line-height: 1;
  color: var(--accent);
  opacity: 0.25;
  font-family: Georgia, serif;
}
blockquote p { margin: 0; padding-left: 1.5rem; font-size: 1.02rem; line-height: 1.55; }
blockquote p + p { margin-top: var(--s-3); }
blockquote em { font-style: normal; color: var(--muted); }

/* =================================================================
   Buttons + CTA row
   ================================================================= */
.cta-row {
  display: flex;
  flex-wrap: wrap;
  gap: var(--s-3);
  margin: var(--s-5) 0;
  align-items: center;
}
.cta-button {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: var(--accent);
  color: #fff !important;
  padding: 0.85rem 1.6rem;
  border-radius: var(--r-pill);
  text-decoration: none !important;
  font-weight: 600;
  letter-spacing: 0.01em;
  border: 0;
  cursor: pointer;
  font-size: 0.98rem;
  box-shadow: var(--sh-2);
  transition: background var(--t-fast), transform var(--t-fast), box-shadow var(--t-fast);
  position: relative;
}
.cta-button::after {
  content: "";
  display: inline-block;
  width: 7px;
  height: 7px;
  border-right: 2px solid currentColor;
  border-top: 2px solid currentColor;
  transform: rotate(45deg);
  margin-left: 0.25rem;
  transition: transform var(--t-fast);
}
.cta-button:hover { background: var(--accent-dark); transform: translateY(-1px); box-shadow: var(--sh-3); }
.cta-button:hover::after { transform: rotate(45deg) translate(2px, -2px); }
.cta-button:active { transform: translateY(0); box-shadow: var(--sh-1); }

.cta-button.secondary {
  background: var(--surface);
  color: var(--fg) !important;
  border: 1.5px solid var(--line);
  box-shadow: none;
}
.cta-button.secondary:hover {
  background: var(--surface-2);
  border-color: var(--accent);
  color: var(--accent) !important;
}
.cta-button.secondary::after { border-color: currentColor; }

.cta-phone {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.85rem 1.2rem;
  color: var(--fg) !important;
  text-decoration: none !important;
  font-weight: 700;
  font-size: 1rem;
  border-radius: var(--r-pill);
  background: var(--surface);
  border: 1.5px solid var(--line);
  transition: border-color var(--t-fast), color var(--t-fast), transform var(--t-fast);
}
.cta-phone::before {
  content: "";
  display: inline-block;
  width: 18px;
  height: 18px;
  background-color: currentColor;
  -webkit-mask: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'><path d='M6.62 10.79a15.05 15.05 0 0 0 6.59 6.59l2.2-2.2a1 1 0 0 1 1.01-.24c1.12.37 2.33.57 3.58.57a1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.46.57 3.58.1.36.03.74-.24 1.01l-2.21 2.2z'/></svg>") center/contain no-repeat;
          mask: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'><path d='M6.62 10.79a15.05 15.05 0 0 0 6.59 6.59l2.2-2.2a1 1 0 0 1 1.01-.24c1.12.37 2.33.57 3.58.57a1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.46.57 3.58.1.36.03.74-.24 1.01l-2.21 2.2z'/></svg>") center/contain no-repeat;
  color: var(--accent);
}
.cta-phone:hover { border-color: var(--accent); color: var(--accent) !important; transform: translateY(-1px); }

/* =================================================================
   Form placeholder + hero figure
   ================================================================= */
.quote-form-placeholder {
  margin: var(--s-5) 0;
  padding: var(--s-5);
  border: 2px dashed var(--line);
  border-radius: var(--r-3);
  background: var(--surface-2);
  color: var(--muted);
  font-style: italic;
  font-size: 0.9rem;
}

.hero-figure {
  margin: var(--s-5) 0 0 0;
  padding: 0;
}
.hero-figure img {
  width: 100%;
  height: auto;
  max-height: 440px;
  object-fit: cover;
  object-position: center;
  border-radius: var(--r-3);
  display: block;
  box-shadow: var(--sh-3);
}

/* =================================================================
   Brand page hero — image background, centered text, dark overlay.
   Same visual language as the homepage video hero. Used by brand-
   repair / brand-spindle / brand-way-covers pages. Emitted by the
   generators as <section class="brand-hero"> and wrapped in a
   page-section-hero band by wrap_into_sections.
   ================================================================= */
/* Hero band overrides — the band itself is full-bleed and the inner
   container drops its readable-column max-width so the hero image
   actually fills the viewport instead of being boxed into 72ch. */
.page-section-hero {
  padding: 0;
  background: var(--bg);
}
.page-section-hero > .section-inner {
  max-width: none;
  width: 100%;
  padding: 0;
}

.brand-hero {
  position: relative;
  width: 100%;
  min-height: clamp(380px, 55vh, 540px);
  display: flex;
  align-items: center;
  overflow: hidden;
  isolation: isolate;
  color: #fff;
  margin: 0;
  background: #000;
}
.brand-hero-bg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
  z-index: 1;
  pointer-events: none;
}
.brand-hero-overlay {
  position: absolute;
  inset: 0;
  z-index: 2;
  pointer-events: none;
  background: linear-gradient(
    to bottom,
    rgba(0, 0, 0, 0.55) 0%,
    rgba(0, 0, 0, 0.75) 100%
  );
}
.brand-hero-content {
  position: relative;
  z-index: 3;
  max-width: var(--max-wide);
  width: 100%;
  margin: 0 auto;
  padding: clamp(3rem, 6vw, 4.5rem) var(--s-5);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}
.brand-hero-content > .eyebrow {
  font-size: 0.7rem;
  padding: 0.25rem 0.7rem;
  margin: 0 0 var(--s-4) 0;
  background: rgba(255, 255, 255, 0.12);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.20);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}
.brand-hero-content > h1 {
  font-size: clamp(1.9rem, 4vw, 3rem);
  line-height: 1.08;
  letter-spacing: -0.025em;
  font-weight: 800;
  margin: 0 0 var(--s-4) 0;
  max-width: 24ch;
  color: #fff;
  text-shadow: 0 2px 12px rgba(0, 0, 0, 0.35);
}
.brand-hero-content > p {
  font-size: clamp(1rem, 1.2vw, 1.15rem);
  line-height: 1.55;
  color: rgba(255, 255, 255, 0.92);
  margin: 0 0 var(--s-5) 0;
  max-width: 58ch;
  text-shadow: 0 1px 6px rgba(0, 0, 0, 0.4);
}
.brand-hero-content > .cta-row {
  margin: 0;
  justify-content: center;
}
/* Frosted-glass phone CTA against the dark hero (same treatment the
   homepage hero uses) */
.brand-hero-content .cta-phone {
  background: rgba(255, 255, 255, 0.10);
  color: #fff !important;
  border-color: rgba(255, 255, 255, 0.28);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}
.brand-hero-content .cta-phone:hover {
  background: rgba(255, 255, 255, 0.18);
  border-color: rgba(255, 255, 255, 0.5);
  color: #fff !important;
}
.brand-hero-content .cta-phone::before { color: #fff; }

@media (max-width: 768px) {
  .brand-hero { min-height: clamp(340px, 60vh, 480px); }
  .brand-hero-content { padding: clamp(2rem, 7vw, 3rem) var(--s-4); }
  .brand-hero-content > .cta-row { width: 100%; flex-direction: column; }
  .brand-hero-content > .cta-row > * { width: 100%; justify-content: center; }
}

/* =================================================================
   Two-column page hero — used by every page that has a hero image.
   Applied automatically by wrap_into_sections when the intro section
   contains a <figure class="hero-figure">.
   ================================================================= */
.page-hero {
  display: grid;
  grid-template-columns: 1.1fr 1fr;
  gap: var(--s-7);
  align-items: center;
  margin: 0;
  padding: var(--s-4) 0 var(--s-5) 0;
}
.page-hero-text { min-width: 0; }
.page-hero-text > :first-child { margin-top: 0; }
.page-hero-text > h1 { margin-top: 0; }
.page-hero-text > p { font-size: 1.05rem; }
.page-hero-text > p:first-of-type { color: var(--fg); }
.page-hero-image { min-width: 0; }
.page-hero-image figure {
  margin: 0;
  padding: 0;
}
.page-hero-image figure img {
  width: 100%;
  height: auto;
  display: block;
  border-radius: var(--r-3);
  object-fit: cover;
  aspect-ratio: 4 / 3;
  max-height: none;
  box-shadow: var(--sh-4);
}
@media (max-width: 900px) {
  .page-hero {
    grid-template-columns: 1fr;
    gap: var(--s-5);
    padding: var(--s-3) 0 var(--s-4) 0;
  }
  .page-hero-image figure img {
    max-height: 320px;
    aspect-ratio: 16 / 10;
  }
}

/* =================================================================
   Tables — modern card-wrapped responsive
   ================================================================= */
.table-scroll {
  margin: var(--s-5) 0;
  border-radius: var(--r-3);
  background: var(--surface);
  box-shadow: var(--sh-2);
  border: 1px solid var(--line);
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  /* Scroll shadow indicators */
  background:
    linear-gradient(to right, var(--surface) 30%, rgba(255,255,255,0)),
    linear-gradient(to right, rgba(0,0,0,0.08), rgba(255,255,255,0) 30%) 0 100%,
    radial-gradient(farthest-side at 0 50%, rgba(0,0,0,0.08), rgba(0,0,0,0)),
    radial-gradient(farthest-side at 100% 50%, rgba(0,0,0,0.08), rgba(0,0,0,0)) 100% 0;
  background-repeat: no-repeat;
  background-color: var(--surface);
  background-size: 40px 100%, 40px 100%, 14px 100%, 14px 100%;
  background-position: 0 0, 100% 0, 0 0, 100% 0;
  background-attachment: local, local, scroll, scroll;
}
table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.95rem;
}
.table-scroll table { min-width: 480px; }
thead { background: var(--surface-2); }
th {
  text-align: left;
  font-weight: 700;
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--muted);
  padding: var(--s-3) var(--s-4);
  border-bottom: 1px solid var(--line);
  white-space: nowrap;
}
td {
  padding: var(--s-3) var(--s-4);
  border-bottom: 1px solid var(--line);
  vertical-align: top;
}
tbody tr { transition: background var(--t-fast); }
tbody tr:hover { background: var(--surface-2); }
tbody tr:last-child td { border-bottom: 0; }
tbody tr:nth-child(even) { background: rgba(241, 237, 231, 0.35); }
tbody tr:nth-child(even):hover { background: var(--surface-2); }

/* For standalone tables without .table-scroll wrapper, still look good */
article > table {
  border-radius: var(--r-3);
  background: var(--surface);
  box-shadow: var(--sh-2);
  border: 1px solid var(--line);
  overflow: hidden;
  margin: var(--s-5) 0;
}

/* =================================================================
   FAQ accordion (<details>/<summary>)
   ================================================================= */
.faq-list { display: flex; flex-direction: column; gap: var(--s-3); margin: var(--s-5) 0; }
.faq-item {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--r-3);
  box-shadow: var(--sh-1);
  transition: box-shadow var(--t-base), border-color var(--t-base);
  overflow: hidden;
}
.faq-item[open] {
  border-color: var(--accent);
  box-shadow: var(--sh-3);
}
.faq-item > summary {
  list-style: none;
  cursor: pointer;
  padding: var(--s-4) var(--s-5);
  font-weight: 600;
  font-size: 1rem;
  color: var(--fg);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--s-4);
  transition: background var(--t-fast);
}
.faq-item > summary::-webkit-details-marker { display: none; }
.faq-item > summary:hover { background: var(--surface-2); }
.faq-item > summary::after {
  content: "";
  flex-shrink: 0;
  display: inline-block;
  width: 12px;
  height: 12px;
  border-right: 2px solid var(--accent);
  border-bottom: 2px solid var(--accent);
  transform: rotate(45deg);
  margin-top: -4px;
  transition: transform var(--t-base);
}
.faq-item[open] > summary::after {
  transform: rotate(-135deg);
  margin-top: 4px;
}
.faq-item .faq-answer {
  padding: 0 var(--s-5) var(--s-5) var(--s-5);
  color: var(--fg);
  font-size: 0.97rem;
  line-height: 1.65;
  border-top: 1px solid var(--line);
  padding-top: var(--s-4);
  animation: faq-open var(--t-base) ease;
}
.faq-item .faq-answer p { margin: var(--s-3) 0 0 0; }
.faq-item .faq-answer p:first-child { margin-top: 0; }
@keyframes faq-open {
  from { opacity: 0; transform: translateY(-4px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* =================================================================
   Process / How-To steps
   ================================================================= */
.process-steps {
  display: flex;
  flex-direction: column;
  gap: var(--s-4);
  margin: var(--s-5) 0;
  counter-reset: process;
  list-style: none;
  padding-left: 0;
}
.process-steps > li {
  position: relative;
  padding: var(--s-4) var(--s-5) var(--s-4) calc(var(--s-7) + var(--s-3));
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--r-3);
  box-shadow: var(--sh-1);
  transition: transform var(--t-fast), box-shadow var(--t-fast);
  margin: 0;
  counter-increment: process;
}
.process-steps > li:hover { transform: translateY(-2px); box-shadow: var(--sh-3); border-color: var(--accent); }
.process-steps > li::before {
  content: counter(process);
  position: absolute;
  top: var(--s-4);
  left: var(--s-4);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--accent);
  color: #fff;
  font-weight: 700;
  font-size: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(184, 52, 26, 0.35);
}
.process-steps > li::marker { content: none; }
.process-steps > li strong:first-child {
  display: block;
  margin-bottom: var(--s-1);
  font-size: 1.05rem;
  color: var(--fg);
  line-height: 1.3;
}

/* =================================================================
   Related-services grid — card-style links used at the bottom of
   brand-repair / brand-spindle / brand-way-covers pages.
   ================================================================= */
.related-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: var(--s-3);
  margin: var(--s-4) 0 0 0;
  list-style: none;
  padding: 0;
}
.related-grid li { margin: 0; }
.related-grid a {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--s-3);
  padding: var(--s-4);
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--r-3);
  box-shadow: var(--sh-1);
  text-decoration: none !important;
  color: var(--fg) !important;
  font-weight: 600;
  transition: transform var(--t-fast), box-shadow var(--t-fast),
              border-color var(--t-fast), color var(--t-fast);
}
.related-grid a::after {
  content: "";
  display: inline-block;
  width: 8px;
  height: 8px;
  border-right: 2px solid currentColor;
  border-top: 2px solid currentColor;
  transform: rotate(45deg);
  opacity: 0.45;
  transition: transform var(--t-fast), opacity var(--t-fast);
  flex-shrink: 0;
}
.related-grid a:hover {
  border-color: var(--accent);
  color: var(--accent) !important;
  transform: translateY(-2px);
  box-shadow: var(--sh-3);
}
.related-grid a:hover::after { opacity: 1; transform: rotate(45deg) translate(2px, -2px); }
.related-coverage {
  margin: var(--s-4) 0 0 0;
  color: var(--muted);
  font-size: 0.9rem;
}

/* =================================================================
   Coverage map — Leaflet-based service area visualization.
   Hub variant: all 7 states with served cities pinned + Waterloo origin.
   State variant: one state outline with served cities pinned + Waterloo.
   City variant: city location + driving route to Waterloo.
   Leaflet CSS+JS is loaded conditionally only on pages that emit a
   .coverage-map element (see the loader script in markdown_to_html
   below).
   ================================================================= */
.coverage-map {
  max-width: var(--max-wide);
  margin: var(--s-5) auto;
  height: 460px;
  background: var(--surface-2);
  border: 1px solid var(--line);
  border-radius: var(--r-3);
  box-shadow: var(--sh-2);
  overflow: hidden;
  position: relative;
}
.coverage-map--city { height: 360px; }
.coverage-map--hub  { height: 520px; }
.coverage-map-empty {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  text-align: center;
  padding: var(--s-4);
  color: var(--muted);
  font-size: 0.92rem;
  pointer-events: none;
  z-index: 1;
}
.coverage-map-empty::before {
  content: "🗺";
  font-size: 2rem;
  margin-bottom: var(--s-2);
  opacity: 0.5;
}
.coverage-map.is-loaded .coverage-map-empty { display: none; }
.coverage-map .leaflet-container {
  background: var(--surface-2);
  font-family: inherit;
}
/* Style the popups to match the site */
.coverage-map .leaflet-popup-content-wrapper {
  border-radius: var(--r-2);
  box-shadow: var(--sh-3);
}
.coverage-map .leaflet-popup-content {
  margin: 0.75rem 1rem;
  font-size: 0.9rem;
  line-height: 1.45;
}
.coverage-map .leaflet-popup-content a {
  color: var(--accent);
  font-weight: 600;
  text-decoration: none;
}
.coverage-map .leaflet-popup-content a:hover { text-decoration: underline; }
.coverage-map-caption {
  max-width: var(--max-wide);
  margin: calc(var(--s-3) * -1) auto var(--s-5);
  padding: 0 var(--s-3);
  font-size: 0.85rem;
  color: var(--muted);
  text-align: center;
  font-style: italic;
}
@media (max-width: 600px) {
  .coverage-map { height: 380px; }
  .coverage-map--city { height: 280px; }
  .coverage-map--hub  { height: 420px; }
}

/* =================================================================
   Insights — pillar landing + article page styling.

   Used by /insights/ pillar pages, /insights/{pillar}/{article}/
   pages, and the /insights/ index. The .insight-* prefix keeps the
   stylesheet self-contained.

   ACCESSIBILITY NOTES (WCAG 2.1 AA targets)
   - Body copy on .insight-hero uses --fg (#1a1a1a) on --surface-3
     (#f1ede7): ≈ 16:1. Well above 4.5:1 minimum for normal text.
   - .insight-eyebrow uses --accent-dark (#8c2510) on --surface-3:
     ≈ 6.3:1. Above 4.5:1 minimum even though the eyebrow text is
     small (12px ≈ 9pt — treated as "normal" text by WCAG).
   - .insight-card-tag uses --accent-dark on a 92%-surface tint:
     ≈ 6.2:1. Comfortable margin.
   - .insight-meta uses --muted (#5a5a5a) on --bg (#ffffff): ≈ 7.5:1.
   - All interactive elements get :focus-visible rings via the
     global .focus-ring tokens that apply to every <a> and <button>.
   - prefers-reduced-motion zeroes the transform/opacity transitions
     on .insight-card and .insight-pillar-card.
   ================================================================= */

/* Editorial hero — used on /insights/ index + each pillar landing.
   Replaces the video hero with a quiet, text-focused band so the
   page reads as long-form editorial content rather than a marketing
   landing. Centered text, generous padding, no images. */
.insight-hero {
  position: relative;
  width: 100%;
  background:
    radial-gradient(120% 80% at 50% 0%, rgba(184, 52, 26, 0.05), transparent 60%),
    var(--surface-3);
  border-bottom: 1px solid var(--line);
  padding: clamp(3rem, 7vw, 5rem) var(--s-5) clamp(2.5rem, 6vw, 4rem);
}
.insight-hero-inner {
  max-width: 760px;
  margin: 0 auto;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.insight-hero-eyebrow {
  display: inline-block;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--accent-dark);
  background: rgba(184, 52, 26, 0.10);
  border: 1px solid rgba(184, 52, 26, 0.20);
  border-radius: var(--r-pill);
  padding: 0.32rem 0.78rem;
  margin: 0 0 var(--s-4) 0;
}
.insight-hero h1 {
  font-size: clamp(1.85rem, 4vw, 2.8rem);
  line-height: 1.12;
  letter-spacing: -0.02em;
  font-weight: 800;
  margin: 0 0 var(--s-4) 0;
  max-width: 22ch;
  color: var(--fg);
}
.insight-hero h1::before { display: none; } /* override the global h2-rule accent */
.insight-hero-lede {
  font-size: clamp(1.05rem, 1.25vw, 1.18rem);
  line-height: 1.6;
  color: var(--fg);
  margin: 0 0 var(--s-5) 0;
  max-width: 60ch;
}
.insight-hero-cta {
  display: flex;
  gap: var(--s-3);
  flex-wrap: wrap;
  justify-content: center;
  margin: 0;
}

@media (max-width: 600px) {
  .insight-hero { padding: var(--s-5) var(--s-4) var(--s-5); }
  .insight-hero-inner { text-align: left; align-items: flex-start; }
  .insight-hero-lede { font-size: 1rem; }
  .insight-hero-cta { width: 100%; flex-direction: column; }
  .insight-hero-cta > * { width: 100%; justify-content: center; }
}

/* Pillar tile grid (insights index page) */
.insight-pillar-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--s-4);
  margin: var(--s-5) 0 var(--s-6) 0;
  list-style: none;
  padding: 0;
}
.insight-pillar-card { margin: 0; }
.insight-pillar-card a {
  display: flex;
  flex-direction: column;
  height: 100%;
  text-decoration: none !important;
  color: var(--fg) !important;
  background: var(--surface);
  padding: var(--s-5);
  border-radius: var(--r-3);
  border: 1px solid var(--line);
  box-shadow: var(--sh-1);
  transition: transform var(--t-base), box-shadow var(--t-base), border-color var(--t-base);
}
.insight-pillar-card a:hover {
  transform: translateY(-3px);
  box-shadow: var(--sh-3);
  border-color: var(--accent);
}
.insight-pillar-card a:focus-visible {
  outline: 3px solid var(--accent-dark);
  outline-offset: 3px;
}
.insight-pillar-eyebrow {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--accent-dark);  /* 6.7:1 on white — safer than --accent for small text */
  font-weight: 700;
}
.insight-pillar-card h3 { margin: var(--s-2) 0; font-size: 1.18rem; color: var(--fg); }
.insight-pillar-card p { color: var(--fg); margin: var(--s-1) 0 var(--s-3) 0; font-size: 0.95rem; flex-grow: 1; }
.insight-pillar-counts {
  color: var(--muted);
  font-size: 0.85rem;
  margin: var(--s-2) 0 var(--s-3) 0 !important;
  flex-grow: 0 !important;
}

/* Cluster card grid (pillar pages + recent-articles strip on index) */
.insight-cluster-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--s-4);
  margin: var(--s-4) 0 var(--s-6) 0;
  list-style: none;
  padding: 0;
}
.insight-card { margin: 0; }
.insight-card > a,
.insight-card > div {
  display: flex;
  flex-direction: column;
  height: 100%;
  text-decoration: none !important;
  color: var(--fg) !important;
  background: var(--surface);
  padding: var(--s-4);
  border-radius: var(--r-3);
  border: 1px solid var(--line);
  box-shadow: var(--sh-1);
  transition: transform var(--t-base), box-shadow var(--t-base), border-color var(--t-base);
}
.insight-card--published > a:hover {
  transform: translateY(-3px);
  box-shadow: var(--sh-3);
  border-color: var(--accent);
}
.insight-card--published > a:focus-visible {
  outline: 3px solid var(--accent-dark);
  outline-offset: 3px;
}
.insight-card--planned > div {
  background: color-mix(in srgb, var(--surface) 94%, var(--accent) 6%);
  border-style: dashed;
  /* No opacity reduction — opacity hurts text contrast. The dashed
     border + tinted background communicates "planned" without dimming. */
}
.insight-card-tag {
  display: inline-block;
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 700;
  color: var(--accent-dark);  /* 6.7:1 on tinted bg — comfortable for small caps */
  background: rgba(184, 52, 26, 0.10);
  border: 1px solid rgba(184, 52, 26, 0.18);
  padding: 0.22rem 0.55rem;
  border-radius: var(--r-pill);
  margin-bottom: var(--s-2);
}
.insight-card-tag--planned {
  color: #3d3d3d;  /* darker than --muted so the chip text passes AAA */
  background: color-mix(in srgb, var(--muted) 14%, transparent);
  border-color: color-mix(in srgb, var(--muted) 28%, transparent);
}
.insight-card h3 { margin: var(--s-1) 0; font-size: 1.08rem; line-height: 1.3; color: var(--fg); }
.insight-card p { color: var(--fg); margin: var(--s-2) 0 var(--s-3) 0; font-size: 0.92rem; flex-grow: 1; }
.insight-card-query { color: var(--muted) !important; }
.insight-card-query em { font-style: italic; color: var(--fg); }

/* Article page — meta strip + eyebrow above the H1 */
.insight-eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--accent-dark);  /* WCAG: 6.7:1 on white, safer than --accent */
  margin: 0 0 var(--s-2) 0;
}
.insight-h1 {
  font-size: clamp(1.75rem, 3.6vw, 2.5rem);
  line-height: 1.15;
  margin: 0 0 var(--s-3) 0;
  letter-spacing: -0.015em;
  color: var(--fg);
}
.insight-h1::before { display: none; } /* override the global h2-rule accent if any */
.insight-meta {
  color: #4a4a4a;  /* 8.9:1 on white — slightly darker than --muted for AAA */
  font-size: 0.95rem;
  margin: 0 0 var(--s-5) 0;
}

/* Key Takeaways block — scoped to insights article body only. The
   block is the first <h2 id="key-takeaways"> followed immediately
   by a <ul>. We use the H2's stable id (added by the markdown
   converter from the heading slug) as the anchor, not a fragile
   :first-of-type structural rule that would fire on non-insights
   pages that happen to have a UL after their first H2. */
.insights-article main article h2#key-takeaways {
  /* Visually hide the Key Takeaways heading text but keep it for AT.
     The styled callout box below is the visible affordance. The H2
     is still in the document outline. */
  position: absolute !important;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
.insights-article main article h2#key-takeaways + ul,
.insight-takeaways {
  background: color-mix(in srgb, var(--surface) 88%, var(--accent) 6%);
  border: 1px solid color-mix(in srgb, var(--accent) 22%, var(--line));
  border-left: 4px solid var(--accent-dark);
  border-radius: var(--r-2);
  padding: var(--s-4) var(--s-4) var(--s-4) calc(var(--s-4) + 1rem);
  margin: 0 0 var(--s-5) 0;
  list-style: disc;
  position: relative;
}
.insights-article main article h2#key-takeaways + ul::before,
.insight-takeaways::before {
  /* Visible "Key Takeaways" label for sighted users — replaces the
     visually-hidden H2. */
  content: "Key Takeaways";
  display: block;
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: 700;
  color: var(--accent-dark);
  margin: 0 0 var(--s-3) calc(-1rem);
  list-style: none;
}
.insights-article main article h2#key-takeaways + ul li,
.insight-takeaways li {
  margin: 0.4rem 0;
  color: var(--fg);
  font-size: 1.02rem;
  line-height: 1.55;
}

/* Tail CTA on every article — sits in the natural flow, not a sticky bar. */
.insight-cta {
  margin: var(--s-6) 0 var(--s-4) 0;
  padding: var(--s-5);
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--r-3);
  box-shadow: var(--sh-1);
}
.insight-cta p:first-child {
  margin: 0 0 var(--s-3) 0;
  font-size: 1.05rem;
}
.insight-cta p:last-child {
  margin: 0;
  display: flex;
  gap: var(--s-3);
  flex-wrap: wrap;
}
.insight-cta .cta-button,
.insight-cta .cta-phone {
  /* uses the existing button styles */
}

/* Definitional opener — first paragraph under each H2 in an
   insights article gets a slightly heavier weight + size to
   reinforce the "quote me" cue. Subtle, not screaming. Scoped to
   .insights-article so this doesn't affect other page types. */
.insights-article main article h2 + p {
  font-size: 1.08rem;
  line-height: 1.65;
  color: var(--fg);
}

/* Article body link styling — make in-body links scannable without
   being noisy. Underline on hover; clear focus ring. */
.insights-article main article p a,
.insights-article main article li a {
  color: var(--accent-dark);
  text-decoration: underline;
  text-decoration-thickness: 1px;
  text-underline-offset: 2px;
  text-decoration-color: rgba(140, 37, 16, 0.45);
  transition: text-decoration-color var(--t-fast), color var(--t-fast);
}
.insights-article main article p a:hover,
.insights-article main article li a:hover {
  text-decoration-color: var(--accent-dark);
  color: var(--accent-dark);
}
.insights-article main article p a:focus-visible,
.insights-article main article li a:focus-visible {
  outline: 3px solid var(--accent-dark);
  outline-offset: 2px;
  border-radius: 2px;
}

/* Body paragraph rhythm in insights articles. */
.insights-article main article p {
  font-size: 1.05rem;
  line-height: 1.7;
  color: var(--fg);
}

/* Sources & references tail */
.insight-sources,
section.insight-sources {
  margin-top: var(--s-6);
  padding-top: var(--s-5);
  border-top: 1px solid var(--line);
}
.insight-sources h2 { font-size: 1.05rem; color: var(--fg); }
.insight-sources li { font-size: 0.92rem; color: #4a4a4a; }

/* Insights CTA button focus state */
.insight-cta a:focus-visible {
  outline: 3px solid var(--accent-dark);
  outline-offset: 3px;
}

@media (max-width: 600px) {
  .insight-pillar-card a { padding: var(--s-4); }
  .insight-h1 { font-size: 1.55rem; }
  .insight-cta { padding: var(--s-4); }
  .insights-article main article p { font-size: 1rem; line-height: 1.65; }
}

/* Reduced-motion: zero out the lift/transition on cards. */
@media (prefers-reduced-motion: reduce) {
  .insight-pillar-card a,
  .insight-card > a,
  .insights-article main article p a,
  .insights-article main article li a {
    transition: none !important;
  }
  .insight-pillar-card a:hover,
  .insight-card--published > a:hover {
    transform: none !important;
  }
}

/* =================================================================
   MachineLookup — site-wide model number lookup.
   Powered by /data/machines.json. Renders a search input that
   fuzzy-matches the user's typed model and routes to the matching
   series-spoke page across all 6 brands.
   ================================================================= */
.machine-lookup {
  max-width: var(--max-wide);
  margin: var(--s-5) auto;
  padding: var(--s-5);
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--r-3);
  box-shadow: var(--sh-2);
  position: relative;
}
.machine-lookup-label {
  display: block;
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted);
  font-weight: 700;
  margin-bottom: var(--s-2);
}
.machine-lookup-input {
  font: inherit;
  width: 100%;
  padding: 0.85rem 1rem;
  font-size: 1.02rem;
  border: 1.5px solid var(--line);
  border-radius: var(--r-2);
  background: var(--surface);
  transition: border-color var(--t-fast), box-shadow var(--t-fast);
}
.machine-lookup-input:hover { border-color: var(--muted); }
.machine-lookup-input:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: var(--sh-focus);
}
.machine-lookup-results {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 0.4rem;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--r-3);
  box-shadow: var(--sh-4);
  z-index: 40;
  overflow: hidden;
  max-height: 360px;
  overflow-y: auto;
}
.machine-lookup-results[hidden] { display: none; }
.machine-lookup-result {
  display: grid;
  grid-template-columns: auto 1fr auto auto;
  align-items: baseline;
  gap: 0.6rem;
  padding: 0.75rem 1rem;
  text-decoration: none !important;
  color: var(--fg) !important;
  border-bottom: 1px solid var(--line);
  transition: background var(--t-fast), padding-left var(--t-fast);
}
.machine-lookup-result:last-child { border-bottom: 0; }
.machine-lookup-result:hover,
.machine-lookup-result:focus {
  background: var(--surface-2);
  color: var(--accent) !important;
  padding-left: 1.2rem;
  outline: none;
}
.machine-lookup-result-brand {
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--muted);
  padding: 0.2rem 0.5rem;
  border-radius: var(--r-1);
  background: var(--surface-2);
}
.machine-lookup-result-model {
  font-weight: 700;
  font-size: 0.98rem;
}
.machine-lookup-result-series {
  color: var(--muted);
  font-size: 0.85rem;
}
.machine-lookup-result-arrow {
  font-size: 1.1rem;
  color: var(--accent);
  opacity: 0.6;
  transition: opacity var(--t-fast), transform var(--t-fast);
}
.machine-lookup-result:hover .machine-lookup-result-arrow,
.machine-lookup-result:focus .machine-lookup-result-arrow {
  opacity: 1;
  transform: translateX(2px);
}
.machine-lookup-empty {
  padding: 1rem 1.25rem;
  color: var(--muted);
  font-size: 0.92rem;
  line-height: 1.5;
}
.machine-lookup-empty a { color: var(--accent); font-weight: 600; }

@media (max-width: 600px) {
  .machine-lookup { padding: var(--s-4); }
  .machine-lookup-result {
    grid-template-columns: 1fr auto;
    grid-template-areas:
      "brand arrow"
      "model arrow"
      "series series";
    gap: 0.25rem 0.6rem;
  }
  .machine-lookup-result-brand { grid-area: brand; justify-self: start; }
  .machine-lookup-result-model { grid-area: model; }
  .machine-lookup-result-series { grid-area: series; }
  .machine-lookup-result-arrow { grid-area: arrow; align-self: center; }
}

/* Browse-by-X lists on hub pages (Browse by Series / Control / Service).
   Each <li> is a card-style link with bolded label + supporting copy. */
.browse-list {
  list-style: none;
  padding: 0;
  margin: var(--s-4) 0 var(--s-5) 0;
  display: grid;
  gap: var(--s-3);
}
.browse-list > li { margin: 0; }
.browse-list > li > a {
  display: block;
  padding: var(--s-4) var(--s-5);
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--r-3);
  box-shadow: var(--sh-1);
  text-decoration: none !important;
  color: var(--fg) !important;
  font-weight: 500;
  line-height: 1.5;
  transition: transform var(--t-fast), box-shadow var(--t-fast),
              border-color var(--t-fast);
  position: relative;
  padding-right: calc(var(--s-5) + 18px);
}
.browse-list > li > a::after {
  content: "";
  position: absolute;
  top: 50%;
  right: var(--s-4);
  width: 9px;
  height: 9px;
  border-right: 2px solid var(--muted);
  border-top: 2px solid var(--muted);
  transform: translateY(-50%) rotate(45deg);
  opacity: 0.5;
  transition: opacity var(--t-fast), transform var(--t-fast),
              border-color var(--t-fast);
}
.browse-list > li > a:hover,
.browse-list > li > a:focus {
  transform: translateY(-2px);
  box-shadow: var(--sh-3);
  border-color: var(--accent);
  outline: none;
}
.browse-list > li > a:hover::after,
.browse-list > li > a:focus::after {
  opacity: 1;
  border-color: var(--accent);
  transform: translateY(-50%) rotate(45deg) translate(2px, -2px);
}
.browse-list > li > a strong {
  color: var(--fg);
  font-weight: 700;
  display: inline;
  margin-right: 0.4rem;
}
.browse-list > li > a:hover strong { color: var(--accent); }

/* "Models We Service" — pill chips instead of dense vertical list */
.model-chips {
  display: flex;
  flex-wrap: wrap;
  gap: var(--s-2);
  list-style: none;
  padding: 0;
  margin: var(--s-3) 0 var(--s-4) 0;
}
.model-chips li {
  margin: 0;
  padding: 0.4rem 0.95rem;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--r-pill);
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--fg);
}

/* =================================================================
   Pull-card / info-box / trust footer aside
   ================================================================= */
.trust-footer, aside.trust-footer {
  margin: var(--s-6) 0;
  padding: var(--s-5);
  background: linear-gradient(135deg, var(--surface-2), var(--surface-3));
  border-radius: var(--r-3);
  border: 1px solid var(--line);
  box-shadow: var(--sh-1);
}
.trust-footer > p { margin: var(--s-3) 0; }
.trust-footer > p:first-child { margin-top: 0; }
.trust-footer > p:last-child { margin-bottom: 0; }
.trust-footer .customer-quote {
  font-style: italic;
  color: var(--fg);
  border-left: 3px solid var(--accent);
  padding-left: var(--s-4);
  margin-top: var(--s-4);
}

/* =================================================================
   Sticky mobile CTA bar
   ================================================================= */
.mobile-cta-bar {
  display: none;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
  padding: var(--s-2) var(--s-3);
  padding-bottom: calc(var(--s-2) + env(safe-area-inset-bottom));
  gap: var(--s-2);
  background: rgba(255, 255, 255, 0.96);
  backdrop-filter: saturate(180%) blur(10px);
  -webkit-backdrop-filter: saturate(180%) blur(10px);
  border-top: 1px solid var(--line);
  box-shadow: 0 -4px 16px rgba(0, 0, 0, 0.06);
}
.mobile-cta-bar a {
  flex: 1 1 0;
  text-align: center;
  padding: 0.9rem 0.5rem;
  font-weight: 700;
  font-size: 0.95rem;
  text-decoration: none !important;
  border-radius: var(--r-pill);
  transition: background var(--t-fast), color var(--t-fast);
}
.mobile-cta-bar .mcta-phone {
  color: var(--fg) !important;
  background: var(--surface);
  border: 1.5px solid var(--line);
}
.mobile-cta-bar .mcta-phone:active { background: var(--surface-2); }
.mobile-cta-bar .mcta-quote {
  color: #fff !important;
  background: var(--accent);
  box-shadow: var(--sh-2);
}
.mobile-cta-bar .mcta-quote:active { background: var(--accent-dark); }

@media (max-width: 767px) {
  .mobile-cta-bar { display: flex; }
  body { padding-bottom: calc(var(--sticky-cta-height) + env(safe-area-inset-bottom)); }
}

/* =================================================================
   Footer
   ================================================================= */
.site-footer {
  border-top: 1px solid var(--line);
  padding: var(--s-7) var(--s-5) var(--s-6);
  color: var(--muted);
  font-size: 0.92rem;
  margin-top: var(--s-8);
  background: var(--surface-2);
}
.footer-inner {
  max-width: var(--max-wide);
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1.6fr 1fr;
  gap: var(--s-6);
  align-items: start;
}
.footer-col p { margin: var(--s-2) 0; }
.footer-brand { color: var(--fg); font-weight: 700; font-size: 1.05rem; margin-top: 0 !important; }
.footer-phone {
  color: var(--accent-dark);
  font-weight: 700;
  font-size: 1.1rem;
  text-decoration: none;
}
.footer-phone:hover { text-decoration: underline; }
.footer-states { color: var(--muted); max-width: 48ch; }

/* Hours block */
.footer-hours-title {
  color: var(--fg);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  font-size: 0.78rem;
  margin: 0 0 var(--s-2) 0 !important;
}
.footer-hours {
  margin: 0 0 var(--s-3) 0;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}
.footer-hours-row {
  display: flex;
  justify-content: space-between;
  gap: var(--s-4);
  max-width: 18rem;
  border-bottom: 1px dotted var(--line);
  padding-bottom: 0.3rem;
}
.footer-hours-row dt { color: var(--fg); font-weight: 600; margin: 0; }
.footer-hours-row dd { color: var(--muted); margin: 0; }
.footer-hours-note { font-size: 0.82rem; color: var(--muted); font-style: italic; max-width: 26ch; }

@media (max-width: 700px) {
  .footer-inner { grid-template-columns: 1fr; gap: var(--s-5); }
}

/* =================================================================
   Responsive overrides
   ================================================================= */
@media (max-width: 900px) {
  main { padding: 0 var(--s-4); }
  article { margin: var(--s-5) auto var(--s-7) auto; }
  h2 { margin: var(--s-6) 0 var(--s-3) 0; }
  .faq-item > summary { padding: var(--s-4); }
  .faq-item .faq-answer { padding-left: var(--s-4); padding-right: var(--s-4); padding-bottom: var(--s-4); }
  .process-steps > li { padding-left: calc(var(--s-7) + var(--s-2)); padding-right: var(--s-4); }
}

@media (max-width: 800px) {
  .site-header {
    flex-direction: column;
    align-items: stretch;
    gap: var(--s-2);
    padding: var(--s-3) var(--s-4);
    position: static;
  }
  .site-header .brand { justify-content: center; }
  .site-header .brand img { height: 56px; }
  .site-header nav { width: 100%; }
  .site-header nav > ul { flex-direction: column; gap: 0; width: 100%; }
  .site-header nav > ul > li { width: 100%; }
  .site-header nav > ul > li > a,
  .site-header nav > ul > li > .menu-label {
    width: 100%;
    padding: 0.65rem 0.75rem;
    border-radius: var(--r-1);
    border-bottom: 1px solid var(--line);
    justify-content: space-between;
  }
  .site-header nav .dropdown {
    position: static;
    box-shadow: none;
    border: none;
    padding: var(--s-1) 0 var(--s-2) 0;
    margin: 0;
    opacity: 1;
    visibility: visible;
    transform: none;
    transition: none;
    min-width: 0;
    background: var(--surface-2);
    border-radius: 0;
  }
  .site-header nav .dropdown a { padding: 0.45rem 1.25rem; }
  .site-header nav a.cta-nav {
    width: 100%;
    text-align: center;
    justify-content: center;
    margin-left: 0;
    margin-top: var(--s-2);
    padding: 0.75rem 1.25rem;
  }
}

@media (max-width: 600px) {
  body { font-size: 16px; }
  h1 { font-size: clamp(1.7rem, 7vw, 2.3rem); }
  h2 { font-size: 1.3rem; }
  article { margin: var(--s-4) auto var(--s-6) auto; }
  .cta-row { flex-direction: column; align-items: stretch; }
  .cta-row .cta-button,
  .cta-row .cta-phone { width: 100%; justify-content: center; }
  .hero-figure img { max-height: 280px; }
  blockquote { padding: var(--s-3) var(--s-4); }
  blockquote p { padding-left: 1.25rem; }
  th, td { padding: var(--s-2) var(--s-3); font-size: 0.9rem; }
}
"""


# ---------- Section banding (alternating full-bleed sections) ----------

_HERO_FIGURE_RE = re.compile(
    r'<figure\s+class="hero-figure"[^>]*>.*?</figure>',
    re.DOTALL | re.IGNORECASE,
)


def _maybe_two_column_hero(intro_html):
    """If the intro fragment contains a <figure class="hero-figure"> element,
    split it out into a two-column hero: text content on the left,
    figure on the right. Otherwise return the fragment unchanged.

    Used to give every page type (hub, brand, state with hero image) the
    same two-column hero treatment the homepage has."""
    m = _HERO_FIGURE_RE.search(intro_html)
    if not m:
        return intro_html
    figure_html = m.group(0)
    text_html = (intro_html[:m.start()] + intro_html[m.end():]).strip()
    if not text_html:
        return intro_html  # only a figure; no point in two-column
    return (
        '<div class="page-hero">\n'
        f'  <div class="page-hero-text">\n{text_html}\n  </div>\n'
        f'  <div class="page-hero-image">\n{figure_html}\n  </div>\n'
        '</div>'
    )


def wrap_into_sections(body_html, layout="default"):
    """Wrap a body fragment into alternating-color full-bleed sections.

    Split positions: each <h2> opening tag begins a new section. Content
    before the first <h2> becomes the intro section.

    layout='wide' makes the inner content container use --max-wide (for
    homepage + hub pages with tiles / brand grids); 'default' uses --max
    (72ch readable column).

    If the leading chunk is already a <section class="home-hero">, it is
    passed through inside its own page-section-hero band (transparent bg,
    its own radial gradient backdrop preserved).
    """
    inner_klass = "section-inner"
    if layout == "wide":
        inner_klass += " wide"

    parts = re.split(r'(?=<h2\b)', body_html)
    out = []
    band_idx = 0

    for i, part in enumerate(parts):
        s = part.strip()
        if not s:
            continue

        # Home-hero / brand-hero: already wrapped by the generator with
        # its own structure. Pass through inside a hero band without the
        # two-column transformation and without alternating-color colour.
        if i == 0 and (
            s.startswith('<section class="home-hero')
            or s.startswith('<section class="brand-hero')
            or s.startswith('<section class="insight-hero')
            or s.startswith('<section class="quote-hero')
        ):
            out.append(
                f'<section class="page-section page-section-hero">\n'
                f'  <div class="{inner_klass}">\n{s}\n  </div>\n'
                f'</section>'
            )
            continue

        # Intro section (pre-first-h2). If it contains a hero-figure, split
        # it into a two-column hero (text left, image right). Use the hero
        # band styling (no alternating colour).
        if i == 0:
            transformed = _maybe_two_column_hero(s)
            is_two_col = transformed != s
            klass = "page-section page-section-hero page-section-intro" if is_two_col \
                    else "page-section page-section-0 page-section-intro"
            out.append(
                f'<section class="{klass}">\n'
                f'  <div class="{inner_klass}">\n{transformed}\n  </div>\n'
                f'</section>'
            )
            # If we landed on hero band (no colour increment), start the
            # next section as band 1 for visible alternation.
            if is_two_col:
                band_idx = 1
            else:
                band_idx = 1
            continue

        klass = f"page-section page-section-{band_idx % 2}"
        out.append(
            f'<section class="{klass}">\n'
            f'  <div class="{inner_klass}">\n{s}\n  </div>\n'
            f'</section>'
        )
        band_idx += 1

    return "\n".join(out) if out else body_html


# ---------- Site header (single source of truth, used by both generators) ----------

# Top brands surfaced in dropdowns. Picked for industry weight + presence
# across all three service lines (spindle / repair / way-covers).
TOP_BRANDS = [
    ("Mazak",    "mazak"),
    ("Haas",     "haas"),
    ("DMG Mori", "dmg-mori"),
    ("Doosan",   "doosan"),
    ("Okuma",    "okuma"),
    ("Fanuc",    "fanuc"),
]

STATE_NAV = [
    ("Iowa",      "iowa"),
    ("Illinois",  "illinois"),
    ("Wisconsin", "wisconsin"),
    ("Minnesota", "minnesota"),
    ("Nebraska",  "nebraska"),
    ("Missouri",  "missouri"),
    ("Texas",     "texas"),
]


def _service_dropdown(label, hub_path, url_suffix, hub_link_text):
    """Build a service-line dropdown <li>. url_suffix appends to /<service>/<brand-slug>."""
    items = [
        f'<li class="dropdown-section">By Service</li>',
        f'<li><a href="{hub_path}" class="dropdown-all">{hub_link_text} →</a></li>',
        f'<li class="dropdown-divider" aria-hidden="true"></li>',
        f'<li class="dropdown-section">Popular Brands</li>',
    ]
    for name, slug in TOP_BRANDS:
        items.append(f'<li><a href="{hub_path}{slug}{url_suffix}/">{name}</a></li>')
    items.append('<li class="dropdown-divider" aria-hidden="true"></li>')
    items.append(f'<li><a href="{hub_path}" class="dropdown-all">View All Brands →</a></li>')
    inner = "\n        ".join(items)
    return f"""    <li class="has-dropdown">
      <a href="{hub_path}" class="menu-label">{label}</a>
      <ul class="dropdown" role="menu">
        {inner}
      </ul>
    </li>"""


def _service_area_dropdown():
    items = [
        '<li class="dropdown-section">By State</li>',
    ]
    for name, slug in STATE_NAV:
        items.append(f'<li><a href="/service-area/{slug}/">{name}</a></li>')
    items.append('<li class="dropdown-divider" aria-hidden="true"></li>')
    items.append('<li><a href="/service-area/" class="dropdown-all">All Locations →</a></li>')
    inner = "\n        ".join(items)
    return f"""    <li class="has-dropdown">
      <a href="/service-area/" class="menu-label">Service Area</a>
      <ul class="dropdown" role="menu">
        {inner}
      </ul>
    </li>"""


def build_site_header():
    """Return the global <header> markup. Identical across both generators."""
    repairs   = _service_dropdown("Repairs",          "/repairs/",          "-cnc-machine-repair", "All Repairs")
    spindle   = _service_dropdown("Spindle Grinding", "/spindle-grinding/", "-spindle-repair",     "All Spindle Work")
    waycovers = _service_dropdown("Way Covers",       "/way-covers/",       "-cnc-way-covers",     "All Way Covers")
    service_area = _service_area_dropdown()

    insights = _insights_dropdown()

    return f"""<header class="site-header">
  <a class="brand" href="/" aria-label="Midwest CNC Services home">
    <img src="/assets/images/logos/midwest-cnc-logo.png" alt="Midwest CNC Services">
  </a>
  <nav aria-label="Primary">
    <ul>
{repairs}
{spindle}
{waycovers}
{service_area}
{insights}
      <li><a href="/get-a-quote/" class="cta-nav">Get a Quote</a></li>
    </ul>
  </nav>
</header>"""


# ---------- Insights dropdown ----------

INSIGHTS_PILLARS_NAV = [
    ("Spindle Diagnostics",      "spindle-diagnostics"),
    ("CNC Control Systems",      "cnc-control-systems"),
    ("Way Covers Engineering",   "way-covers-engineering"),
    ("Field Service & Logistics", "field-service-logistics"),
    ("Buying & Owning Used CNC", "buying-owning-used-cnc"),
]


def _insights_dropdown():
    items = ['<li class="dropdown-section">Technical Pillars</li>']
    for name, slug in INSIGHTS_PILLARS_NAV:
        items.append(f'<li><a href="/insights/{slug}/">{name}</a></li>')
    items.append('<li class="dropdown-divider" aria-hidden="true"></li>')
    items.append('<li><a href="/insights/" class="dropdown-all">All Insights →</a></li>')
    inner = "\n        ".join(items)
    return f"""    <li class="has-dropdown">
      <a href="/insights/" class="menu-label">Insights</a>
      <ul class="dropdown" role="menu">
        {inner}
      </ul>
    </li>"""


# Business hours — single source of truth. Used by build_site_footer()
# (visible) and by the LocalBusiness openingHoursSpecification schema.
# Edit here to change hours everywhere.
BUSINESS_HOURS = [
    ("Mon–Fri", "7 AM – 3:30 PM"),
    ("Sat–Sun", "Closed"),
]


def build_site_footer():
    """Global <footer>. Single source of truth used by all three
    generators (this module, generate_site_shell, generate_insights_pages).
    Includes NAP, a tap-to-call phone link, business hours, and the
    served-states line."""
    hours_rows = "\n".join(
        f'      <div class="footer-hours-row"><dt>{html.escape(d)}</dt>'
        f'<dd>{html.escape(h)}</dd></div>'
        for d, h in BUSINESS_HOURS
    )
    return f"""<footer class="site-footer">
  <div class="footer-inner">
    <div class="footer-col footer-col-contact">
      <p class="footer-brand">Midwest CNC Services</p>
      <p><a class="footer-phone" href="tel:+13196104341">319-610-4341</a></p>
      <p>Waterloo, Iowa</p>
      <p class="footer-states">Serving shops across Iowa, Illinois, Wisconsin, Minnesota, Nebraska, Missouri, and Texas.</p>
    </div>
    <div class="footer-col footer-col-hours">
      <p class="footer-hours-title">Hours</p>
      <dl class="footer-hours">
{hours_rows}
      </dl>
      <p class="footer-hours-note">Machine down outside these hours? Leave a message — we check it first thing.</p>
    </div>
  </div>
</footer>"""


def render_html(fm, body_html):
    """Wrap the converted body in the full page chrome."""
    title = fm.get("title", "Midwest CNC Services")
    meta_desc = fm.get("meta_description", "")
    h1 = fm.get("h1", "")
    slug = fm.get("slug", "")
    page_type = fm.get("page_type", "")

    # Breadcrumb nav from schema_data
    crumbs_html = ""
    bc = (fm.get("schema_data") or {}).get("breadcrumb", {})
    items = bc.get("itemListElement", []) if isinstance(bc, dict) else []
    if items:
        crumb_lis = []
        for item in items:
            if isinstance(item, dict):
                name = item.get("name", "")
                href = item.get("item", "")
                crumb_lis.append(
                    f'<li><a href="{html.escape(str(href))}">{html.escape(str(name))}</a></li>'
                )
        if crumb_lis:
            crumbs_html = (
                '<nav class="breadcrumbs" aria-label="breadcrumb">\n'
                f'  <ol>\n    {"".join(crumb_lis)}\n  </ol>\n'
                '</nav>'
            )

    # Convert eyebrow + CTA-row + form-placeholder markup post-hoc.
    # The generator emits these as italicized paragraphs / paragraphs that
    # contain CTA links — re-style them here for readability.
    body_html = _stylize(body_html)

    schema_blocks = schema_jsonld(fm)

    # The canonical pulls from the breadcrumb's last item, which is now an
    # absolute URL (fix 8). Use as-is.
    bc = (fm.get("schema_data") or {}).get("breadcrumb", {})
    last_item = ""
    items_for_canonical = bc.get("itemListElement", []) if isinstance(bc, dict) else []
    if items_for_canonical:
        last = items_for_canonical[-1]
        last_item = last.get("item", "") if isinstance(last, dict) else ""
    canonical = last_item if last_item.startswith("http") else f"https://midwestcncservices.com{last_item or '/'}"

    return f"""<!doctype html>
<html lang="en">
<head>
{TRACKING_HEAD}
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{ANALYTICS_HEAD}
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(meta_desc)}">
<link rel="canonical" href="{html.escape(canonical)}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(meta_desc)}">
<meta property="og:type" content="website">
{social_meta(title, meta_desc, canonical)}
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap">
<style>
{CSS}</style>
{schema_blocks}
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
{build_site_header()}
{crumbs_html}
<main id="main">
<article>
{wrap_into_sections(body_html, layout="default")}
</article>
</main>
{build_site_footer()}
<div class="mobile-cta-bar" role="region" aria-label="Quick contact">
  <a class="mcta-phone" href="tel:+13196104341">☎ 319-610-4341</a>
  <a class="mcta-quote" href="#quote">Get a Quote</a>
</div>
{COVERAGE_MAP_LOADER}
</body>
</html>
"""


def _stylize(body_html):
    """Light post-processing of the converted markdown:
       - First <p><em>…</em></p> becomes <p class="eyebrow">…</p>
       - Paragraphs that consist only of CTA links + bullet become a CTA row
       - The italic quote-form placeholder becomes a styled placeholder
    """
    # Placeholder replacements first — convert the italicized build-time
    # placeholders into styled divs before the eyebrow rule runs. Otherwise
    # the eyebrow regex (which matches any leading <p><em>…</em></p>) could
    # accidentally claim the placeholder paragraph on pages that don't emit
    # a real eyebrow line (Amada, Trumpf).
    body_html = re.sub(
        r'<p><em>Quote form rendered here at build time\.</em></p>',
        '<div class="quote-form-placeholder">Quote form rendered here at build time.</div>',
        body_html,
    )
    body_html = re.sub(
        r'<p><em>Rendered by the blog teaser component at build time\.</em></p>',
        '<div class="quote-form-placeholder">Blog teaser block rendered here at build time.</div>',
        body_html,
    )

    # Eyebrow paragraph — only when an <p><em>...</em></p> is the FIRST tag
    # in the article body. Anchors to start-of-string so pages without an
    # eyebrow line (Amada, Trumpf) get no .eyebrow at all.
    body_html = re.sub(
        r'\A(\s*)<p><em>([^<]+)</em></p>',
        r'\1<p class="eyebrow">\2</p>',
        body_html,
        count=1,
    )

    # CTA rows: paragraphs that are a "Get a Quote" link followed optionally
    # by a phone link separated by " · "
    def cta_row(m):
        text = m.group(1)
        text = re.sub(
            r'<a href="#quote">Get a Quote</a>',
            '<a class="cta-button" href="#quote">Get a Quote</a>',
            text,
        )
        text = re.sub(
            r'<a href="tel:\+13196104341">319-610-4341</a>',
            '<a class="cta-phone" href="tel:+13196104341">319-610-4341</a>',
            text,
        )
        return f'<div class="cta-row">{text}</div>'

    body_html = re.sub(
        r'<p>((?:[^<]*<a[^>]*>(?:Get a Quote|319-610-4341)</a>[^<]*)+)</p>',
        cta_row,
        body_html,
    )

    return body_html


# ---------- Driver ----------

def output_path_for(fm):
    """Mirror the canonical URL into the public/ tree as
    public/<canonical-path>/index.html. Falls back to public/<slug>.html
    if the canonical can't be parsed."""
    bc = (fm.get("schema_data") or {}).get("breadcrumb", {})
    items = bc.get("itemListElement", []) if isinstance(bc, dict) else []
    if items and isinstance(items[-1], dict):
        item = items[-1].get("item", "")
        if item.startswith("https://midwestcncservices.com"):
            item = item[len("https://midwestcncservices.com"):]
        item = item.strip("/")
        if item:
            return os.path.join(OUTDIR, item, "index.html")
    slug = fm.get("slug", "page")
    return os.path.join(OUTDIR, f"{slug}.html")


def _resolve_targets(args):
    """When args are given, resolve each to a markdown path. Accepts either
    a slug (looked up in every CONTENT_DIRS, returning all matches) or an
    explicit path. When no args, return every .md across all three dirs."""
    md_paths = []
    if args:
        for arg in args:
            if os.path.isabs(arg) or os.path.sep in arg:
                if arg.endswith(".md") and os.path.exists(arg):
                    md_paths.append(arg)
                continue
            # Treat as slug — find in any content dir
            for d in CONTENT_DIRS:
                p = os.path.join(d, f"{arg}.md")
                if os.path.exists(p):
                    md_paths.append(p)
    else:
        for d in CONTENT_DIRS:
            if not os.path.isdir(d):
                continue
            for f in sorted(os.listdir(d)):
                if f.endswith(".md"):
                    md_paths.append(os.path.join(d, f))
    return md_paths


def _kind_for_path(md_path):
    """Tag the source dir for nicer reporting."""
    for d in CONTENT_DIRS:
        if md_path.startswith(d + os.sep):
            return os.path.basename(d)
    return "?"


def main():
    md_paths = _resolve_targets(sys.argv[1:])
    written = 0
    for md_path in md_paths:
        src = open(md_path).read()
        fm, body = parse_frontmatter(src)
        body_html = md_body_to_html(body)
        page_html = render_html(fm, body_html)
        out_path = output_path_for(fm)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w") as f:
            f.write(page_html)
        written += 1
        size_kb = max(1, os.path.getsize(out_path) // 1024)
        rel = os.path.relpath(out_path, REPO)
        kind = _kind_for_path(md_path)
        draft = " [DRAFT]" if fm.get("draft") else ""
        print(f"  ✓ [{kind:<16}] {fm.get('slug',''):<16} → {rel}  ({size_kb} KB){draft}")
    print(f"\n  Total written: {written}")


if __name__ == "__main__":
    main()

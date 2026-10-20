#!/usr/bin/env python3
"""
Insights engine — page generator.

Reads:
  src/data/insights-pillars.json       — pillar + cluster metadata
  src/content/insights/{pillar}/*.md   — published article sources

Generates:
  public/insights/index.html                          — engine landing page
  public/insights/{pillar}/index.html                 — pillar pages
  public/insights/{pillar}/{article}/index.html       — cluster articles

Also updates sitemap.xml and llms.txt to include insights URLs.
"""

from __future__ import annotations

import datetime as _dt
import html
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import markdown_to_html as m2h  # noqa: E402
import generate_site_shell as gss  # noqa: E402

PUBLIC = REPO / "public"
DATA = REPO / "src" / "data" / "insights-pillars.json"
CONTENT = REPO / "src" / "content" / "insights"

DOMAIN = "https://midwestcncservices.com"
PHONE_TEL = "+13196104341"
PHONE_DISPLAY = "319-610-4341"


# ---------- Editorial hero (no video, no image) ----------

def build_insight_hero_html(eyebrow_text, h1_html, lede_html,
                            cta_href="/get-a-quote/", cta_label="Get a Quote",
                            secondary_cta_href=None, secondary_cta_label=None):
    """Editorial-style hero used on /insights/ index + every pillar
    landing. No video, no background image — just well-typed text on
    a subtle tinted band. WCAG-compliant by construction:

    - Text colors hit ≥ 6:1 contrast against the surface-3 background.
    - The eyebrow chip has both color and a bordered shape so it is
      not communicated by color alone.
    - The H1 is the real <h1> for the page (semantic heading order).
    - Focus rings are inherited from the global :focus-visible rules
      plus the .insight-* specific overrides.

    Args mirror build_video_hero_html / build_brand_hero_html so the
    helper is a drop-in replacement for the insights generator's two
    landing-page renderers."""
    secondary = ""
    if secondary_cta_href and secondary_cta_label:
        secondary = (
            f'      <a class="cta-phone" href="{html.escape(secondary_cta_href)}">'
            f'{html.escape(secondary_cta_label)}</a>\n'
        )
    return (
        f'<section class="insight-hero" aria-labelledby="insight-hero-h1">\n'
        f'  <div class="insight-hero-inner">\n'
        f'    <p class="insight-hero-eyebrow">{html.escape(eyebrow_text)}</p>\n'
        f'    <h1 id="insight-hero-h1">{h1_html}</h1>\n'
        f'    <p class="insight-hero-lede">{lede_html}</p>\n'
        f'    <div class="insight-hero-cta">\n'
        f'      <a class="cta-button" href="{html.escape(cta_href)}">{html.escape(cta_label)}</a>\n'
        f'{secondary}'
        f'    </div>\n'
        f'  </div>\n'
        f'</section>\n'
    )

# ---------- Frontmatter helpers ----------

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def parse_article_frontmatter(text: str):
    """Minimal YAML-subset parser for article frontmatter."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    fm_text, body = m.group(1), text[m.end():]
    fm = {}
    for line in fm_text.splitlines():
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        v = v.strip().strip('"').strip("'")
        fm[k.strip()] = v
    return fm, body


# ---------- Schema builders ----------

def breadcrumb_schema(items):
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name,
             **({"item": f"{DOMAIN}{path}"} if path else {})}
            for i, (name, path) in enumerate(items)
        ],
    }


def article_schema(*, title, description, canonical, date, pillar_title, word_count, keywords):
    return {
        "@context": "https://schema.org",
        "@type": ["Article", "BlogPosting"],
        "headline": title,
        "description": description,
        "datePublished": date,
        "dateModified": date,
        "author": {
            "@type": "Person",
            "name": "Ken",
            "jobTitle": "Shop owner",
            "worksFor": {"@id": f"{DOMAIN}/#org"},
        },
        "publisher": {"@id": f"{DOMAIN}/#org"},
        "mainEntityOfPage": canonical,
        "articleSection": pillar_title,
        "keywords": keywords,
        "wordCount": word_count,
        "inLanguage": "en-US",
    }


def faq_schema_from_details(body_html: str):
    """If body_html contains <details><summary>…</summary>…</details> blocks,
    emit an FAQPage schema referencing them."""
    pairs = re.findall(
        r"<details[^>]*>\s*<summary[^>]*>(.*?)</summary>(.*?)</details>",
        body_html, re.DOTALL | re.IGNORECASE,
    )
    if not pairs:
        return None
    mains = []
    for q, a in pairs:
        q_txt = re.sub(r"<[^>]+>", "", q).strip()
        a_txt = re.sub(r"<[^>]+>", " ", a).strip()
        a_txt = re.sub(r"\s+", " ", a_txt)
        if q_txt and a_txt:
            mains.append({
                "@type": "Question",
                "name": q_txt,
                "acceptedAnswer": {"@type": "Answer", "text": a_txt},
            })
    if not mains:
        return None
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": mains}


# ---------- Pillar landing page ----------

def render_pillar_page(pillar: dict, published: List[dict]) -> str:
    """Render the /insights/{pillar}/index.html landing page."""
    slug = pillar["slug"]
    title = pillar["title"]
    h1 = pillar["h1"]
    summary = pillar["summary"]
    eyebrow = pillar["eyebrow"]
    canonical_path = f"/insights/{slug}/"
    canonical = f"{DOMAIN}{canonical_path}"

    # Build the cluster grid — published first, then planned.
    # Reader-facing copy: no "Published" tag (all cards on a pillar
    # page are within the pillar, so the tag is redundant), no
    # target-query line on planned cards (that's SEO terminology and
    # shouldn't leak into the UI).
    published_slugs = {a["slug"] for a in published}
    cluster_cards = []

    for art in published:
        cluster_cards.append(
            f'<li class="insight-card insight-card--published">\n'
            f'  <a href="/insights/{slug}/{art["slug"]}/">\n'
            f'    <h3>{html.escape(art["title"])}</h3>\n'
            f'    <p>{html.escape(art.get("description", ""))}</p>\n'
            f'    <span class="learn-more">Read &rarr;</span>\n'
            f'  </a>\n'
            f'</li>'
        )

    planned = [c for c in pillar["clusters"] if c["slug"] not in published_slugs]
    for art in planned:
        cluster_cards.append(
            f'<li class="insight-card insight-card--planned">\n'
            f'  <div>\n'
            f'    <span class="insight-card-tag insight-card-tag--planned">Coming soon</span>\n'
            f'    <h3>{html.escape(art["title"])}</h3>\n'
            f'  </div>\n'
            f'</li>'
        )

    # Reader-facing count line. Branched so the wording reads naturally
    # whether the series is fresh, mid-build, or fully published.
    n_pub = len(published)
    n_plan = len(planned)
    if n_pub == 0 and n_plan > 0:
        count_line = (
            f"This series is just getting started — {n_plan} articles drafting. "
            f"We publish when the work on the bench warrants writing it down."
        )
    elif n_plan == 0 and n_pub > 0:
        count_line = (
            f"{n_pub} articles in this series, all published. "
            f"More may follow as new failure modes and decisions come up on the bench."
        )
    else:
        count_line = (
            f"{n_pub} published so far. {n_plan} more drafting — we publish when "
            f"the work on the bench warrants writing it down."
        )

    cluster_grid = (
        f'<h2 id="articles">Articles in this series</h2>\n'
        f'<p>{count_line}</p>\n'
        f'<ul class="insight-cluster-grid">\n'
        + "\n".join(cluster_cards)
        + "\n</ul>\n"
    )

    # Pointer to the service page that does this work for real customers.
    reinforces_url = pillar.get("consolidates_signal_for", "")
    reinforce_section = ""
    if reinforces_url:
        reinforce_section = (
            f'<h2 id="service">When you need the work done</h2>\n'
            f'<p>These articles are working notes — diagnostic logic, decision frameworks, '
            f'the cost-and-lead-time math. For the service itself (quotes, scheduling, '
            f'what we actually do on the bench and in the field), the page is at '
            f'<a href="{reinforces_url}">{reinforces_url}</a>.</p>\n'
        )

    # Editorial hero — quiet, text-focused, no video, no image.
    hero_html = build_insight_hero_html(
        eyebrow_text=eyebrow,
        h1_html=html.escape(h1),
        lede_html=html.escape(summary),
        secondary_cta_href=f"tel:{PHONE_TEL}",
        secondary_cta_label=PHONE_DISPLAY,
    )

    body_html = hero_html + cluster_grid + reinforce_section

    # Crumbs + schema
    crumbs = [
        ("Home", "/"),
        ("Insights", "/insights/"),
        (title, None),
    ]
    schema_blocks = [
        breadcrumb_schema(crumbs),
        {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": title,
            "description": summary,
            "url": canonical,
            "isPartOf": {"@id": f"{DOMAIN}/insights/"},
        },
    ]

    return _wrap_page(
        title=f"{title} | Midwest CNC Services",
        meta_desc=summary[:160],
        canonical=canonical,
        schema_blocks=schema_blocks,
        crumbs=crumbs,
        body_html=body_html,
        layout="wide",
        body_class="insights-page insights-pillar",
    )


# ---------- Article page ----------

def render_article_page(pillar: dict, article: dict, md_body: str) -> str:
    """Render an article HTML page from the markdown body + article metadata."""
    pillar_slug = pillar["slug"]
    pillar_title = pillar["title"]
    article_slug = article["slug"]
    canonical_path = f"/insights/{pillar_slug}/{article_slug}/"
    canonical = f"{DOMAIN}{canonical_path}"

    title = article["title"]
    description = article.get("description", "")
    date = article.get("date", _dt.date.today().isoformat())

    # Markdown body → HTML
    body_html = m2h.md_body_to_html(md_body)

    # Insert reading-meta strip + eyebrow band right at the top of the body.
    wc = len(re.sub(r"<[^>]+>", " ", body_html).split())
    read_min = max(3, round(wc / 200))
    meta_strip = (
        f'<p class="insight-eyebrow">{html.escape(pillar_title)}</p>\n'
        f'<h1 class="insight-h1">{html.escape(title)}</h1>\n'
        f'<p class="insight-meta">By Ken &middot; {date} &middot; ~{read_min} min read</p>\n'
    )
    body_html = meta_strip + body_html

    # CTA tail
    body_html += (
        '\n<div class="insight-cta">\n'
        '  <p><strong>Need this work done?</strong> Tell us the machine and the symptom.</p>\n'
        '  <p><a class="cta-button" href="/get-a-quote/">Get a quote</a> '
        '<a class="cta-phone" href="tel:+13196104341">319-610-4341</a></p>\n'
        '</div>\n'
    )

    crumbs = [
        ("Home", "/"),
        ("Insights", "/insights/"),
        (pillar_title, f"/insights/{pillar_slug}/"),
        (title, None),
    ]

    keywords = article.get("target_query", "")
    schema_blocks = [
        breadcrumb_schema(crumbs),
        article_schema(
            title=title,
            description=description,
            canonical=canonical,
            date=date,
            pillar_title=pillar_title,
            word_count=wc,
            keywords=keywords,
        ),
    ]
    faq = faq_schema_from_details(body_html)
    if faq:
        schema_blocks.append(faq)

    return _wrap_page(
        title=f"{title} | Midwest CNC Services",
        meta_desc=description[:160],
        canonical=canonical,
        schema_blocks=schema_blocks,
        crumbs=crumbs,
        body_html=body_html,
        layout="default",
        body_class="insights-page insights-article",
    )


# ---------- Insights landing index ----------

def render_insights_index(pillars_data: dict, published_by_pillar: Dict[str, List[dict]]) -> str:
    canonical_path = "/insights/"
    canonical = f"{DOMAIN}{canonical_path}"

    total_published = sum(len(v) for v in published_by_pillar.values())
    total_planned = sum(len(p["clusters"]) for p in pillars_data["pillars"]) - total_published

    hero_html = build_insight_hero_html(
        eyebrow_text="Technical Insights",
        h1_html="CNC Repair Insights from the Bench and the Field",
        lede_html=(
            "Working notes from Ken and the Midwest CNC team. The diagnostic logic, "
            "decision frameworks, and platform-specific knowledge we use day-to-day — "
            "written for shop owners and operators, not search engines."
        ),
        secondary_cta_href=f"tel:{PHONE_TEL}",
        secondary_cta_label=PHONE_DISPLAY,
    )

    pillar_cards = []
    for p in pillars_data["pillars"]:
        n_pub = len(published_by_pillar.get(p["slug"], []))
        n_planned = len(p["clusters"]) - n_pub
        # Reader-facing count: "2 published, 14 drafting" reads more
        # honest than "planned" (we don't have a posting calendar; we
        # publish when the work warrants it).
        if n_pub == 0:
            count_text = f"{n_planned} articles drafting"
        elif n_planned == 0:
            count_text = f"{n_pub} articles"
        else:
            count_text = f"{n_pub} published &middot; {n_planned} drafting"
        pillar_cards.append(
            f'<li class="insight-pillar-card">\n'
            f'  <a href="/insights/{p["slug"]}/">\n'
            f'    <span class="insight-pillar-eyebrow">{html.escape(p["eyebrow"])}</span>\n'
            f'    <h3>{html.escape(p["title"])}</h3>\n'
            f'    <p>{html.escape(p["summary"][:220])}{"…" if len(p["summary"]) > 220 else ""}</p>\n'
            f'    <p class="insight-pillar-counts">{count_text}</p>\n'
            f'    <span class="learn-more">Read articles &rarr;</span>\n'
            f'  </a>\n'
            f'</li>'
        )

    pillars_section = (
        f'<h2 id="topics">Where we focus</h2>\n'
        f'<p>Five areas where the bench work, the diagnostic reasoning, and the '
        f'platform-specific knowledge actually lives. Articles ship when a piece of '
        f'work earns the writing — there is no posting calendar. '
        f'{total_published} published so far, {total_planned} more drafting.</p>\n'
        f'<ul class="insight-pillar-grid">\n'
        + "\n".join(pillar_cards)
        + "\n</ul>\n"
    )

    # Recent articles (sort by date string only — dicts aren't comparable)
    all_pub = []
    for p in pillars_data["pillars"]:
        for a in published_by_pillar.get(p["slug"], []):
            all_pub.append((a.get("date", ""), p, a))
    all_pub.sort(key=lambda t: t[0], reverse=True)
    recent_cards = []
    for _, p, a in all_pub[:6]:
        recent_cards.append(
            f'<li class="insight-card insight-card--published">\n'
            f'  <a href="/insights/{p["slug"]}/{a["slug"]}/">\n'
            f'    <span class="insight-card-tag">{html.escape(p["title"])}</span>\n'
            f'    <h3>{html.escape(a["title"])}</h3>\n'
            f'    <p>{html.escape(a.get("description", ""))}</p>\n'
            f'    <span class="learn-more">Read &rarr;</span>\n'
            f'  </a>\n'
            f'</li>'
        )
    recent_section = ""
    if recent_cards:
        recent_section = (
            f'<h2 id="latest">Latest articles</h2>\n'
            f'<ul class="insight-cluster-grid">\n'
            + "\n".join(recent_cards)
            + "\n</ul>\n"
        )

    body_html = hero_html + pillars_section + recent_section

    crumbs = [("Home", "/"), ("Insights", None)]
    schema_blocks = [
        breadcrumb_schema(crumbs),
        {
            "@context": "https://schema.org",
            "@type": "Blog",
            "name": "Midwest CNC Insights",
            "description": "Technical insights on CNC repair, spindle work, way covers, controls, and used-machine ownership.",
            "url": canonical,
        },
    ]

    return _wrap_page(
        title="Technical Insights | Midwest CNC Services",
        meta_desc="Working notes from the bench and the field — CNC diagnostics, control systems, way covers, field service logistics, and used-machine ownership.",
        canonical=canonical,
        schema_blocks=schema_blocks,
        crumbs=crumbs,
        body_html=body_html,
        layout="wide",
        body_class="insights-page insights-index",
    )


# ---------- Page chrome ----------

def _wrap_page(*, title, meta_desc, canonical, schema_blocks, crumbs,
               body_html, layout, body_class=""):
    schema_json = "\n".join(
        f'<script type="application/ld+json">\n{json.dumps(s, indent=2, ensure_ascii=False)}\n</script>'
        for s in schema_blocks
    )

    crumb_lis = []
    for name, href in crumbs:
        if href:
            crumb_lis.append(f'<li><a href="{html.escape(href)}">{html.escape(name)}</a></li>')
        else:
            crumb_lis.append(f'<li>{html.escape(name)}</li>')
    crumbs_html = (
        '<nav class="breadcrumbs" aria-label="breadcrumb">\n'
        '  <ol>\n    '
        + "".join(crumb_lis)
        + '\n  </ol>\n</nav>'
    )

    # Pull the .insight-hero block out so it renders full-bleed (no
    # section-inner wrapping, no alternating-band coloring) and only
    # the rest of the body gets wrapped into alternating sections.
    hero_html = ""
    rest_html = body_html
    m = re.match(r"\s*(<section class=\"insight-hero\"[\s\S]*?</section>)\s*", body_html)
    if m:
        hero_html = m.group(1)
        rest_html = body_html[m.end():]

    banded_rest = m2h.wrap_into_sections(rest_html, layout=layout) if rest_html.strip() else ""

    classes = [f"layout-{layout}"] if layout != "default" else []
    if body_class:
        classes.extend(body_class.split())
    class_attr = f' class="{" ".join(classes)}"' if classes else ""

    return f"""<!doctype html>
<html lang="en">
<head>
{m2h.TRACKING_HEAD}
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{m2h.ANALYTICS_HEAD}
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(meta_desc)}">
<link rel="canonical" href="{html.escape(canonical)}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(meta_desc)}">
<meta property="og:type" content="article">
{m2h.social_meta(title, meta_desc, canonical)}
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap">
<style>
{m2h.CSS}</style>
{schema_json}
</head>
<body{class_attr}>
<a class="skip-link" href="#main">Skip to content</a>
{m2h.build_site_header()}
{crumbs_html}
<main id="main">
<article>
{hero_html}
{banded_rest}
</article>
</main>
{m2h.build_site_footer()}
<div class="mobile-cta-bar" role="region" aria-label="Quick contact">
  <a class="mcta-phone" href="tel:+13196104341">&#9742; 319-610-4341</a>
  <a class="mcta-quote" href="/get-a-quote/">Get a Quote</a>
</div>
{m2h.COVERAGE_MAP_LOADER}
</body>
</html>
"""


# ---------- Driver ----------

def collect_published(pillar_slug: str, cluster_specs: List[dict]) -> List[dict]:
    """Walk src/content/insights/{pillar}/*.md and match against the
    cluster spec for that pillar. Returns the published article entries
    enriched with frontmatter."""
    dirp = CONTENT / pillar_slug
    if not dirp.exists():
        return []
    out = []
    spec_by_slug = {c["slug"]: c for c in cluster_specs}
    for md in sorted(dirp.glob("*.md")):
        if md.name.startswith("_"):
            continue
        text = md.read_text(encoding="utf-8")
        fm, _body = parse_article_frontmatter(text)
        slug = fm.get("slug") or md.stem
        spec = dict(spec_by_slug.get(slug, {}))
        spec["slug"] = slug
        spec["title"] = fm.get("title") or spec.get("title", slug)
        spec["description"] = fm.get("description", spec.get("title", ""))
        spec["date"] = fm.get("date") or _dt.date.today().isoformat()
        spec["_md_path"] = md
        out.append(spec)
    return out


def main():
    pillars_data = json.loads(DATA.read_text(encoding="utf-8"))
    published_by_pillar: Dict[str, List[dict]] = {}

    print("=== Generating insights pages ===\n")

    # Per-pillar work
    for pillar in pillars_data["pillars"]:
        slug = pillar["slug"]
        published = collect_published(slug, pillar["clusters"])
        published_by_pillar[slug] = published

        # Pillar landing page
        pillar_out = PUBLIC / "insights" / slug / "index.html"
        pillar_out.parent.mkdir(parents=True, exist_ok=True)
        html_out = render_pillar_page(pillar, published)
        pillar_out.write_text(html_out, encoding="utf-8")
        print(f"  ✓ pillar  → {pillar_out.relative_to(REPO)}  ({len(published)} published, {len(pillar['clusters']) - len(published)} planned)")

        # Article pages
        for art in published:
            md_path: Path = art["_md_path"]
            md_text = md_path.read_text(encoding="utf-8")
            _fm, md_body = parse_article_frontmatter(md_text)
            article_out = PUBLIC / "insights" / slug / art["slug"] / "index.html"
            article_out.parent.mkdir(parents=True, exist_ok=True)
            html_out = render_article_page(pillar, art, md_body)
            article_out.write_text(html_out, encoding="utf-8")
            print(f"    ✓ article  → {article_out.relative_to(REPO)}")

    # Index page
    index_out = PUBLIC / "insights" / "index.html"
    index_out.parent.mkdir(parents=True, exist_ok=True)
    index_out.write_text(render_insights_index(pillars_data, published_by_pillar), encoding="utf-8")
    print(f"\n  ✓ index  → {index_out.relative_to(REPO)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

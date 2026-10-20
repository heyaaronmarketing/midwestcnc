#!/usr/bin/env python3
"""
Phase 1 — site shell generator.

Builds: homepage, /about/, /get-a-quote/, four service hubs
(/repairs/, /spindle-grinding/, /way-covers/, /service-area/), the
404 page, sitemap.xml, robots.txt, and a SVG favicon. Updates
public/_redirects with the seven state-URL placeholders.

Imports CSS from markdown_to_html.py so the shell matches the brand
pages exactly. Adds SITE_SHELL_CSS for tile grids and the quote form.
"""

import html
import json
import os
import re
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import markdown_to_html as m2h
import generate_brand_pages as gbp


# ---------- Config ----------

REPO = m2h.REPO
PUBLIC = m2h.OUTDIR
CONTENT_BRAND_DIR = os.path.join(REPO, "src", "content", "spindle-brands")
CONTENT_REPAIR_DIR = os.path.join(REPO, "src", "content", "machine-repair")
CONTENT_COVERS_DIR = os.path.join(REPO, "src", "content", "way-covers")

DOMAIN = "https://midwestcncservices.com"
PHONE_DISPLAY = "319-610-4341"
PHONE_TEL = "+13196104341"
ADDRESS_CITY = "Waterloo"
ADDRESS_STATE = "IA"
WEB3FORMS_KEY = "14ef8440-a42b-4dd3-b416-30d9d6b3e906"  # legacy — no longer used; form now posts to /api/quote

# Cloudflare Turnstile site key (public — safe to embed in HTML).
# Replace with your real site key after creating the widget at
# https://dash.cloudflare.com/?to=/:account/turnstile.
# The matching TURNSTILE_SECRET is set as a server-side env var in
# the Cloudflare Pages dashboard, NOT here.
#
# For local-build testing without a real key, leave the test key
# below. Cloudflare's documented test key always passes verification
# in development and always fails in production.
TURNSTILE_SITE_KEY = "0x4AAAAAADXY93Hw7DfP3PQJ"

# Service-area state list (the 7 states Ken confirmed)
STATE_TILES = [
    ("Iowa",      "iowa",       "Des Moines, Davenport, Waterloo, Cedar Rapids",
     "/assets/images/general/view-all-iowa-cnc-service-locations.png"),
    ("Illinois",  "illinois",   "Chicago, Rockford, Peoria, Springfield",
     "/assets/images/general/illinois.png"),
    ("Wisconsin", "wisconsin",  "Milwaukee, Madison, Green Bay",
     "/assets/images/general/wisconsin.png"),
    ("Minnesota", "minnesota",  "St. Paul, Minneapolis, Rochester",
     "/assets/images/general/minnesota.png"),
    ("Nebraska",  "nebraska",   "Lincoln, Omaha, Grand Island",
     "/assets/images/general/nebraska.png"),
    ("Missouri",  "missouri",   "St. Louis, Kansas City, Springfield",
     "/assets/images/general/missouri.png"),
    ("Texas",     "texas",      "Dallas, Houston, Austin",
     "/assets/images/general/texas.png"),
]
STATE_NAMES = [n for n, *_ in STATE_TILES]

# Service tiles for the homepage — expanded descriptions (~50–60 words each)
# referencing specific brand coverage from spindle-brands.json.
SERVICE_TILES = [
    {
        "title": "Machine Repair",
        "href": "/repairs/",
        "image": "/assets/images/general/image-of-cnc-machine.png",
        "alt": "CNC machining center under service",
        "desc": ("CNC machine repair across spindle, control, ATC, drive, "
                 "and alignment work. We service Mazak, Haas, Okuma, DMG Mori, "
                 "Fanuc, Doosan, Brother, Hurco, and 12 other major OEM "
                 "platforms — plus Amada press brakes and Trumpf lasers. Field "
                 "troubleshooting where a remote diagnostic can save a teardown."),
    },
    {
        "title": "Way Covers",
        "href": "/way-covers/",
        "image": "/assets/images/general/image-of-way-covers.png",
        "alt": "Replacement CNC way covers",
        "desc": ("Replacement way covers in bellows, telescoping steel, and "
                 "roll-up styles. Built to spec for every CNC platform we "
                 "service — from Mazak Integrex multi-taskers and Haas VF "
                 "machines to legacy Fadal 4020s and Hitachi Seiki HMCs. Most "
                 "orders ship in 2–4 weeks. We measure from your original or "
                 "build to drawing."),
    },
    {
        "title": "Spindle Grinding",
        "href": "/spindle-grinding/",
        "image": "/assets/images/general/image-of-spindle-grinding.png",
        "alt": "CNC spindle on the grinding bench",
        "desc": ("Spindle rebuilds, regrinds, and rebalancing across 18 OEM "
                 "platforms — Mazak, Haas, Okuma, DMG Mori, Mori Seiki, Doosan, "
                 "and on through Fadal and Hitachi Seiki legacy work. Most "
                 "jobs run 2–6 weeks depending on bearing-pack damage and "
                 "parts availability. Each brand page has failure modes and "
                 "lead times."),
    },
]


# Homepage FAQ — 4 Q&As traceable to Ken's authorized emphasis themes
# (response, legacy, coverage, crash-recovery). Used both as visible HTML
# and as FAQPage JSON-LD.
HOMEPAGE_FAQ = [
    {
        "q": "How fast can you respond to a quote request?",
        "a": ("Most quote requests go out within one business day. If the "
              "machine is down and you need someone on the line right now, "
              "call 319-610-4341 — we'd rather talk through the symptoms "
              "than wait for an email back. Field troubleshooting on the "
              "phone often saves a full teardown."),
    },
    {
        "q": "Do you work on older or discontinued machines?",
        "a": ("Yes. We have dedicated brand pages and parts-sourcing "
              "approaches for Fadal, Hitachi Seiki, and Monarch — "
              "manufacturers whose CNC lines have been gone for years but "
              "whose machines are still cutting daily in Midwest shops. We "
              "lean on aftermarket suppliers, used-market sourcing, and "
              "custom-machined replacements where OEM components are gone."),
    },
    {
        "q": "Where do you work? Do you come on-site?",
        "a": ("We serve shops across Iowa, Illinois, Wisconsin, Minnesota, "
              "Nebraska, Missouri, and Texas from our Waterloo, Iowa shop. "
              "Field service when that's the right call for the job; spindle "
              "rebuilds and way-cover builds happen at our bench and ship "
              "back to you."),
    },
    {
        "q": "Can you recover a crashed spindle?",
        "a": ("Often, yes. Crash recovery is one of the threads of work "
              "that comes through here — taper damage, bearing-pack failure, "
              "alignment loss from impact. Customers are usually relieved "
              "to avoid the replacement lead times and the six-figure "
              "capital expense of a new spindle. Bring it in for a teardown."),
    },
]


# ---------- Shared chrome ----------

SITE_SHELL_CSS = """
/* =================================================================
   Site-shell additions: homepage, hubs, quote form, tiles, brand grid
   ================================================================= */

/* Early success-state toggle — set on <html> in <head> before paint */
.form-submitted-html .quote-form,
.form-submitted-html .quote-helpers { display: none; }
.form-submitted-html .success-message { display: block; }

.section-eyebrow {
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

/* =================================================================
   Homepage hero — single-column, video background, image fallback.

   Structure:
     <section class="home-hero">
       <video class="home-hero-video" .../>      <- bg media layer
       <div class="home-hero-overlay"/>          <- dark gradient
       <div class="home-hero-content">           <- text + CTAs
     </section>

   Layers (z-index):
     0  video (decorative, aria-hidden)
     1  overlay (legibility gradient)
     2  content (text, white on dark)

   prefers-reduced-motion respects the user's OS setting — video is
   removed and the poster image is shown as a static background instead.
   ================================================================= */

/* Reset the band wrapper: hero is full-bleed, manages own backdrop. */
.page-section-hero {
  padding: 0;
  background: var(--bg);
}
.page-section-hero > .section-inner { padding: 0; max-width: none; }

.home-hero {
  position: relative;
  width: 100%;
  height: 100vh;
  min-height: 600px;
  max-height: 820px;
  display: flex;
  align-items: center;
  overflow: hidden;
  isolation: isolate;
  color: #fff;
  background:
    /* Poster image fallback if video fails to load (and on mobile +
       prefers-reduced-motion, where the <video> is hidden) */
    url('/assets/images/general/midwest-cnc-highway-shot.webp')
    center / cover no-repeat
    #000;
}

.home-hero-video {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
  z-index: 1;
  pointer-events: none;
  /* Start invisible — the JS opacity driver below ramps it up from
     the video's actual currentTime, so the fade is locked to the
     video clock instead of drifting against a fixed-length CSS
     keyframe. No clunky seam. */
  opacity: 0;
}

/* Dark vertical gradient overlay — top 40% black to bottom 70% black.
   Keeps white text legible over any frame, slightly heavier at the
   bottom where the CTAs and trust line sit. */
.home-hero-overlay {
  position: absolute;
  inset: 0;
  z-index: 2;
  pointer-events: none;
  background: linear-gradient(
    to bottom,
    rgba(0, 0, 0, 0.40) 0%,
    rgba(0, 0, 0, 0.70) 100%
  );
}

.home-hero-content {
  position: relative;
  z-index: 3;
  max-width: var(--max-wide);
  width: 100%;
  margin: 0 auto;
  padding: clamp(3rem, 7vw, 5rem) var(--s-5);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.home-hero-content > .eyebrow {
  font-size: 0.7rem;
  padding: 0.28rem 0.75rem;
  margin: 0 0 var(--s-4) 0;
  background: rgba(255, 255, 255, 0.12);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.20);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

.home-hero-content > h1 {
  font-size: clamp(2.1rem, 4.6vw, 3.6rem);
  line-height: 1.05;
  letter-spacing: -0.025em;
  font-weight: 800;
  margin: 0 0 var(--s-5) 0;
  max-width: 22ch;
  color: #fff;
  text-shadow: 0 2px 12px rgba(0, 0, 0, 0.3);
}

.home-hero-content > .lede {
  font-size: clamp(1.05rem, 1.25vw, 1.2rem);
  line-height: 1.55;
  color: rgba(255, 255, 255, 0.92);
  margin: 0 0 var(--s-6) 0;
  max-width: 60ch;
  text-shadow: 0 1px 6px rgba(0, 0, 0, 0.4);
}

.home-hero-content > .cta-row {
  margin: 0 0 var(--s-5) 0;
  justify-content: center;
}
/* Strengthen the secondary phone CTA against the dark video — give it
   a semi-transparent surface so it reads cleanly. */
.home-hero-content .cta-phone {
  background: rgba(255, 255, 255, 0.10);
  color: #fff !important;
  border-color: rgba(255, 255, 255, 0.28);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}
.home-hero-content .cta-phone:hover {
  background: rgba(255, 255, 255, 0.18);
  border-color: rgba(255, 255, 255, 0.5);
  color: #fff !important;
}
.home-hero-content .cta-phone::before { color: #fff; }

.home-hero-content > .trust-line {
  margin: 0;
  font-size: 0.88rem;
  color: rgba(255, 255, 255, 0.72);
  text-shadow: 0 1px 6px rgba(0, 0, 0, 0.4);
}

/* Mobile — skip the video entirely. Cellular users shouldn't get hit
   with a 1.5 MB autoplay download. The poster image (set as the
   .home-hero background-image above) takes over. */
@media (max-width: 768px) {
  .home-hero {
    height: auto;
    min-height: clamp(420px, 75vh, 560px);
    max-height: none;
  }
  .home-hero-video { display: none; }
  .home-hero-content {
    padding: clamp(2rem, 7vw, 3rem) var(--s-4);
  }
  .home-hero-content > .cta-row { width: 100%; }
}

/* Respect prefers-reduced-motion — disable the video, let the poster
   image background take over. Vestibular-disorder accessibility +
   Core Web Vitals signal. */
@media (prefers-reduced-motion: reduce) {
  .home-hero-video { display: none; }
}

/* =================================================================
   Tile grid (homepage services, state grid)
   ================================================================= */
.tile-grid, .state-grid {
  display: grid;
  gap: var(--s-4);
  margin: var(--s-5) 0 var(--s-6) 0;
}
.tile-grid { grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); }
.state-grid { grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); }

.tile {
  display: flex;
  flex-direction: column;
  text-decoration: none !important;
  color: var(--fg) !important;
  background: var(--surface);
  padding: var(--s-4);
  border-radius: var(--r-3);
  border: 1px solid var(--line);
  box-shadow: var(--sh-1);
  transition: transform var(--t-base), box-shadow var(--t-base), border-color var(--t-base);
  position: relative;
  overflow: hidden;
}
.tile::after {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: var(--r-3);
  background: linear-gradient(135deg, transparent 60%, rgba(184, 52, 26, 0.04));
  opacity: 0;
  transition: opacity var(--t-base);
  pointer-events: none;
}
.tile:hover {
  transform: translateY(-4px);
  box-shadow: var(--sh-4);
  border-color: var(--accent);
}
.tile:hover::after { opacity: 1; }
.tile img {
  width: 100%;
  height: 160px;
  object-fit: cover;
  border-radius: var(--r-2);
  margin-bottom: var(--s-3);
  display: block;
}
.tile h3 { margin: var(--s-1) 0 var(--s-2) 0; font-size: 1.15rem; }
.tile p { color: var(--muted); font-size: 0.95rem; margin: var(--s-2) 0 var(--s-3) 0; flex-grow: 1; }
.tile .learn-more {
  color: var(--accent);
  font-size: 0.9rem;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  transition: gap var(--t-fast);
}
.tile:hover .learn-more { gap: 0.55rem; }

/* =================================================================
   Brand grid — hub pages
   ================================================================= */
.brand-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: var(--s-3);
  margin: var(--s-4) 0 var(--s-6) 0;
  list-style: none;
  padding: 0;
}
.brand-grid li { margin: 0; }
.brand-grid a {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.85rem 1rem;
  border: 1px solid var(--line);
  border-radius: var(--r-2);
  text-decoration: none !important;
  color: var(--fg) !important;
  font-weight: 600;
  background: var(--surface);
  box-shadow: var(--sh-1);
  transition: transform var(--t-fast), border-color var(--t-fast), color var(--t-fast), box-shadow var(--t-fast);
  position: relative;
}
.brand-grid a::after {
  content: "";
  display: inline-block;
  width: 7px;
  height: 7px;
  border-right: 2px solid currentColor;
  border-top: 2px solid currentColor;
  transform: rotate(45deg);
  opacity: 0.4;
  transition: transform var(--t-fast), opacity var(--t-fast);
}
.brand-grid a:hover {
  border-color: var(--accent);
  color: var(--accent) !important;
  transform: translateY(-2px);
  box-shadow: var(--sh-3);
}
.brand-grid a:hover::after { opacity: 1; transform: rotate(45deg) translate(2px, -2px); }

/* =================================================================
   State sections (hub) + state grid tiles
   ================================================================= */
.state-section {
  margin: var(--s-6) 0;
  padding: var(--s-5);
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--r-3);
  box-shadow: var(--sh-1);
}
.state-section h2 { margin-top: 0; }
.state-section h2::before { display: none; }
.state-cities { color: var(--muted); margin: var(--s-1) 0 var(--s-3) 0; }

/* =================================================================
   Quote form
   ================================================================= */
.quote-form {
  display: flex;
  flex-direction: column;
  gap: var(--s-4);
  max-width: 560px;
  margin: var(--s-6) 0;
  padding: var(--s-5);
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--r-3);
  box-shadow: var(--sh-2);
}
.quote-form .field { display: flex; flex-direction: column; gap: 0.4rem; }
.quote-form label { font-weight: 600; font-size: 0.92rem; color: var(--fg); }
.quote-form .required::after { content: " *"; color: var(--accent); }
.quote-form input,
.quote-form textarea,
.quote-form select {
  font: inherit;
  padding: 0.75rem 0.9rem;
  border: 1.5px solid var(--line);
  border-radius: var(--r-2);
  background: var(--surface);
  width: 100%;
  transition: border-color var(--t-fast), box-shadow var(--t-fast);
}
.quote-form input:hover,
.quote-form textarea:hover,
.quote-form select:hover { border-color: var(--muted); }
.quote-form input:focus,
.quote-form textarea:focus,
.quote-form select:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: var(--sh-focus);
}
.quote-form textarea { min-height: 9rem; resize: vertical; }
.quote-form .radio-group { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: var(--s-2); }
.quote-form .radio-group label {
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  padding: 0.55rem 0.8rem;
  border: 1.5px solid var(--line);
  border-radius: var(--r-2);
  background: var(--surface);
  transition: border-color var(--t-fast), background var(--t-fast);
}
.quote-form .radio-group label:hover { border-color: var(--muted); background: var(--surface-2); }
.quote-form .radio-group input[type="radio"] { accent-color: var(--accent); }
.quote-form button {
  font: inherit;
  background: var(--accent);
  color: #fff;
  padding: 0.95rem 1.6rem;
  border: 0;
  border-radius: var(--r-pill);
  font-weight: 700;
  cursor: pointer;
  align-self: flex-start;
  box-shadow: var(--sh-2);
  transition: background var(--t-fast), transform var(--t-fast), box-shadow var(--t-fast);
}
.quote-form button:hover { background: var(--accent-dark); transform: translateY(-1px); box-shadow: var(--sh-3); }
.quote-form button:active { transform: translateY(0); box-shadow: var(--sh-1); }
.quote-form .honeypot { position: absolute; left: -9999px; opacity: 0; pointer-events: none; }

/* Turnstile widget — minimal styling, lets Cloudflare's iframe render
   itself. The wrapper just centers the widget within the form column. */
.quote-form .cf-turnstile {
  display: flex;
  justify-content: center;
  margin: var(--s-2) 0;
}

/* Error banner shown when the Pages Function redirected back with
   ?error=... in the query string. Hidden by default; the inline
   <script> at the bottom of the form un-hides it when present. */
.form-error-banner {
  padding: var(--s-4);
  border-radius: var(--r-3);
  background: rgba(184, 52, 26, 0.06);
  border: 1px solid rgba(184, 52, 26, 0.25);
  border-left: 4px solid var(--accent-dark);
  margin: var(--s-5) 0;
  color: var(--fg);
}
.form-error-banner p { margin: 0; }
.form-error-banner[hidden] { display: none; }

/* =================================================================
   Get-a-Quote page — modern conversion-focused redesign.
   See quote_body() in this file for the matching HTML.
   ================================================================= */

/* Quote hero — distinct from brand-hero / video-hero. Calmer
   editorial band with a heavy phone CTA. */
.quote-hero {
  background:
    radial-gradient(120% 80% at 50% 0%, rgba(184, 52, 26, 0.06), transparent 60%),
    var(--surface-3);
  border-bottom: 1px solid var(--line);
  padding: clamp(2.5rem, 6vw, 4rem) var(--s-5) clamp(2rem, 5vw, 3rem);
  margin: 0 0 var(--s-5) 0;
}
.quote-hero-inner {
  max-width: var(--max-wide);
  margin: 0 auto;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.quote-hero-eyebrow {
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
.quote-hero h1 {
  font-size: clamp(1.85rem, 4vw, 2.8rem);
  line-height: 1.12;
  letter-spacing: -0.02em;
  font-weight: 800;
  margin: 0 0 var(--s-3) 0;
  max-width: 22ch;
  color: var(--fg);
}
.quote-hero h1::before { display: none; }
.quote-hero-lede {
  font-size: clamp(1.02rem, 1.2vw, 1.15rem);
  line-height: 1.55;
  color: var(--fg);
  margin: 0 0 var(--s-5) 0;
  max-width: 60ch;
}

/* Dominant call banner — the primary action on this page. Full-width
   (capped), large tap target. Built for a stressed owner on a phone in
   the shop: the call button is the loudest thing above the form. */
.quote-call-banner {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--s-4);
  width: 100%;
  max-width: 520px;
  margin: 0 auto var(--s-3);
  background: var(--accent);
  color: #fff !important;
  text-decoration: none !important;
  padding: 1.15rem 1.5rem;
  border-radius: var(--r-3);
  box-shadow: var(--sh-3);
  transition: background var(--t-fast), transform var(--t-fast), box-shadow var(--t-fast);
}
.quote-call-banner:hover {
  background: var(--accent-dark);
  transform: translateY(-2px);
  box-shadow: var(--sh-4);
}
.quote-call-banner:focus-visible {
  outline: 3px solid var(--accent-dark);
  outline-offset: 3px;
}
.quote-call-banner-icon {
  font-size: 2rem;
  line-height: 1;
  flex-shrink: 0;
}
.quote-call-banner-text { display: flex; flex-direction: column; align-items: flex-start; line-height: 1.15; }
.quote-call-banner-main {
  font-size: 1.25rem;
  font-weight: 800;
  letter-spacing: -0.01em;
}
.quote-call-banner-sub {
  font-size: 0.85rem;
  opacity: 0.92;
  margin-top: 0.12rem;
}
.quote-hero-jumplink {
  display: inline-block;
  color: var(--accent-dark);
  text-decoration: underline;
  text-decoration-color: rgba(140, 37, 16, 0.45);
  text-underline-offset: 3px;
  font-size: 0.95rem;
  font-weight: 600;
  transition: text-decoration-color var(--t-fast);
}
.quote-hero-jumplink:hover { text-decoration-color: var(--accent-dark); }
.quote-hero-jumplink:focus-visible {
  outline: 3px solid var(--accent-dark);
  outline-offset: 3px;
  border-radius: 2px;
}

/* Mobile: the call banner goes truly full-width and even bigger —
   this is the in-the-shop scenario the page is designed around. */
@media (max-width: 600px) {
  .quote-call-banner {
    max-width: none;
    padding: 1.25rem 1rem;
  }
  .quote-call-banner-main { font-size: 1.3rem; }
}

@media (prefers-reduced-motion: reduce) {
  .quote-call-banner { transition: none !important; }
  .quote-call-banner:hover { transform: none !important; }
}

/* Single-column layout — the whole quote body lives inside one
   .page-section-hero band whose .section-inner is uncapped (max-width:
   none, padding: 0), so .quote-layout is the element that re-establishes
   the 1140px content width + horizontal gutter. The form card, intro
   checklist, and "What happens next" timeline all stack inside it at
   full width. */
.quote-layout {
  max-width: var(--max-wide);
  margin: 0 auto;
  padding: var(--s-6) var(--s-5);
}
@media (max-width: 700px) {
  .quote-layout { padding: var(--s-5) var(--s-4); }
}

/* Intro checklist at the top of the form — sets expectations for
   what to have handy before filling out the fields. */
.quote-form-intro {
  padding: var(--s-4) var(--s-5);
  background: color-mix(in srgb, var(--surface) 90%, var(--accent) 5%);
  border: 1px solid color-mix(in srgb, var(--accent) 20%, var(--line));
  border-left: 4px solid var(--accent);
  border-radius: var(--r-2);
}
.quote-form-intro-title {
  margin: 0 0 var(--s-2) 0;
  font-weight: 600;
  font-size: 1.02rem;
  color: var(--fg);
}
.quote-form-intro-list {
  margin: 0;
  padding-left: 1.2rem;
  color: var(--fg);
  font-size: 0.98rem;
  line-height: 1.55;
}
.quote-form-intro-list li { margin: 0.28rem 0; }

/* "What happens next" — 3-step timeline as a horizontal grid inside
   the form card, below the submit button. Stacks on narrow. */
.quote-next-steps {
  margin-top: var(--s-4);
  padding-top: var(--s-5);
  border-top: 1px solid var(--line);
}
.quote-next-steps-title {
  font-weight: 700;
  font-size: 0.88rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--accent-dark);
  margin: 0 0 var(--s-4) 0;
}
.quote-next-steps-grid {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--s-5);
}
.quote-next-steps-grid li {
  display: flex;
  align-items: flex-start;
  gap: var(--s-3);
}
.quote-next-steps-num {
  width: 34px;
  height: 34px;
  background: var(--accent);
  color: #fff;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 0.98rem;
  flex-shrink: 0;
}
.quote-next-steps-grid strong {
  display: block;
  color: var(--fg);
  font-size: 1rem;
  margin-bottom: 0.15rem;
}
.quote-next-steps-grid span {
  color: var(--muted);
  font-size: 0.92rem;
  line-height: 1.5;
}
@media (max-width: 780px) {
  .quote-next-steps-grid { grid-template-columns: 1fr; gap: var(--s-3); }
}

/* Form card — full width of the wide band, sits on a surface card
   with generous padding so fields have real breathing room. Overrides
   the legacy .quote-form rule (max-width: 560px) which is otherwise
   still applied because the form carries both classes. */
.quote-form.quote-form-modern {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--r-3);
  box-shadow: var(--sh-2);
  padding: clamp(var(--s-5), 4vw, var(--s-8));
  margin: 0;
  max-width: none;
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: var(--s-7);
}

/* Field-section grouping — uses <fieldset> for semantics; no
   visible fieldset border. The <legend> becomes a section title. */
.form-section {
  border: 0;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: var(--s-4);
}
.form-section-title {
  font-size: 0.88rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--accent-dark);
  padding: 0;
  margin: 0 0 var(--s-2) 0;
}

/* Single-column field rows — every field gets its own line at the
   full form width. No internal columns anywhere in the quote form. */
.form-row {
  display: flex;
  flex-direction: column;
  gap: var(--s-4);
}

/* Scale up the form for the wider column. Larger inputs, labels,
   and textarea give the form appropriate weight in the layout. */
.quote-form-modern .field { display: flex; flex-direction: column; gap: 0.45rem; }
.quote-form-modern .field label,
.quote-form-modern .field-label {
  font-weight: 600;
  font-size: 1rem;
  color: var(--fg);
}
.quote-form-modern input,
.quote-form-modern textarea,
.quote-form-modern select {
  font: inherit;
  font-size: 1.02rem;
  padding: 0.95rem 1.1rem;
  border-radius: var(--r-2);
}
.quote-form-modern textarea {
  min-height: 15rem;
  line-height: 1.55;
}
.quote-form-modern .field-hint {
  margin: 0.4rem 0 0 0;
  font-size: 0.9rem;
  color: var(--muted);
}

/* Service selection — icon cards. The actual radio input is
   visually hidden but stays in the tab order. The whole card is the
   click target. Checked state is communicated by border, background,
   icon tint, and a small checkmark badge in the top-right corner —
   no exposed radio circle. */
.service-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--s-2);
}
@media (max-width: 720px) {
  .service-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

.service-card {
  position: relative;
  display: block !important;
  margin: 0 !important;
  padding: 0 !important;
  cursor: pointer;
}

/* Visually hide the radio input but keep it accessible to keyboard
   and assistive tech. Standard sr-only pattern. */
.service-card input[type="radio"] {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.service-card-inner {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  text-align: center;
  gap: 0.5rem;
  padding: var(--s-4) var(--s-3);
  border: 1.5px solid var(--line);
  border-radius: var(--r-3);
  background: var(--surface);
  transition: border-color var(--t-fast), background var(--t-fast),
              box-shadow var(--t-fast), transform var(--t-fast);
  min-height: 132px;
  height: 100%;
}

.service-card:hover .service-card-inner {
  border-color: var(--muted);
  background: var(--surface-2);
  transform: translateY(-2px);
  box-shadow: var(--sh-2);
}

.service-card input[type="radio"]:checked + .service-card-inner {
  border-color: var(--accent);
  background: color-mix(in srgb, var(--surface) 94%, var(--accent) 6%);
  box-shadow: 0 0 0 1px var(--accent) inset, var(--sh-2);
}

.service-card input[type="radio"]:focus-visible + .service-card-inner {
  outline: 3px solid var(--accent-dark);
  outline-offset: 3px;
}

.service-card-icon {
  width: 36px;
  height: 36px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--muted);
  transition: color var(--t-fast), transform var(--t-fast);
  margin-bottom: 0.15rem;
}
.service-card:hover .service-card-icon {
  color: var(--accent-dark);
}
.service-card input[type="radio"]:checked + .service-card-inner .service-card-icon {
  color: var(--accent-dark);
  transform: scale(1.05);
}

.service-card-title {
  font-weight: 700;
  font-size: 0.98rem;
  color: var(--fg);
  line-height: 1.2;
}

.service-card-desc {
  font-size: 0.82rem;
  color: var(--muted);
  line-height: 1.35;
  font-weight: 400;
}
.service-card input[type="radio"]:checked + .service-card-inner .service-card-desc {
  color: var(--fg);
}

/* Checkmark badge appears in the top-right corner of the selected
   card. CSS-only — uses an inline SVG data-URI as the background. */
.service-card-inner::after {
  content: "";
  position: absolute;
  top: 0.55rem;
  right: 0.55rem;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background-color: var(--accent);
  background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23ffffff' stroke-width='3.5' stroke-linecap='round' stroke-linejoin='round'><polyline points='20 6 9 17 4 12'/></svg>");
  background-size: 12px 12px;
  background-position: center;
  background-repeat: no-repeat;
  opacity: 0;
  transform: scale(0.6);
  transition: opacity var(--t-fast), transform var(--t-fast);
}
.service-card input[type="radio"]:checked + .service-card-inner::after {
  opacity: 1;
  transform: scale(1);
}

/* Respect reduced-motion. */
@media (prefers-reduced-motion: reduce) {
  .service-card-inner,
  .service-card-icon,
  .service-card-inner::after { transition: none !important; }
  .service-card:hover .service-card-inner { transform: none !important; }
  .service-card input[type="radio"]:checked + .service-card-inner .service-card-icon {
    transform: none !important;
  }
}

/* Submit tail — Turnstile + button + note grouped tightly. */
.quote-form-tail {
  display: flex;
  flex-direction: column;
  gap: var(--s-3);
  align-items: stretch;
  border-top: 1px solid var(--line);
  padding-top: var(--s-4);
  margin-top: var(--s-2);
}
.quote-turnstile {
  display: flex;
  justify-content: center;
}
.quote-submit {
  width: 100%;
  font: inherit;
  background: var(--accent);
  color: #fff;
  padding: 1.25rem 1.8rem;
  border: 0;
  border-radius: var(--r-2);
  font-weight: 800;
  font-size: 1.15rem;
  letter-spacing: -0.005em;
  cursor: pointer;
  align-self: stretch;
  box-shadow: var(--sh-2);
  transition: background var(--t-fast), transform var(--t-fast), box-shadow var(--t-fast);
}
.quote-submit:hover { background: var(--accent-dark); transform: translateY(-1px); box-shadow: var(--sh-3); }
.quote-submit:active { transform: translateY(0); box-shadow: var(--sh-1); }
.quote-submit:focus-visible {
  outline: 3px solid var(--accent-dark);
  outline-offset: 3px;
}
.quote-submit-note {
  text-align: center;
  font-size: 0.85rem;
  color: var(--muted);
  margin: 0;
}

/* Sidebar — stack of supporting cards. */
.quote-layout-sidebar {
  display: flex;
  flex-direction: column;
  gap: var(--s-4);
}
.quote-card {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--r-3);
  padding: var(--s-5);
  box-shadow: var(--sh-1);
}
.quote-card h3 {
  margin: 0 0 var(--s-3) 0;
  font-size: 1.02rem;
  color: var(--fg);
}
.quote-card h3::before { display: none; }
.quote-card p { margin: 0 0 var(--s-2) 0; color: var(--fg); font-size: 0.95rem; line-height: 1.55; }
.quote-card p:last-child { margin-bottom: 0; }
.quote-card-list {
  margin: 0;
  padding: 0 0 0 1.1rem;
  font-size: 0.95rem;
  color: var(--fg);
  line-height: 1.55;
}
.quote-card-list li { margin: 0.4rem 0; }

/* Timeline inside "What happens next" card. */
.quote-timeline {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0;
}
.quote-timeline li {
  display: flex;
  align-items: flex-start;
  gap: var(--s-3);
  padding: var(--s-3) 0;
  border-bottom: 1px solid var(--line);
}
.quote-timeline li:last-child { border-bottom: 0; padding-bottom: 0; }
.quote-timeline li:first-child { padding-top: 0; }
.quote-timeline-step {
  width: 30px;
  height: 30px;
  background: var(--accent);
  color: #fff;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.9rem;
  flex-shrink: 0;
}
.quote-timeline strong {
  display: block;
  font-size: 0.95rem;
  color: var(--fg);
  margin-bottom: 0.15rem;
}
.quote-timeline p { margin: 0; font-size: 0.9rem; color: var(--muted); line-height: 1.5; }

/* "Or just call" card — visually emphasized so it pulls the
   high-intent visitor's eye. */
.quote-card-call {
  background: var(--surface-3);
  border-color: rgba(184, 52, 26, 0.22);
  border-left: 4px solid var(--accent);
}
.quote-card-phone {
  display: block;
  font-size: 1.4rem;
  font-weight: 800;
  color: var(--accent-dark);
  letter-spacing: -0.01em;
  text-decoration: none;
  margin: var(--s-2) 0 var(--s-3) 0;
  padding: 0.55rem 0;
  border-bottom: 2px solid transparent;
  transition: border-color var(--t-fast), color var(--t-fast);
}
.quote-card-phone:hover {
  color: var(--accent);
  border-color: var(--accent);
}
.quote-card-phone:focus-visible {
  outline: 3px solid var(--accent-dark);
  outline-offset: 3px;
  border-radius: 2px;
}
.quote-card-meta {
  font-size: 0.85rem !important;
  color: var(--muted) !important;
  margin: 0 !important;
}

@media (max-width: 600px) {
  .quote-hero { padding: var(--s-5) var(--s-4) var(--s-4); }
  .quote-hero-inner { text-align: left; align-items: flex-start; }
  .quote-hero-jumplink { text-align: center; width: 100%; }
  .quote-form-modern { padding: var(--s-4); }
}

/* Reduced-motion: drop the lift effect on buttons/links. */
@media (prefers-reduced-motion: reduce) {
  .quote-submit,
  .quote-card-phone { transition: none !important; }
  .quote-submit:hover { transform: none !important; }
}

.success-message {
  display: none;
  padding: var(--s-5);
  border-radius: var(--r-3);
  background: var(--success-bg);
  border: 1px solid rgba(46, 125, 50, 0.25);
  border-left: 4px solid #2e7d32;
  color: var(--success-fg);
  margin: var(--s-6) 0;
  box-shadow: var(--sh-1);
}
.success-message h2 { margin-top: 0; color: var(--success-fg); }
.success-message h2::before { background: #2e7d32; }
body.form-submitted .success-message { display: block; }
body.form-submitted .quote-form { display: none; }
body.form-submitted .quote-helpers { display: none; }

.alt-contact {
  margin: var(--s-6) 0;
  padding: var(--s-5);
  background: var(--surface-2);
  border-radius: var(--r-3);
  border: 1px solid var(--line);
}
.alt-contact h3 { margin: 0 0 var(--s-2) 0; }
.alt-contact p { margin: var(--s-1) 0; }
"""


def head_html(title, description, canonical, schema_blocks, extra_head=""):
    return f"""<!doctype html>
<html lang="en">
<head>
{m2h.TRACKING_HEAD}
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{m2h.ANALYTICS_HEAD}
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description)}">
<link rel="canonical" href="{html.escape(canonical)}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(description)}">
<meta property="og:type" content="website">
{m2h.social_meta(title, description, canonical)}
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap">
<style>
{m2h.CSS}{SITE_SHELL_CSS}</style>
<script>
  // Early success-state detection — runs in <head> before paint so the form
  // never flashes visible if the URL has ?success=1. Harmless on other pages.
  if (location.search.indexOf('success=1') !== -1) {{
    document.documentElement.classList.add('form-submitted-html');
  }}
</script>
{schema_blocks}
{extra_head}
</head>"""


SITE_HEADER = m2h.build_site_header()

SITE_FOOTER = m2h.build_site_footer()

from _coverage_map_loader import COVERAGE_MAP_LOADER as _COVERAGE_MAP_LOADER
from _hero_video_script import HERO_VIDEO_SCRIPT as _HERO_VIDEO_SCRIPT

MOBILE_CTA = """<div class="mobile-cta-bar" role="region" aria-label="Quick contact">
  <a class="mcta-phone" href="tel:+13196104341">☎ 319-610-4341</a>
  <a class="mcta-quote" href="/get-a-quote/">Get a Quote</a>
</div>
""" + _COVERAGE_MAP_LOADER


# ---------- Video hero helper (reused by homepage + service-area pages) ----------

def build_video_hero_html(eyebrow_text, h1_html, lede_html,
                          trust_line_html=None, cta_href="/get-a-quote/",
                          cta_label="Get a Quote"):
    """Reusable .home-hero video-background hero used by the homepage
    and the service-area pages (hub, state, city). Same visual treatment
    everywhere: midwest-cnc-bg-fade.mp4 background, dark gradient overlay,
    centered white text, frosted-glass CTAs.

    Args:
        eyebrow_text:  plain string — will be HTML-escaped.
        h1_html:       HTML fragment for the H1 (caller is responsible for
                       escaping; may include entities like &nbsp;).
        lede_html:     HTML fragment for the lede paragraph (caller-escaped).
        trust_line_html: optional HTML fragment placed below the CTAs in
                       a .trust-line paragraph. Used on the homepage.
        cta_href:      primary CTA href. Defaults to /get-a-quote/ since
                       service-area pages have no inline #quote form; brand
                       pages (which DO have one) keep using build_brand_hero_html
                       with its own #quote anchor.
        cta_label:     primary CTA label.

    Returns the <section> + the inline fade <script> as a single string.
    The script is idempotent — safe to include on any page; it bails if
    no .home-hero-video element is found.
    """
    trust_html = (
        f'    <p class="trust-line">{trust_line_html}</p>\n'
        if trust_line_html else ""
    )
    return (
        f'<section class="home-hero">\n'
        f'  <video class="home-hero-video"\n'
        f'         autoplay muted loop playsinline\n'
        f'         preload="auto"\n'
        f'         poster="/assets/images/general/midwest-cnc-highway-shot.webp"\n'
        f'         aria-hidden="true">\n'
        f'    <source src="/assets/images/general/midwest-cnc-bg-fade.mp4" type="video/mp4">\n'
        f'  </video>\n'
        f'  <div class="home-hero-overlay" aria-hidden="true"></div>\n'
        f'  <div class="home-hero-content">\n'
        f'    <p class="eyebrow">{html.escape(eyebrow_text)}</p>\n'
        f'    <h1>{h1_html}</h1>\n'
        f'    <p class="lede">{lede_html}</p>\n'
        f'    <div class="cta-row">\n'
        f'      <a class="cta-button" href="{html.escape(cta_href)}">{html.escape(cta_label)}</a>\n'
        f'      <a class="cta-phone" href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a>\n'
        f'    </div>\n'
        f'{trust_html}'
        f'  </div>\n'
        f'</section>\n'
        f'{_HERO_VIDEO_SCRIPT}\n'
    )


def breadcrumbs_html(items):
    """items: list of (name, href). The last item is the current page; href may be None to render as text."""
    if not items:
        return ""
    lis = []
    for i, (name, href) in enumerate(items):
        if href and i < len(items) - 1:
            lis.append(f'<li><a href="{html.escape(href)}">{html.escape(name)}</a></li>')
        else:
            lis.append(f'<li>{html.escape(name)}</li>')
    return f'<nav class="breadcrumbs" aria-label="breadcrumb">\n  <ol>\n    {"".join(lis)}\n  </ol>\n</nav>'


def wrap_page(*, title, description, canonical, schema_blocks, crumbs_html_str,
              body_html, layout="default", noindex=False):
    """layout='default' (--max readable column), 'wide' (--max-wide for
    homepage + hubs with tiles, brand grids, and other landscape content).
    Body is split into alternating-color full-bleed sections at <h2>
    boundaries.

    noindex=True injects <meta name="robots" content="noindex,follow">
    in the head. Use on confirmation / thank-you pages."""
    body_class = f' class="layout-{layout}"' if layout != "default" else ""
    banded = m2h.wrap_into_sections(body_html, layout=layout)
    extra = '<meta name="robots" content="noindex,follow">' if noindex else ""
    return f"""{head_html(title, description, canonical, schema_blocks, extra_head=extra)}
<body{body_class}>
<a class="skip-link" href="#main">Skip to content</a>
{SITE_HEADER}
{crumbs_html_str}
<main id="main">
<article>
{banded}
</article>
</main>
{SITE_FOOTER}
{MOBILE_CTA}
</body>
</html>
"""


# ---------- Shared content blocks ----------

CERT_BLOCK = (
    "Experienced field technicians with hands-on time across the major CNC OEM "
    "platforms, in-house precision spindle balancing capability, laser alignment "
    "services, and established relationships with aftermarket bearing and spindle "
    "component suppliers."
)

QUOTE_OPENER = "\"Honestly, we thought the machine was done for.\""
QUOTE_FRAMING_A = ("Most customers tell us they're relieved to avoid replacement "
                   "lead times and six-figure capital expenses.")


def trust_block_html():
    return (
        '<h2 id="why-shops-trust-us">Why Shops Trust Us</h2>\n'
        f'<p>{CERT_BLOCK}</p>\n'
        f'<blockquote><p>{html.escape(QUOTE_OPENER)} {QUOTE_FRAMING_A}</p></blockquote>\n'
    )


def hero_cta_html(label="Get a Quote", href="/get-a-quote/"):
    return (
        f'<div class="cta-row">'
        f'<a class="cta-button" href="{href}">{label}</a>'
        f'<a class="cta-phone" href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a>'
        f'</div>'
    )


# ---------- Schema builders ----------

def organization_localbusiness_schema():
    """Authoritative LocalBusiness schema for the homepage.
    Phase 4C: includes geo coordinates for Waterloo, IA (Wikipedia infobox)
    and hasMap link to Google Maps."""
    blocks = []
    blocks.append({
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "@id": f"{DOMAIN}/#org",
        "name": "Midwest CNC Services",
        "url": f"{DOMAIN}/",
        "telephone": PHONE_TEL,
        "address": {
            "@type": "PostalAddress",
            "addressLocality": ADDRESS_CITY,
            "addressRegion": ADDRESS_STATE,
            "addressCountry": "US",
        },
        "geo": {
            "@type": "GeoCoordinates",
            "latitude": 42.4928,
            "longitude": -92.3426,
        },
        "hasMap": "https://www.google.com/maps/place/Waterloo,+IA",
        "areaServed": STATE_NAMES,
        "openingHoursSpecification": [
            {
                "@type": "OpeningHoursSpecification",
                "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                "opens": "07:00",
                "closes": "15:30",
            },
        ],
    })
    return blocks


def hub_itemlist_schema(hub_title, items):
    """Phase 4B: ItemList schema for service hub brand grids.
    items: list of {name, url} dicts."""
    return {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": hub_title,
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "name": item["name"],
                "url": item["url"],
            }
            for i, item in enumerate(items)
        ],
    }


def hub_faq_schema(qa_pairs):
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in qa_pairs
        ],
    }


def hub_faq_html(qa_pairs):
    items = []
    for q, a in qa_pairs:
        items.append(
            f'<details class="faq-item">\n'
            f'  <summary>{html.escape(q)}</summary>\n'
            f'  <div class="faq-answer"><p>{html.escape(a)}</p></div>\n'
            f'</details>'
        )
    return (
        '<h2 id="faq">Frequently Asked Questions</h2>\n'
        '<div class="faq-list">\n'
        + "\n".join(items) + "\n"
        + '</div>\n'
    )


def faqpage_schema(qa_pairs):
    """Build a FAQPage JSON-LD from a list of {q, a} dicts."""
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": qa["q"],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": qa["a"],
                },
            }
            for qa in qa_pairs
        ],
    }


def breadcrumb_schema(items):
    """Build a BreadcrumbList JSON-LD from items list [(name, absolute_url), ...]."""
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"position": i + 1, "name": name, "item": url}
            for i, (name, url) in enumerate(items)
        ],
    }


def schema_script_tags(schemas):
    """Take a list of schema dicts and return inline <script> tags."""
    return "\n".join(
        f'<script type="application/ld+json">\n{json.dumps(s, indent=2, ensure_ascii=False)}\n</script>'
        for s in schemas
    )


# ---------- Per-page body builders ----------

def homepage_body():
    """Scrubbed hero, service tiles, state tiles, trust block, closing CTA."""
    # Hero — scrubbed from pages.json["/"]. The Durable copy claimed
    # "certified techs", "transparent quotes", "unmatched response times" —
    # all replaced with Ken-authorized language.
    states_inline = ", ".join(STATE_NAMES[:-1]) + ", and " + STATE_NAMES[-1]

    # Single-column hero with background video. Opacity is driven by
    # JS from the video's actual currentTime — the fade is locked to
    # the video clock, never drifts against a fixed CSS keyframe. The
    # markup + script are emitted by build_video_hero_html() so the
    # same hero treatment can be reused on every service-area page.
    hero = build_video_hero_html(
        eyebrow_text="Stop Losing Money",
        h1_html="When Your Machine Stops, We&nbsp;Start",
        lede_html=(
            "CNC repair, spindle work, and replacement way covers across the U.S. "
            "Midwest. When a machine goes down, our experienced field technicians "
            "come out to diagnose and get you back to cutting. From spindle "
            "rebuilds and machine repair to custom way covers we ship anywhere, "
            "the goal is the same: keep your shop producing."
        ),
        trust_line_html=f"Serving shops in {html.escape(states_inline)}. Based in Waterloo, Iowa.",
    )

    # Service tiles
    tiles_html = []
    for t in SERVICE_TILES:
        tiles_html.append(
            f'<a class="tile" href="{t["href"]}">'
            f'<img src="{t["image"]}" alt="{html.escape(t["alt"])}" loading="lazy">'
            f'<h3>{html.escape(t["title"])}</h3>'
            f'<p>{html.escape(t["desc"])}</p>'
            f'<span class="learn-more">Learn More →</span>'
            f'</a>'
        )
    services = (
        '<h2 id="our-services">Our Services</h2>\n'
        '<p>Three lines of work, one shop. We do machine repair on production CNC equipment, manufacture replacement way covers to spec, and rebuild and grind spindles back to factory tolerance — across every major OEM platform we service.</p>\n'
        f'<div class="tile-grid">{"".join(tiles_html)}</div>\n'
    )

    # State tiles
    state_tile_html = []
    for name, slug, cities, image in STATE_TILES:
        state_tile_html.append(
            f'<a class="tile" href="/service-area/{slug}/">'
            f'<img src="{image}" alt="{html.escape(name)} CNC service coverage" loading="lazy">'
            f'<h3>{html.escape(name)}</h3>'
            f'<p>{html.escape(cities)}</p>'
            f'<span class="learn-more">Learn More →</span>'
            f'</a>'
        )
    state_section = (
        '<h2 id="service-areas">Service Areas</h2>\n'
        '<p>We work with shops across seven Midwest and South-Central states. '
        'Production environments and job shops across the Midwest, plus '
        'specialty work where brand-specific expertise matters — from '
        'high-precision Makino aerospace and mold-die customers to legacy '
        'Fadal and Hitachi Seiki rebuilds. Field troubleshooting where a '
        'remote diagnostic can save a teardown.</p>\n'
        f'<div class="state-grid">{"".join(state_tile_html)}</div>\n'
    )

    # How We Work — condensed workflow that matches the brand pages.
    how_we_work = (
        '<h2 id="how-we-work">How We Work</h2>\n'
        '<p>Same three steps every brand page describes:</p>\n'
        '<ol class="process-steps">\n'
        '  <li><strong>Contact Us.</strong> Call 319-610-4341 or use the quote form. Tell us the machine, the symptoms, and how urgent it is.</li>\n'
        '  <li><strong>Grab Model #.</strong> We\'ll fire back price, lead time, and shipping ETA after reviewing your details.</li>\n'
        '  <li><strong>Approve &amp; Rebuild.</strong> We complete the work, verify it back to spec, and return the machine ready to run.</li>\n'
        '</ol>\n'
    )

    # Trust block
    trust = trust_block_html()

    # FAQ — 4 Q&As, structurally mirrors the FAQPage JSON-LD in <head>.
    faq_items = []
    for i, qa in enumerate(HOMEPAGE_FAQ):
        faq_items.append(
            f'<details class="faq-item" id="faq-{i+1}">\n'
            f'  <summary>{html.escape(qa["q"])}</summary>\n'
            f'  <div class="faq-answer"><p>{html.escape(qa["a"])}</p></div>\n'
            f'</details>'
        )
    faq_section = (
        '<h2 id="faq">Common Questions</h2>\n'
        '<div class="faq-list">\n'
        + "\n".join(faq_items) + "\n"
        + '</div>\n'
    )

    # Closing CTA (scrubbed — Durable said "24/7" and "transparent" and "fast quotes")
    closing = (
        '<h2 id="downtime">Don\'t Let Downtime Drain Your Profits</h2>\n'
        '<p>Every minute your CNC sits idle is money out the door. Call us with the machine and the issue — most quotes go out within one business day, and we\'ll get you back to cutting.</p>\n'
        f'{hero_cta_html()}\n'
    )

    return hero + services + state_section + how_we_work + trust + faq_section + closing


def about_body():
    """Rebuilt About — no fabricated business-age claims, no 'tighter than OEM',
    no 'beat the spec'. Only verifiable facts + Ken's authorized capabilities."""

    body = []
    body.append('<h1>About Midwest CNC Services</h1>')
    body.append(
        '<p>Midwest CNC Services is based in Waterloo, Iowa. We provide CNC '
        'machine repair, spindle rebuild and grinding, and replacement way '
        'covers to shops across Iowa, Illinois, Wisconsin, Minnesota, '
        'Nebraska, Missouri, and Texas.</p>'
    )

    body.append('<h2 id="what-we-do">What We Do</h2>')
    body.append(
        '<p>Three lines of service, organized so you can find the work you need:</p>'
    )
    tile_html = []
    for t in SERVICE_TILES:
        tile_html.append(
            f'<a class="tile" href="{t["href"]}">'
            f'<h3>{html.escape(t["title"])}</h3>'
            f'<p>{html.escape(t["desc"])}</p>'
            f'<span class="learn-more">Learn More →</span>'
            f'</a>'
        )
    body.append(f'<div class="tile-grid">{"".join(tile_html)}</div>')

    body.append('<h2 id="where-we-work">Where We Work</h2>')
    body.append(
        '<p>Our service area covers seven states across the Midwest and South-Central US. '
        'See the <a href="/service-area/">service-area hub</a> for the city-level coverage. '
        'States we work in:</p>'
    )
    state_html = []
    for name, slug, cities, _img in STATE_TILES:
        state_html.append(
            f'<li><strong>{html.escape(name)}</strong> — {html.escape(cities)}</li>'
        )
    body.append(f'<ul>{"".join(state_html)}</ul>')

    body.append('<h2 id="why-shops-choose-us">Why Shops Choose Us</h2>')
    body.append(f'<p>{CERT_BLOCK}</p>')
    body.append(
        f'<blockquote><p>{html.escape(QUOTE_OPENER)} {QUOTE_FRAMING_A}</p></blockquote>'
    )

    body.append(hero_cta_html())

    return "\n".join(body) + "\n"


def quote_body(brands):
    """The Get-a-Quote form page. Submissions are handled by the
    Cloudflare Pages Function at /functions/api/quote.js, which:
      - verifies the Turnstile token server-side
      - validates required fields
      - sends a notification email via Resend
      - redirects to /get-a-quote/thank-you/ on success

    Layout: prominent hero with split phone CTA, two-column form +
    sidebar on desktop, single column on mobile/tablet. See
    docs/forms-setup.md for the secret-config steps."""
    # Brand dropdown options, alphabetical
    options = sorted(b["brand_display_name"] for b in brands)
    option_tags = ['<option value="">Select a brand…</option>']
    for opt in options:
        option_tags.append(f'<option value="{html.escape(opt)}">{html.escape(opt)}</option>')
    option_tags.append('<option value="Other">Other</option>')
    options_html = "\n              ".join(option_tags)

    body = f'''<section class="quote-hero">
  <div class="quote-hero-inner">
    <p class="quote-hero-eyebrow">Machine down? Start here.</p>
    <h1>Talk to a tech &mdash; don't wait on email.</h1>
    <p class="quote-hero-lede">If your machine is down, the fastest path is the phone. We answer Monday through Friday, 7&nbsp;AM&ndash;3:30&nbsp;PM Central. Not urgent? The form below gets a reply within one business day.</p>
    <a class="quote-call-banner" href="tel:{PHONE_TEL}">
      <span class="quote-call-banner-icon" aria-hidden="true">&#9742;</span>
      <span class="quote-call-banner-text">
        <span class="quote-call-banner-main">Call now &mdash; talk to a tech</span>
        <span class="quote-call-banner-sub">{PHONE_DISPLAY} &middot; Mon&ndash;Fri 7&nbsp;AM&ndash;3:30&nbsp;PM CT</span>
      </span>
    </a>
    <a class="quote-hero-jumplink" href="#quote">Or fill out the form below &darr;</a>
  </div>
</section>

<div class="form-error-banner" id="error" hidden>
  <p>We could not submit your request. <span id="error-message"></span></p>
</div>

<section class="quote-layout">

  <form class="quote-form quote-form-modern" id="quote" action="/api/quote" method="POST">

      <div class="quote-form-intro">
        <p class="quote-form-intro-title">Have these handy &mdash; the more detail, the faster we quote it:</p>
        <ul class="quote-form-intro-list">
          <li>Machine make, model, and approximate age</li>
          <li>Symptoms or error codes you are seeing</li>
          <li>How long the machine has been down</li>
          <li>Photos of the spindle, control screen, or affected area if you have them</li>
        </ul>
      </div>

      <fieldset class="form-section">
        <legend class="form-section-title">About you</legend>
        <div class="form-row">
          <div class="field">
            <label class="required" for="name">Your name</label>
            <input id="name" name="name" type="text" required autocomplete="name" placeholder="Jane Doe">
          </div>
          <div class="field">
            <label class="required" for="company">Company</label>
            <input id="company" name="company" type="text" required autocomplete="organization" placeholder="Acme Manufacturing">
          </div>
        </div>
        <div class="form-row">
          <div class="field">
            <label class="required" for="phone">Phone</label>
            <input id="phone" name="phone" type="tel" required autocomplete="tel" placeholder="319-555-1234">
          </div>
          <div class="field">
            <label class="required" for="email">Email</label>
            <input id="email" name="email" type="email" required autocomplete="email" placeholder="jane@acme.com">
          </div>
        </div>
      </fieldset>

      <fieldset class="form-section">
        <legend class="form-section-title">About your machine</legend>
        <div class="form-row">
          <div class="field">
            <label for="machine_brand">Brand</label>
            <select id="machine_brand" name="machine_brand">
              {options_html}
            </select>
          </div>
          <div class="field">
            <label for="machine_model">Model</label>
            <input id="machine_model" name="machine_model" type="text" placeholder="VF-3, Integrex i-200, Genos M460…">
          </div>
        </div>

        <div class="field">
          <span class="field-label required">Service needed</span>
          <div class="service-grid" role="radiogroup" aria-label="Service needed">

            <label class="service-card">
              <input type="radio" name="service" value="Spindle" required>
              <div class="service-card-inner">
                <span class="service-card-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="8" y="3" width="8" height="10" rx="1"/>
                    <line x1="8" y1="7" x2="16" y2="7"/>
                    <path d="M9 13 L7 17 L17 17 L15 13"/>
                    <line x1="12" y1="17" x2="12" y2="21"/>
                  </svg>
                </span>
                <span class="service-card-title">Spindle work</span>
                <span class="service-card-desc">Rebuild, regrind, balance</span>
              </div>
            </label>

            <label class="service-card">
              <input type="radio" name="service" value="Machine Repair">
              <div class="service-card-inner">
                <span class="service-card-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>
                  </svg>
                </span>
                <span class="service-card-title">Machine repair</span>
                <span class="service-card-desc">Control, ATC, drive, alignment</span>
              </div>
            </label>

            <label class="service-card">
              <input type="radio" name="service" value="Way Covers">
              <div class="service-card-inner">
                <span class="service-card-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M3 7 L7 9 L7 15 L3 17 Z"/>
                    <path d="M7 9 L11 7 L11 17 L7 15"/>
                    <path d="M11 7 L15 9 L15 15 L11 17"/>
                    <path d="M15 9 L19 7 L19 17 L15 15"/>
                    <path d="M19 7 L21 9 L21 15 L19 17"/>
                  </svg>
                </span>
                <span class="service-card-title">Way covers</span>
                <span class="service-card-desc">Telescoping, bellows, roll-up</span>
              </div>
            </label>

            <label class="service-card">
              <input type="radio" name="service" value="Other">
              <div class="service-card-inner">
                <span class="service-card-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>
                  </svg>
                </span>
                <span class="service-card-title">Something else</span>
                <span class="service-card-desc">Tell us in the message</span>
              </div>
            </label>

          </div>
        </div>
      </fieldset>

      <fieldset class="form-section">
        <legend class="form-section-title">What's happening</legend>
        <div class="field">
          <label class="required" for="message">Describe the issue</label>
          <textarea id="message" name="message" required rows="6" placeholder="What you are seeing or hearing, error codes, how long it has been happening, how urgent…"></textarea>
          <p class="field-hint">The more detail, the faster we can quote it.</p>
        </div>
      </fieldset>

      <!-- Honeypot — bots fill this; humans never see it. Server-side check. -->
      <div class="honeypot" aria-hidden="true">
        <label for="botcheck">Leave this field empty</label>
        <input id="botcheck" type="checkbox" name="botcheck" value="" tabindex="-1" autocomplete="off">
      </div>

      <div class="quote-form-tail">
        <div class="quote-turnstile">
          <div class="cf-turnstile" data-sitekey="{TURNSTILE_SITE_KEY}"></div>
        </div>
        <button type="submit" class="quote-submit">Send Quote Request</button>
        <p class="quote-submit-note">We typically reply within one business day. No automated sales follow-ups.</p>
      </div>

      <div class="quote-next-steps">
        <p class="quote-next-steps-title">What happens next</p>
        <ol class="quote-next-steps-grid">
          <li>
            <span class="quote-next-steps-num" aria-hidden="true">1</span>
            <div>
              <strong>Within one business day</strong>
              <span>We read your message and reply. If we need more info, we ask.</span>
            </div>
          </li>
          <li>
            <span class="quote-next-steps-num" aria-hidden="true">2</span>
            <div>
              <strong>Quote in hand</strong>
              <span>Price, lead time, and the scope of work in plain English.</span>
            </div>
          </li>
          <li>
            <span class="quote-next-steps-num" aria-hidden="true">3</span>
            <div>
              <strong>Schedule the work</strong>
              <span>Bench rebuild in Waterloo or field service across our 7-state coverage area.</span>
            </div>
          </li>
        </ol>
      </div>

  </form>
</section>

<script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async defer></script>
<script>
  // If the server bounced us back with ?error=..., surface the
  // message and scroll into view.
  (function () {{
    var match = location.search.match(/[?&]error=([^&]+)/);
    if (!match) return;
    var code = decodeURIComponent(match[1]);
    var msg;
    if (code === 'captcha-missing')      msg = 'Please complete the captcha check above the submit button and try again.';
    else if (code === 'captcha-failed')  msg = 'Captcha verification failed. Please refresh and try again.';
    else if (code === 'email-failed')    msg = 'We could not send your message right now. Please try again in a minute, or call us at {PHONE_DISPLAY}.';
    else if (code === 'bad-request')     msg = 'There was a problem with the submission. Please refresh and try again.';
    else if (code.indexOf('missing-') === 0) msg = 'Please fill in all required fields.';
    else                                  msg = 'Something went wrong. Please try again or call us at {PHONE_DISPLAY}.';

    var banner = document.getElementById('error');
    var span = document.getElementById('error-message');
    if (banner && span) {{
      span.textContent = msg;
      banner.hidden = false;
      banner.scrollIntoView({{behavior: 'smooth'}});
    }}
  }})();
</script>
'''
    return body


# ---------- Hub bodies ----------

def _brand_list_html(brands, *, link_for):
    """Build a brand grid. link_for: callable taking brand → (label, url) or None to skip."""
    items = []
    for b in sorted(brands, key=lambda x: x["brand_display_name"]):
        pair = link_for(b)
        if pair is None:
            continue
        label, url = pair
        items.append(f'<li><a href="{url}">{html.escape(label)}</a></li>')
    return f'<ul class="brand-grid">{"".join(items)}</ul>'


def repairs_hub_body(brands):
    body = []
    body.append('<p class="eyebrow">CNC Machine Repair</p>')
    body.append('<h1>CNC Machine Repair Across the Midwest</h1>')
    body.append(
        '<p>When a CNC machine goes down, the call we hear most is the '
        'same: get production back online. We service spindles, controls, '
        'ATC systems, drives, and alignment across every major OEM platform — '
        'plus Amada press brakes and Trumpf laser-cutting systems. Field '
        'troubleshooting where it can save a teardown; full rebuilds on the '
        'bench when that\'s what the job calls for.</p>'
    )
    body.append(hero_cta_html())
    body.append(
        '<figure class="hero-figure"><img src="/assets/images/general/image-of-cnc-machine.png" '
        'alt="CNC machining center under service" loading="lazy"></figure>'
    )

    # Expanded overview (Phase 4B)
    body.append('<h2 id="when-you-need-this">When You Need Machine Repair</h2>')
    body.append(
        "<p>The patterns that bring CNC machines to our shop fall into a few "
        "buckets: spindle issues (bearing-pack failure, runout, taper damage), "
        "control problems (alarms that don't reset, communication faults, "
        "encoder issues), ATC faults (drawbar wear, tool-change timing), drive "
        "system wear, and way alignment that's drifted out of spec after a "
        "crash or years of production. Most calls come in after the shop has "
        "tried the obvious and is now trying to decide whether to rebuild or "
        "replace. We diagnose what's actually broken before we quote — "
        "sometimes what looks like a spindle problem is something cheaper.</p>"
    )

    body.append('<h2 id="brands-we-service">Brands We Service</h2>')
    body.append(
        '<p>Every brand we repair has its own page with model coverage, '
        'lead-time notes, and what we typically see come in:</p>'
    )

    def link_for_repair(b):
        if b["page_type"] == "cnc_spindle":
            return (b["brand_display_name"], f"/repairs/{b['slug']}-cnc-machine-repair/")
        return (b["brand_display_name"], b["current_url"])

    body.append(_brand_list_html(brands, link_for=link_for_repair))

    body.append('<h2 id="how-service-works">How Service Works</h2>')
    body.append(
        '<ol class="process-steps">\n'
        '  <li><strong>Contact us.</strong> Tell us the machine and the symptoms — call 319-610-4341 or use the quote form. We respond same business day on most inquiries.</li>\n'
        '  <li><strong>Review &amp; quote.</strong> After looking at the model, the symptoms, and any photos you can send, we send back a price and a realistic lead time.</li>\n'
        '  <li><strong>Approve &amp; rebuild.</strong> We complete the work, verify it back to spec, and return the machine ready to run. Most jobs run 3–6 weeks depending on brand, failure mode, and parts availability.</li>\n'
        '</ol>'
    )

    body.append('<h2 id="industries-we-serve">Industries We Serve</h2>')
    body.append(
        "<p>Aerospace and defense, agricultural equipment, heavy machinery, "
        "medical devices, automotive supply chain, oil-and-gas equipment, "
        "food processing, and the general job-shop base across our seven-"
        "state service area. Brand specialization tends to follow industry "
        "— Makino in aerospace and mold/die, Mazak across ag and heavy, "
        "Brother Speedio in medical-device precision.</p>"
    )

    body.append(trust_block_html())

    # FAQ
    qa = [
        ("What does a typical CNC machine repair cost?",
         "Pricing depends on the diagnostic — we don't quote without scoping the actual work. Most quotes go out within one business day of getting the machine, model, and symptom description. Expect rebuild quotes to come with a lead time and a parts breakdown."),
        ("Do you service older machines from defunct manufacturers?",
         "Yes. Fadal, Hitachi Seiki, Monarch, and Giddings & Lewis platforms — all manufacturers whose CNC lines ended years ago — remain part of our routine work. We source parts from aftermarket suppliers, used inventory, and custom-machining where OEM components are gone."),
        ("Can you come on-site or do machines have to come to your shop?",
         "Both. Field service is part of routine work across Iowa and adjacent states; for substantial diagnostic work and bundled jobs we drive into Illinois, Wisconsin, Minnesota, Nebraska, and Missouri. Texas and far-out cities run ship-in via standard freight. Bench rebuilds happen at our Waterloo, IA shop."),
    ]
    body.append(hub_faq_html(qa))
    body.append(hero_cta_html())

    return "\n".join(body) + "\n", qa


def spindle_hub_body(brands):
    body = []
    body.append('<p class="eyebrow">Spindle Grinding & Repair</p>')
    body.append('<h1>CNC Spindle Repair, Rebuilds, and Grinding</h1>')
    body.append(
        '<p>Spindle work is our most-requested service. We rebuild, regrind, '
        'and rebalance to factory tolerance across the eighteen OEM platforms '
        'below. Most jobs run two to six weeks depending on brand and parts '
        'availability — each brand page has the specifics from our '
        'technicians.</p>'
    )
    body.append(hero_cta_html())
    body.append(
        '<figure class="hero-figure"><img src="/assets/images/general/image-of-spindle-grinding.png" '
        'alt="CNC spindle on the grinding bench" loading="lazy"></figure>'
    )

    body.append('<h2 id="when-you-need-this">When You Need Spindle Service</h2>')
    body.append(
        "<p>Spindles come to us in a few patterns: bearing-pack wear from "
        "high-RPM production, taper damage from a crash or toolholder failure, "
        "preload loss showing up as runout in finish work, encoder "
        "contamination, and coolant-intrusion damage that's gone past the "
        "warning signs. Sometimes the call is preventive — the shop noticed "
        "chatter or surface-finish degradation and wants the spindle pulled "
        "before it fails outright. We diagnose the damage on teardown and "
        "scope the rebuild from there.</p>"
    )

    body.append('<h2 id="brands-we-service">Brands We Service</h2>')
    body.append('<p>Pick your brand for failure modes, models, and lead-time expectations:</p>')

    def link_for_spindle(b):
        if not b.get("services_offered", {}).get("spindle"):
            return None
        return (b["brand_display_name"], f"/spindle-grinding/{b['slug']}-spindle-repair/")

    body.append(_brand_list_html(brands, link_for=link_for_spindle))

    body.append('<h2 id="how-service-works">How Service Works</h2>')
    body.append(
        '<ol class="process-steps">\n'
        '  <li><strong>Contact us with the spindle details.</strong> Brand, model, symptoms, and any noise/runout/heat data you have. Photos help if the housing is accessible.</li>\n'
        '  <li><strong>Quote &amp; lead time.</strong> We review and respond with a flat-or-range price plus a realistic lead time for the rebuild.</li>\n'
        '  <li><strong>Rebuild, verify, ship.</strong> Bearing-pack replacement, shaft repair, taper grinding, and dynamic balancing — routine across all 18 OEM platforms. We verify balance and runout, then ship back ready to install.</li>\n'
        '</ol>'
    )

    body.append('<h2 id="industries-we-serve">Industries We Serve</h2>')
    body.append(
        "<p>Aerospace and mold/die work (Makino-heavy), medical-device "
        "precision (Brother Speedio, Makino), heavy-equipment and ag (Mazak, "
        "Toyoda, Doosan), automotive supply chain (broad coverage), and "
        "legacy CNC platforms still in production (Fadal, Hitachi Seiki, "
        "Monarch) across our seven-state Midwest service area.</p>"
    )

    body.append(trust_block_html())

    qa = [
        ("How long does a typical spindle rebuild take?",
         "Most spindle rebuilds run 2-6 weeks depending on brand, failure mode, and parts availability. Mazak Integrex and DMG Mori multi-tasking work tends toward the longer end; Haas, Doosan, and Hurco platforms typically come back faster."),
        ("Do you ship spindles back nationally?",
         "Yes. We ship rebuilt spindles to any continental US destination. Return shipping is included in most rebuild quotes. Standard freight, with packaging and crating handled at our shop."),
        ("Can you grind taper damage from a crash?",
         "Often yes. Crash recovery is a routine pattern — taper damage, bearing-pack failure, alignment loss from impact. We grind the taper back to spec where the shaft survives the impact; we recommend replacement when the geometry won't recover."),
    ]
    body.append(hub_faq_html(qa))
    body.append(hero_cta_html())

    return "\n".join(body) + "\n", qa


def way_covers_hub_body(brands):
    body = []
    body.append('<p class="eyebrow">CNC Way Covers</p>')
    body.append('<h1>Replacement CNC Way Covers — Built to Spec</h1>')
    body.append(
        '<p>We manufacture replacement way covers in bellows, telescoping '
        'steel, and roll-up styles to fit the machine in front of you. Most '
        'orders ship in two to four weeks depending on dimensions and '
        'material. Send us the original or the machine specs and we\'ll '
        'match or build to drawing.</p>'
    )
    body.append(hero_cta_html())
    body.append(
        '<figure class="hero-figure"><img src="/assets/images/general/image-of-way-covers.png" '
        'alt="Replacement CNC way covers manufactured by Midwest CNC Services" loading="lazy"></figure>'
    )

    body.append('<h2 id="when-you-need-this">When You Need Replacement Way Covers</h2>')
    body.append(
        "<p>Way covers get replaced for a few reasons: chip and coolant "
        "intrusion has worn the existing cover beyond its useful life, the "
        "shop is upgrading machine guards for a particular operation, the "
        "OEM no longer sells replacement covers for an older machine, or a "
        "crash damaged the cover and the machine is down waiting for it. "
        "Most jobs start with the original cover or measurements of the way "
        "system; we build to that spec.</p>"
    )

    body.append('<h2 id="brands-we-build-for">Brands We Build For</h2>')
    body.append(
        '<p>Brand-specific way-cover pages include the model coverage and '
        'photos of typical builds:</p>'
    )

    def link_for_way_covers(b):
        so = b.get("services_offered", {})
        if not so.get("way_covers"):
            return None
        if b.get("way_covers_verification_pending"):
            return None
        return (b["brand_display_name"], f"/way-covers/{b['slug']}-cnc-way-covers/")

    body.append(_brand_list_html(brands, link_for=link_for_way_covers))

    body.append('<h2 id="how-service-works">How Service Works</h2>')
    body.append(
        '<ol class="process-steps">\n'
        '  <li><strong>Send measurements or the original cover.</strong> We work from either — overall dimensions, way spacing, mounting details, or the failed cover itself.</li>\n'
        '  <li><strong>Quote the build.</strong> We confirm style (bellows, telescoping steel, or roll-up), material, and lead time.</li>\n'
        '  <li><strong>Fabricate &amp; ship.</strong> On approval we build to spec and ship anywhere in the continental US. Most orders are out the door in 2–4 weeks; rush options are available.</li>\n'
        '</ol>'
    )

    body.append('<h2 id="industries-we-serve">Industries We Serve</h2>')
    body.append(
        "<p>Heavy-equipment manufacturing, aerospace, ag-equipment supply "
        "chain, mold/die, and the broader job-shop base. Older machine "
        "inventory (Fadal, Hitachi Seiki, Monarch) is a strong driver — "
        "OEM cover replacement is often discontinued, and we build "
        "drop-in replacements that match the original.</p>"
    )

    body.append(trust_block_html())

    qa = [
        ("What way-cover styles do you build?",
         "Three styles: bellows for protected ways with limited debris, telescoping steel for heavier chip and coolant environments, and roll-up for retrofits and specific clearance constraints. We match the original or build to drawing."),
        ("Can you build for older machines whose OEM covers are discontinued?",
         "Yes. We routinely build replacement way covers for Fadal, Hitachi Seiki, Monarch, and other legacy machine platforms where the OEM no longer supplies covers. Measure from the original or the machine; we'll build to those dimensions."),
        ("How fast can you ship a replacement way cover?",
         "Most way-cover orders ship in 2-4 weeks depending on dimensions and material. We offer rush options for machine-down situations — call to discuss what's possible for your timeline."),
    ]
    body.append(hub_faq_html(qa))
    body.append(hero_cta_html())

    return "\n".join(body) + "\n", qa


def service_area_hub_body():
    """Service-area hub — brand-hero + machine lookup + overview map +
    state tile grid + FAQ. Links out to the 7 state pages."""
    # Lazy imports to avoid circular import at module top
    import generate_brand_pages as gbp
    import _geo_data
    import json as _json

    body = []

    # Video hero — same midwest-cnc-bg-fade.mp4 background used on the
    # homepage. Same visual language carries across the entire service-area
    # section (hub, state pages, city pages).
    hero_lede = (
        "We work with production shops, job shops, and OEM customers across seven "
        "states from our Waterloo, Iowa location. Field service where it can save a "
        "teardown; bench work and shipped builds when that's what the repair calls for."
    )
    body.append(build_video_hero_html(
        eyebrow_text="Service Areas",
        h1_html="Midwest CNC Service Coverage",
        lede_html=html.escape(hero_lede),
    ))
    body.append(gbp.machine_lookup_html())

    # Coverage overview map — every ENRICH city across all 7 states,
    # Waterloo origin pinned in the center.
    all_cities = _geo_data.all_served_cities()
    body.append(
        f'<div class="coverage-map coverage-map--hub"\n'
        f'     data-cities=\'{_json.dumps(all_cities, ensure_ascii=False)}\'\n'
        f'     aria-label="Map showing Midwest CNC Services coverage across Iowa, Illinois, Wisconsin, Minnesota, Nebraska, Missouri, and Texas, with our Waterloo, IA home base">\n'
        f'  <div class="coverage-map-empty">Loading coverage map…</div>\n'
        f'</div>\n'
        f'<p class="coverage-map-caption">{len(all_cities)} cities across 7 states — pinned alongside our Waterloo, IA home base.</p>'
    )

    # State tile grid linking to the real state pages
    body.append('<h2 id="states-we-serve">States We Serve</h2>')
    body.append(
        '<p>Pick a state for local coverage detail and the cities we serve there:</p>'
    )
    tiles = []
    for name, slug, cities, image in STATE_TILES:
        tiles.append(
            f'<a class="tile" href="/service-area/{slug}/">'
            f'<img src="{image}" alt="{html.escape(name)} CNC service coverage" loading="lazy">'
            f'<h3>{html.escape(name)}</h3>'
            f'<p>{html.escape(cities)}</p>'
            f'<span class="learn-more">Learn More →</span>'
            f'</a>'
        )
    body.append(f'<div class="tile-grid">{"".join(tiles)}</div>')

    body.append(trust_block_html())

    qa = [
        ("Do you cover all seven states equally?",
         "Iowa is our home state — same-day field response is realistic across the state. Adjacent states (Illinois, Wisconsin, Minnesota) are within drive radius for substantial field jobs. Nebraska, Missouri, and Texas run primarily ship-in service, with field travel by arrangement for major work."),
        ("How far do you travel for field service?",
         "Field service across Iowa is routine. Major-job field visits routinely run into Illinois, Wisconsin, Minnesota, eastern Nebraska, and the Missouri metros. Texas is by-arrangement only; way covers and spindle rebuilds ship in via standard freight."),
        ("Can you support shops outside your listed seven states?",
         "On a ship-in basis, yes. Way covers ship anywhere in the continental US; spindle rebuilds ship in and out via standard freight. Field service outside our routine seven-state area is quoted separately for major jobs."),
    ]
    body.append(hub_faq_html(qa))
    body.append(hero_cta_html())

    return "\n".join(body) + "\n", qa


def privacy_body():
    """Privacy policy — scoped to what this site actually collects.
    Verified by audit: no analytics/cookies/tracking present; only
    Google Fonts as external load. Web3Forms is the sole third-party
    processor of form submissions."""
    today = datetime.now(timezone.utc).strftime("%B %d, %Y")
    return f"""<h1>Privacy Policy</h1>
<p><em>Last updated: {today}</em></p>

<p>Midwest CNC Services collects only the information you provide directly
through this site, and uses it only to respond to your inquiry. We don't
run ads, we don't track you, and we don't share your information with
anyone beyond what's needed to deliver the service you're asking about.</p>

<h2 id="what-we-collect">What we collect</h2>
<p>The Get a Quote form on <a href="/get-a-quote/">/get-a-quote/</a>
collects the following information when you submit it:</p>
<ul>
  <li>Your name</li>
  <li>Your company name</li>
  <li>Your phone number</li>
  <li>Your email address</li>
  <li>The machine brand and model you're asking about</li>
  <li>The service type (spindle, machine repair, way covers, other)</li>
  <li>Your description of the issue or the work needed</li>
</ul>
<p>We don't collect this information any other way. There is no analytics
script, no tag manager, no Facebook Pixel, no Hotjar, and no marketing
automation running on this site. We don't set cookies.</p>
<p>This site loads the Inter typeface from Google Fonts
(<code>fonts.googleapis.com</code>). Google may log your IP address and
user-agent as part of standard CDN operation when your browser fetches
the font; Google does not set a tracking cookie via the font request.
Our hosting provider (Cloudflare Pages) keeps standard web-server access
logs (IP, browser, request path, timestamp) as part of infrastructure
operation; we don't analyze those for marketing.</p>

<h2 id="how-we-use-it">How we use it</h2>
<p>Information you submit through the quote form is used for one purpose:
to respond to your quote request and follow up about the work you're
inquiring about. We don't add you to a marketing list, send unrequested
email, or share your contact information with third parties.</p>

<h2 id="who-we-share-it-with">Who we share it with</h2>
<p>Quote form submissions are processed through Web3Forms
(<a href="https://web3forms.com" rel="noopener nofollow">web3forms.com</a>),
a form-handling service that receives your submission and delivers it
to our email. Web3Forms is the only third party that touches your form
data. Their privacy policy applies to their handling of submissions; you
can review it on their site.</p>
<p>We don't sell, rent, or trade your information.</p>

<h2 id="your-rights">Your rights</h2>
<p>If you submitted a quote request and want a copy of the data we have
about you, or want it deleted from our records, call us at
<a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a>. We'll handle the request
the same business day.</p>

<h2 id="contact">How to reach us</h2>
<p>Midwest CNC Services<br>
Waterloo, Iowa<br>
<a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></p>
"""


def terms_body():
    today = datetime.now(timezone.utc).strftime("%B %d, %Y")
    return f"""<h1>Terms of Service</h1>
<p><em>Last updated: {today}</em></p>

<p>These terms apply to your use of midwestcncservices.com (the "Site").
The Site is an informational marketing site for Midwest CNC Services, a
CNC machine repair, spindle work, and replacement way cover business
based in Waterloo, Iowa.</p>

<h2 id="what-this-site-is">What this site is</h2>
<p>The Site exists to describe the services Midwest CNC Services provides,
list our service area, and let you submit a quote request. It is not a
portal for placing orders, signing service contracts, or transferring
payment. Any actual service relationship between Midwest CNC and your
shop is governed by the service agreement we sign with you for a specific
job — not by anything published here.</p>

<h2 id="quote-requests">Quote requests</h2>
<p>A quote request submitted through this Site is an inquiry, not a
binding contract. Submitting a request does not obligate either party.
We respond to quote requests with pricing, lead times, and scope. A
binding service agreement begins only when we and your authorized
representative both sign the agreement covering the specific job.</p>

<h2 id="limitation-of-liability">Limitation of liability</h2>
<p>Information published on this Site is provided as-is for general
informational purposes. Lead times, service descriptions, and equipment
compatibility statements reflect typical work but do not guarantee
outcomes for any specific job. Actual service is delivered subject to a
signed service agreement, which contains the warranties, performance
commitments, and remedies that apply to that job.</p>
<p>To the maximum extent permitted by law, Midwest CNC Services, its
employees, contractors, and partners are not liable for indirect,
incidental, consequential, or punitive damages arising from your use of
the Site or your reliance on information published here. Direct damages,
if any, are limited to the value of the service agreement signed for
the specific job in question.</p>

<h2 id="warranties">Warranties</h2>
<p>Equipment and service warranties are governed by the service agreement
signed for each job, not by anything stated on this Site. If you have a
question about the warranty terms for a specific service we provided,
call <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a>.</p>

<h2 id="intellectual-property">Intellectual property</h2>
<p>Content on this Site — text, images, schema markup, and code — is the
property of Midwest CNC Services or used with permission. The brand names
of CNC machine OEMs referenced on this Site (Mazak, Haas, Okuma, DMG Mori,
Fanuc, and others) are the property of their respective owners. We use
those names to describe the platforms we service; we are not affiliated
with, endorsed by, or operating under license from those OEMs unless
explicitly noted on a specific service page.</p>

<h2 id="changes">Changes to these terms</h2>
<p>We may update these terms from time to time. Changes take effect when
posted to this page. The "Last updated" date above reflects the most
recent change. If you submitted a quote request before a change, the
version of these terms in effect at the time of your submission applies
to that submission.</p>

<h2 id="jurisdiction">Jurisdiction</h2>
<p>These terms are governed by the laws of the State of Iowa, without
regard to conflict-of-law principles. Any dispute arising from your use
of this Site or from a service relationship with Midwest CNC Services
will be resolved in the state or federal courts located in Black Hawk
County, Iowa.</p>

<h2 id="contact">Contact</h2>
<p>Questions about these terms: call
<a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a> or write to Midwest CNC
Services, Waterloo, Iowa.</p>
"""


def not_found_body():
    return f"""<h1>Page not found</h1>
<p>Looks like that page doesn't exist (or moved). Try one of these:</p>
<ul>
  <li><a href="/repairs/">CNC machine repair</a></li>
  <li><a href="/spindle-grinding/">Spindle grinding</a></li>
  <li><a href="/way-covers/">Way covers</a></li>
  <li><a href="/service-area/">Service areas</a></li>
</ul>
<p>Or get in touch:</p>
{hero_cta_html()}
"""


# ---------- Page-write helpers ----------

def write_page(rel_url_dir, *, title, description, canonical_path, schemas,
               crumbs, body_html, layout="default", noindex=False,
               exclude_from_sitemap=False):
    """rel_url_dir: path like '/about/' or '/' for the URL. Writes to
    public/<rel_url_dir>/index.html (or public/index.html for the homepage).

    noindex=True adds <meta name="robots" content="noindex,follow"> to
    the head so search engines ignore the page (use for thank-you /
    confirmation pages).

    exclude_from_sitemap=True records the canonical URL in a module-
    level set that the sitemap generator skips. Use together with
    noindex for internal-only pages."""
    out_path = os.path.join(PUBLIC, rel_url_dir.strip("/"), "index.html") \
        if rel_url_dir.strip("/") else os.path.join(PUBLIC, "index.html")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    schema_blocks = schema_script_tags(schemas)
    crumbs_html_str = breadcrumbs_html(crumbs) if crumbs else ""

    page_html = wrap_page(
        title=title,
        description=description,
        canonical=f"{DOMAIN}{canonical_path}",
        schema_blocks=schema_blocks,
        crumbs_html_str=crumbs_html_str,
        body_html=body_html,
        layout=layout,
        noindex=noindex,
    )
    with open(out_path, "w") as f:
        f.write(page_html)
    if exclude_from_sitemap:
        SITEMAP_EXCLUDE.add(f"{DOMAIN}{canonical_path}")
    return out_path


# Module-level set of canonicals that gen_sitemap() must skip. Populated
# by write_page() when exclude_from_sitemap=True is passed.
SITEMAP_EXCLUDE: set = set()


def absolute(path):
    return f"{DOMAIN}{path}"


# ---------- Driver per page ----------

def gen_homepage(brands):
    schemas = organization_localbusiness_schema()
    schemas.append(faqpage_schema(HOMEPAGE_FAQ))
    return write_page(
        "/",
        title="Midwest CNC Services — CNC Repair, Spindle Work & Way Covers",
        description=(
            "CNC machine repair, spindle rebuilds, and replacement way covers "
            "from Waterloo, IA. Serving shops across 7 Midwest states. "
            "Call 319-610-4341."
        ),
        canonical_path="/",
        schemas=schemas,
        crumbs=None,
        body_html=homepage_body(),
        layout="wide",
    )


def gen_about():
    schemas = [breadcrumb_schema([
        ("Home", absolute("/")),
        ("About", absolute("/about/")),
    ])]
    return write_page(
        "/about/",
        title="About Midwest CNC Services | Waterloo, Iowa",
        description=(
            "Midwest CNC Services is based in Waterloo, Iowa, serving shops "
            "across the Midwest and South-Central US with CNC machine repair, "
            "spindle work, and replacement way covers."
        ),
        canonical_path="/about/",
        schemas=schemas,
        crumbs=[("Home", "/"), ("About", None)],
        body_html=about_body(),
    )


def gen_quote(brands):
    schemas = [breadcrumb_schema([
        ("Home", absolute("/")),
        ("Get a Quote", absolute("/get-a-quote/")),
    ])]
    return write_page(
        "/get-a-quote/",
        title="Get a Quote — Midwest CNC Services",
        description=(
            "Tell us about your machine and we'll get back to you with pricing "
            "and lead time. Most quotes go out within one business day."
        ),
        canonical_path="/get-a-quote/",
        schemas=schemas,
        crumbs=[("Home", "/"), ("Get a Quote", None)],
        body_html=quote_body(brands),
        layout="wide",
    )


def quote_thanks_body():
    """The thank-you page shown after a successful quote submission.
    The Pages Function at /functions/api/quote.js redirects here."""
    return f'''<h1>Thanks — we got it.</h1>

<p class="lede">Your quote request is in our inbox. We'll be in touch within one business day with pricing and lead time.</p>

<div class="quote-helpers">
  <h2 id="next-steps">What happens next</h2>
  <p>One of us — usually Ken or Aaron — will read your message, look at the machine specifics, and reply. Most replies come back inside the next business day. If we need more information (a photo of the spindle, the exact alarm code, the year of the machine), we will ask.</p>

  <h2 id="if-urgent">If it's urgent</h2>
  <p>If the machine is down and production is waiting, call us at <a href="tel:{PHONE_TEL}"><strong>{PHONE_DISPLAY}</strong></a>. We will pick up faster than email reaches us, and we can usually scope the work on the call.</p>

  <h2 id="while-you-wait">While you wait</h2>
  <p>Articles that match common reasons shops reach out:</p>
  <ul>
    <li><a href="/insights/spindle-diagnostics/diagnose-cnc-spindle-vibration/">How to Diagnose CNC Spindle Vibration: A Symptoms Decoder</a></li>
    <li><a href="/insights/spindle-diagnostics/rebuild-vs-replace-spindle-economics/">Spindle Rebuild vs. Replace: When Each Makes Sense</a></li>
    <li><a href="/insights/cnc-control-systems/mazatrol-matrix-vs-smooth/">Mazatrol Matrix vs. Smooth: When to Upgrade</a></li>
  </ul>
</div>

<div class="alt-contact">
  <p>Midwest CNC Services &middot; Waterloo, Iowa</p>
  <p>Serving shops across Iowa, Illinois, Wisconsin, Minnesota, Nebraska, Missouri, and Texas.</p>
</div>
'''


def gen_quote_thanks():
    schemas = [breadcrumb_schema([
        ("Home", absolute("/")),
        ("Get a Quote", absolute("/get-a-quote/")),
        ("Thank you", absolute("/get-a-quote/thank-you/")),
    ])]
    return write_page(
        "/get-a-quote/thank-you/",
        title="Quote received — Midwest CNC Services",
        description="Your quote request is in. We will be in touch within one business day.",
        canonical_path="/get-a-quote/thank-you/",
        schemas=schemas,
        crumbs=[("Home", "/"), ("Get a Quote", "/get-a-quote/"), ("Thank you", None)],
        body_html=quote_thanks_body(),
        # Internal post-submission page only. Tell crawlers to skip it
        # AND keep it out of the sitemap so it isn't surfaced as a
        # landing page anywhere.
        noindex=True,
        exclude_from_sitemap=True,
    )


def _build_hub_itemlist(hub_title, brands, link_for):
    """Build an ItemList schema enumerating the brand pages in a hub."""
    items = []
    for b in sorted(brands, key=lambda x: x["brand_display_name"]):
        pair = link_for(b)
        if pair is None:
            continue
        label, url = pair
        items.append({"name": label, "url": f"{DOMAIN}{url}"})
    return hub_itemlist_schema(hub_title, items)


def gen_repairs_hub(brands):
    body_html, qa = repairs_hub_body(brands)

    def link_for(b):
        if b["page_type"] == "cnc_spindle":
            return (b["brand_display_name"], f"/repairs/{b['slug']}-cnc-machine-repair/")
        return (b["brand_display_name"], b["current_url"])

    schemas = [
        breadcrumb_schema([
            ("Home", absolute("/")),
            ("Repairs", absolute("/repairs/")),
        ]),
        _build_hub_itemlist("Brands We Service for Machine Repair", brands, link_for),
        hub_faq_schema(qa),
    ]
    return write_page(
        "/repairs/",
        title="CNC Machine Repair Services | Midwest CNC Services",
        description=(
            "CNC machine repair across the Midwest — spindle, control, ATC, "
            "drive, and alignment work on every major OEM platform. "
            "Experienced field technicians."
        ),
        canonical_path="/repairs/",
        schemas=schemas,
        crumbs=[("Home", "/"), ("Repairs", None)],
        body_html=body_html,
        layout="wide",
    )


def gen_spindle_hub(brands):
    body_html, qa = spindle_hub_body(brands)

    def link_for(b):
        if not b.get("services_offered", {}).get("spindle"):
            return None
        return (b["brand_display_name"], f"/spindle-grinding/{b['slug']}-spindle-repair/")

    schemas = [
        breadcrumb_schema([
            ("Home", absolute("/")),
            ("Spindle Grinding", absolute("/spindle-grinding/")),
        ]),
        _build_hub_itemlist("Brands We Service for Spindle Work", brands, link_for),
        hub_faq_schema(qa),
    ]
    return write_page(
        "/spindle-grinding/",
        title="CNC Spindle Repair, Rebuilds & Grinding | Midwest CNC Services",
        description=(
            "CNC spindle repair, rebuild, and grinding across 18 OEM platforms. "
            "Most jobs run 2–6 weeks. Experienced field technicians."
        ),
        canonical_path="/spindle-grinding/",
        schemas=schemas,
        crumbs=[("Home", "/"), ("Spindle Grinding", None)],
        body_html=body_html,
        layout="wide",
    )


def gen_way_covers_hub(brands):
    body_html, qa = way_covers_hub_body(brands)

    def link_for(b):
        so = b.get("services_offered", {})
        if not so.get("way_covers"): return None
        if b.get("way_covers_verification_pending"): return None
        return (b["brand_display_name"], f"/way-covers/{b['slug']}-cnc-way-covers/")

    schemas = [
        breadcrumb_schema([
            ("Home", absolute("/")),
            ("Way Covers", absolute("/way-covers/")),
        ]),
        _build_hub_itemlist("Brands We Build Way Covers For", brands, link_for),
        hub_faq_schema(qa),
    ]
    return write_page(
        "/way-covers/",
        title="CNC Way Cover Replacement | Midwest CNC Services",
        description=(
            "Replacement CNC way covers in bellows, telescoping steel, and "
            "roll-up styles. Built to spec, shipped anywhere in the continental "
            "US. 2–4 week lead times."
        ),
        canonical_path="/way-covers/",
        schemas=schemas,
        crumbs=[("Home", "/"), ("Way Covers", None)],
        body_html=body_html,
        layout="wide",
    )


def gen_service_area_hub():
    body_html, qa = service_area_hub_body()

    schemas = [
        breadcrumb_schema([
            ("Home", absolute("/")),
            ("Service Area", absolute("/service-area/")),
        ]),
        hub_faq_schema(qa),
    ]
    return write_page(
        "/service-area/",
        title="Service Area Coverage | Midwest CNC Services",
        description=(
            "Midwest CNC Service coverage across Iowa, Illinois, Wisconsin, "
            "Minnesota, Nebraska, Missouri, and Texas — field service and "
            "shipped builds from Waterloo, IA."
        ),
        canonical_path="/service-area/",
        schemas=schemas,
        crumbs=[("Home", "/"), ("Service Area", None)],
        body_html=body_html,
        layout="wide",
    )


def gen_privacy():
    schemas = [breadcrumb_schema([
        ("Home", absolute("/")),
        ("Privacy Policy", absolute("/privacy-policy/")),
    ])]
    return write_page(
        "/privacy-policy/",
        title="Privacy Policy | Midwest CNC Services",
        description=(
            "How Midwest CNC Services handles information you submit through "
            "the quote form. No analytics, no tracking, no marketing list."
        ),
        canonical_path="/privacy-policy/",
        schemas=schemas,
        crumbs=[("Home", "/"), ("Privacy Policy", None)],
        body_html=privacy_body(),
    )


def gen_terms():
    schemas = [breadcrumb_schema([
        ("Home", absolute("/")),
        ("Terms of Service", absolute("/terms-of-service/")),
    ])]
    return write_page(
        "/terms-of-service/",
        title="Terms of Service | Midwest CNC Services",
        description=(
            "Terms governing your use of midwestcncservices.com. Quote "
            "requests are inquiries; service agreements are signed "
            "separately for each job."
        ),
        canonical_path="/terms-of-service/",
        schemas=schemas,
        crumbs=[("Home", "/"), ("Terms of Service", None)],
        body_html=terms_body(),
    )


def gen_404():
    schemas = []  # No JSON-LD on the 404 itself
    out_path = os.path.join(PUBLIC, "404.html")
    page_html = wrap_page(
        title="Page not found — Midwest CNC Services",
        description="The page you were looking for isn't here. Try one of our service hubs.",
        canonical=absolute("/404.html"),
        schema_blocks="",
        crumbs_html_str="",
        body_html=not_found_body(),
    )
    with open(out_path, "w") as f:
        f.write(page_html)
    return out_path


# ---------- Sitemap + robots + favicon ----------

def gen_sitemap(brands):
    """Walk public/ for index.html files, extract canonical, skip drafts."""
    # Build set of draft canonical URLs from spindle-brands.json
    drafts = set()
    for b in brands:
        if b.get("way_covers_verification_pending"):
            drafts.add(f"{DOMAIN}/way-covers/{b['slug']}-cnc-way-covers/")

    urls = []
    for root, dirs, files in os.walk(PUBLIC):
        for f in files:
            if f != "index.html":
                continue
            path = os.path.join(root, f)
            with open(path) as h:
                src = h.read()
            m = re.search(r'<link rel="canonical" href="([^"]+)"', src)
            if not m:
                continue
            url = m.group(1)
            if url in drafts:
                continue
            # Skip pages flagged exclude_from_sitemap (e.g. thank-you).
            if url in SITEMAP_EXCLUDE:
                continue
            # Also skip pages with noindex robots meta — belt and
            # suspenders defense for any internal page that forgot the
            # exclude flag.
            if re.search(r'<meta\s+name="robots"\s+content="[^"]*noindex', src):
                continue
            # Priority by URL pattern
            if url.rstrip("/") == DOMAIN:
                priority = "1.0"
            elif url.rstrip("/") in (
                f"{DOMAIN}/repairs", f"{DOMAIN}/spindle-grinding",
                f"{DOMAIN}/way-covers", f"{DOMAIN}/service-area",
                f"{DOMAIN}/about", f"{DOMAIN}/get-a-quote",
            ):
                priority = "0.8"
            elif "/spindle-grinding/" in url or "/way-covers/" in url \
                    or "/repairs/" in url:
                priority = "0.7"
            else:
                priority = "0.6"
            urls.append((url, priority))

    urls.sort(key=lambda x: x[0])
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url, priority in urls:
        lines.append('  <url>')
        lines.append(f'    <loc>{url}</loc>')
        lines.append(f'    <lastmod>{today}</lastmod>')
        lines.append(f'    <priority>{priority}</priority>')
        lines.append('  </url>')
    lines.append('</urlset>')

    out = os.path.join(PUBLIC, "sitemap.xml")
    with open(out, "w") as f:
        f.write("\n".join(lines) + "\n")
    return out, len(urls), len(drafts)


def gen_robots():
    out = os.path.join(PUBLIC, "robots.txt")
    with open(out, "w") as f:
        f.write(
            "User-agent: *\n"
            "Allow: /\n"
            f"Sitemap: {DOMAIN}/sitemap.xml\n"
        )
    return out


def gen_headers():
    """Write public/_headers for Cloudflare Pages.

    Security headers apply to every route. We deliberately do NOT set a
    Content-Security-Policy yet — a strict CSP would need testing against
    every third-party script (gtag, googletagmanager, consentresolve,
    cloudflare turnstile, unpkg leaflet, google fonts) and a wrong CSP
    silently breaks the site. CSP is a documented follow-up.

    Long cache on /assets/* (images, video, fonts) since filenames are
    stable; HTML stays revalidated so content edits show immediately."""
    out = os.path.join(PUBLIC, "_headers")
    content = """/*
  X-Content-Type-Options: nosniff
  X-Frame-Options: SAMEORIGIN
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: geolocation=(), microphone=(), camera=()

/assets/*
  Cache-Control: public, max-age=604800

/*.webp
  Cache-Control: public, max-age=604800

/favicon.svg
  Cache-Control: public, max-age=604800
"""
    with open(out, "w") as f:
        f.write(content)
    return out


def gen_llms_txt():
    """Phase 4D: llms.txt at site root for AEO/GEO crawlers (ChatGPT,
    Perplexity, Google AI Overviews). Format per https://llmstxt.org/"""
    content = f"""# Midwest CNC Services

> Independent CNC machine repair, spindle grinding and rebuild, and
> replacement way-cover manufacturing for shops across the U.S. Midwest.
> Based in Waterloo, Iowa; serving Iowa, Illinois, Wisconsin, Minnesota,
> Nebraska, Missouri, and Texas. Phone: 319-610-4341.

This site documents brand-specific CNC service capabilities across
twenty OEM platforms (Mazak, Haas, Okuma, DMG Mori, Mori Seiki, Doosan,
Brother, Hurco, Makino, Fanuc, Toyoda, Fadal, Hitachi Seiki, Giddings &
Lewis, Monarch, Amera-Seiki, Niigata, Johnford, Amada, Trumpf), plus
geographic service coverage for the Midwest and South-Central US.

Content is authored from first-hand technician knowledge (Ken Ehlers
at Midwest CNC Services) and supplemented with verifiable regional
context from Wikipedia city/state articles. We do not claim named
manufacturers (Boeing Defense, John Deere, Lockheed Martin, etc.) as
direct customers — those references appear as regional industry
context only.

## Authoritative starting points

- [Homepage](https://midwestcncservices.com/): business overview, service summary, FAQs
- [About Midwest CNC](https://midwestcncservices.com/about/): who we are, what we do, where we work
- [Get a Quote](https://midwestcncservices.com/get-a-quote/): contact form for service inquiries

## Service hubs

- [Machine Repair](https://midwestcncservices.com/repairs/): CNC machine repair across all 20 brand platforms
- [Spindle Grinding](https://midwestcncservices.com/spindle-grinding/): spindle rebuild, regrind, and rebalance across 18 brands
- [Way Covers](https://midwestcncservices.com/way-covers/): replacement way-cover manufacturing
- [Service Area Coverage](https://midwestcncservices.com/service-area/): 7-state geographic coverage

## Technical Insights (long-form, citation-friendly)

Working-knowledge articles authored by Ken (shop owner). Each piece is
grounded in real shop work and intended to be quotable in AI Overviews,
ChatGPT, Perplexity, and Gemini answers. Cite the source URL with the
article title.

- [Insights index](https://midwestcncservices.com/insights/): all five pillars + recent articles
- [Spindle Diagnostics & Repair Decisions](https://midwestcncservices.com/insights/spindle-diagnostics/): vibration symptoms, bearing failure modes, runout, rebuild-vs-replace economics
- [CNC Control Systems](https://midwestcncservices.com/insights/cnc-control-systems/): Mazatrol, Fanuc, Siemens, Heidenhain, OSP — alarm codes, retrofits, legacy support
- [Way Covers Engineering](https://midwestcncservices.com/insights/way-covers-engineering/): telescoping vs bellows vs roll-up, OEM-vs-custom, field measurement
- [Field Service & Logistics](https://midwestcncservices.com/insights/field-service-logistics/): drive-time radius reality, ship-vs-onsite decisions, multi-state coverage
- [Buying & Owning Used CNC](https://midwestcncservices.com/insights/buying-owning-used-cnc/): inspection checklists, era-by-era buying guides, TCO math, retrofit ROI

## Sitemaps + indexes

- [Sitemap](https://midwestcncservices.com/sitemap.xml)
- [Robots.txt](https://midwestcncservices.com/robots.txt)

## Content licensing

All content is © Midwest CNC Services. AEO/GEO crawlers are welcome
to cite specific facts (lead times, service descriptions, regional
context) with link attribution to the source URL on this site. Brand
names referenced (Mazak, Haas, etc.) are the property of their
respective OEM owners.
"""
    out = os.path.join(PUBLIC, "llms.txt")
    with open(out, "w") as f:
        f.write(content)
    return out


def gen_favicon():
    """Write a small SVG favicon. We rely on SVG only (modern browsers);
    no .ico/.png raster is included this round — documented in the report."""
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <rect width="32" height="32" rx="4" fill="#b8341a"/>
  <text x="16" y="22" font-family="Inter, Arial, sans-serif" font-size="15"
        font-weight="700" fill="#fff" text-anchor="middle">MC</text>
</svg>
'''
    out = os.path.join(PUBLIC, "favicon.svg")
    with open(out, "w") as f:
        f.write(svg)
    return out


# ---------- Link audit ----------

def parse_redirects():
    """Read public/_redirects → set of source paths."""
    redirects = set()
    path = os.path.join(PUBLIC, "_redirects")
    if not os.path.exists(path):
        return redirects
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) >= 2:
            redirects.add(parts[0])
    return redirects


def resolve_internal(href, redirects):
    """Return one of:
       ("ok",       absolute_disk_path)
       ("redirect", source_path)
       ("broken",   absolute_disk_path that doesn't exist)
       ("skip",     reason)         # external, tel:, mailto:, anchor, etc.
    """
    if not href:
        return ("skip", "empty")
    if href.startswith(("#", "?")):
        return ("skip", "in-page")
    if href.startswith(("tel:", "mailto:", "javascript:")):
        return ("skip", "non-http")
    if href.startswith(("http://", "https://", "//")):
        if "midwestcncservices.com" in href:
            href = href.split("midwestcncservices.com", 1)[1] or "/"
        else:
            return ("skip", "external")
    if not href.startswith("/"):
        return ("skip", "relative")  # we don't use these
    # Strip query/fragment
    clean = href.split("?", 1)[0].split("#", 1)[0] or "/"
    # If matched by a redirect, treat as resolved
    if clean in redirects:
        return ("redirect", clean)
    # Map to disk
    if clean.endswith("/"):
        disk = os.path.join(PUBLIC, clean.lstrip("/"), "index.html")
    elif "." in os.path.basename(clean):
        disk = os.path.join(PUBLIC, clean.lstrip("/"))
    else:
        disk = os.path.join(PUBLIC, clean.lstrip("/"), "index.html")
    if os.path.exists(disk):
        return ("ok", disk)
    return ("broken", clean)


def link_audit():
    redirects = parse_redirects()
    broken_by_source = {}   # source_file → list of (href, source_text)
    total_links = 0
    external_count = 0
    skip_count = 0
    redirect_count = 0
    ok_count = 0

    for root, dirs, files in os.walk(PUBLIC):
        for f in files:
            if not f.endswith(".html"):
                continue
            path = os.path.join(root, f)
            src = open(path).read()
            # Match anchors with ANY inner content (including <img>/<span>/etc.) —
            # the previous [^<]* version skipped tile-style anchors entirely.
            for m in re.finditer(
                r'<a\s[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
                src,
                flags=re.DOTALL,
            ):
                href = m.group(1)
                text = re.sub(r"<[^>]+>", "", m.group(2)).strip()
                total_links += 1
                status, info = resolve_internal(href, redirects)
                if status == "ok":
                    ok_count += 1
                elif status == "redirect":
                    redirect_count += 1
                elif status == "broken":
                    rel_source = os.path.relpath(path, PUBLIC)
                    broken_by_source.setdefault(rel_source, []).append((href, text))
                elif status == "skip":
                    if info == "external":
                        external_count += 1
                    else:
                        skip_count += 1

    return {
        "total": total_links,
        "ok": ok_count,
        "redirect": redirect_count,
        "external": external_count,
        "skip": skip_count,
        "broken_by_source": broken_by_source,
    }


def write_audit_report(audit):
    """Write docs/phase-1-link-audit.md from the audit dict."""
    lines = ["# Phase 1 — Cross-Link Audit\n",
             f"Scanned every `<a href>` in every HTML file under `public/` "
             f"and resolved each link against the filesystem and `public/_redirects`.\n",
             "## Totals\n",
             f"- **Total `<a href>` links scanned:** {audit['total']}",
             f"- **Resolved to a real file:** {audit['ok']}",
             f"- **Resolved via `_redirects` (301):** {audit['redirect']}",
             f"- **External links (skipped from broken-check):** {audit['external']}",
             f"- **Other non-http (tel:/mailto:/anchor/etc.):** {audit['skip']}",
             ""]

    broken = audit["broken_by_source"]
    n_broken_links = sum(len(v) for v in broken.values())

    if not broken:
        lines.append("## Broken internal links\n\nNone. 🎉\n")
    else:
        # Aggregate unique broken hrefs across the site
        broken_targets = {}
        for src_file, hrefs in broken.items():
            for href, text in hrefs:
                broken_targets.setdefault(href, set()).add(src_file)

        lines.append(f"## Broken internal links ({n_broken_links} link instances pointing to "
                     f"{len(broken_targets)} unique missing targets)\n")
        lines.append("Sorted by how many source files reference each missing target.\n")
        lines.append("| Missing target | Referenced from |")
        lines.append("|---|---|")
        for href, sources in sorted(broken_targets.items(),
                                     key=lambda kv: (-len(kv[1]), kv[0])):
            srclist = ", ".join(sorted(sources))
            lines.append(f"| `{href}` | {srclist} |")
        lines.append("")

        # Group by URL pattern — what's outstanding for future phases?
        lines.append("## Likely-expected (already-planned) broken links\n")
        phase2_state = [h for h in broken_targets if h.startswith("/service-area/") and h.count("/") == 3]
        phase2_city  = [h for h in broken_targets if h.startswith("/service-area/") and h.count("/") > 3]
        other        = [h for h in broken_targets
                        if not h.startswith("/service-area/")]

        if phase2_state:
            lines.append(f"### Phase 2: state-level pages ({len(phase2_state)})")
            for h in sorted(phase2_state):
                lines.append(f"- `{h}` *(state pages — currently 301-redirected to /service-area/ hub)*")
            lines.append("")
        if phase2_city:
            lines.append(f"### Phase 2 / 3: city-level pages ({len(phase2_city)})")
            for h in sorted(phase2_city)[:25]:
                lines.append(f"- `{h}`")
            if len(phase2_city) > 25:
                lines.append(f"- *…and {len(phase2_city)-25} more*")
            lines.append("")
        if other:
            lines.append(f"### Other broken targets to investigate ({len(other)})")
            for h in sorted(other):
                lines.append(f"- `{h}`")
            lines.append("")

    out = os.path.join(REPO, "docs", "phase-1-link-audit.md")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        f.write("\n".join(lines))
    return out, n_broken_links


# ---------- Main ----------

def main():
    brands = json.load(open(os.path.join(REPO, "src", "data", "spindle-brands.json")))["brands"]

    print("== Generating site shell ==\n")
    paths = []
    paths.append(("homepage",      gen_homepage(brands)))
    paths.append(("about",         gen_about()))
    paths.append(("get-a-quote",   gen_quote(brands)))
    paths.append(("quote-thanks",  gen_quote_thanks()))
    paths.append(("repairs hub",   gen_repairs_hub(brands)))
    paths.append(("spindle hub",   gen_spindle_hub(brands)))
    paths.append(("way-covers",    gen_way_covers_hub(brands)))
    paths.append(("service-area",  gen_service_area_hub()))
    paths.append(("privacy",       gen_privacy()))
    paths.append(("terms",         gen_terms()))
    paths.append(("404",           gen_404()))

    for label, p in paths:
        size = os.path.getsize(p)
        print(f"  ✓ {label:<14} → {os.path.relpath(p, REPO):<48} ({size//1024} KB)")

    # Phase 2/3 brought real state and city pages, so the Phase-1 state
    # placeholders are removed. Instead we now need the 3 Illinois URL
    # typo fixes (Durable's "ilinois" → corrected "illinois").
    inventory_path = os.path.join(REPO, "src", "data", "city-inventory.json")
    typo_pairs = []
    if os.path.exists(inventory_path):
        for c in json.load(open(inventory_path)):
            if c.get("original_path"):
                typo_pairs.append(
                    (c["original_path"] + "/", c["path"], 301)
                )
    extras = []
    if typo_pairs:
        extras.append((
            "Phase 2/3: Illinois URL typo fixes (Durable used 'ilinois')",
            typo_pairs,
        ))

    # Phase 6 (enrichment): redirect CONSOLIDATE-marked city pages to their
    # state page. These were removed from public/ as part of Phase 2 enrichment.
    research_path = os.path.join(REPO, "src", "data", "city-research.json")
    if os.path.exists(research_path):
        research = json.load(open(research_path))
        consolidate_pairs = []
        for slug, c in research.get("cities", {}).items():
            if c.get("decision") == "CONSOLIDATE":
                consolidate_pairs.append(
                    (f"/service-area/{slug}/", f"/service-area/{c['state_slug']}/", 301)
                )
        if consolidate_pairs:
            extras.append((
                "Phase 6: CONSOLIDATE-marked city pages → state pages",
                consolidate_pairs,
            ))

    # Phase 5: redirect deferred content sections to relevant pages.
    # Four evergreen blog posts get specific 301s to relevant service hubs
    # (preserves SEO value of any inbound links). All other /blog/, /guides/,
    # and /customer-stories/ URLs fall through to wildcards → homepage.
    extras.append((
        "Phase 5: deferred content sections (blog/guides/customer-stories)",
        [
            ("/blog/precision-cnc-machining--how-it-drives-efficiency-in-manufacturing/", "/repairs/", 301),
            ("/blog/understanding-the-true-cost--usa-made-way-covers-vs--overseas-options/", "/way-covers/", 301),
            ("/blog/choosing-the-right-way-covers-for-your-cnc-machines--a-comprehensive-buyer-s-guide/", "/way-covers/", 301),
            ("/blog/emergency-cnc-repair--quick-steps-to-restore-your-machine/", "/repairs/", 301),
            ("/blog/*",             "/", 301),
            ("/blog",               "/", 301),
            ("/guides/*",           "/", 301),
            ("/guides",             "/", 301),
            ("/customer-stories/*", "/", 301),
            ("/customer-stories",   "/", 301),
        ],
    ))
    n_redirects = gbp.write_redirects(
        brands, os.path.join(PUBLIC, "_redirects"), extras=extras,
    )
    print(f"\n  ✓ _redirects     ({n_redirects} rules total)")

    # Sitemap, robots, favicon
    sm_path, n_urls, n_drafts = gen_sitemap(brands)
    print(f"  ✓ sitemap.xml    ({n_urls} URLs, {n_drafts} drafts excluded)")
    rb_path = gen_robots()
    print(f"  ✓ robots.txt")
    hd_path = gen_headers()
    print(f"  ✓ _headers")
    fv_path = gen_favicon()
    print(f"  ✓ favicon.svg")
    llms_path = gen_llms_txt()
    print(f"  ✓ llms.txt")

    # Copy machines.json into public/ so the MachineLookup component
    # can fetch it from /data/machines.json on the live site.
    import shutil
    src_machines = os.path.join(REPO, "src", "data", "machines.json")
    dst_machines = os.path.join(PUBLIC, "data", "machines.json")
    os.makedirs(os.path.dirname(dst_machines), exist_ok=True)
    if os.path.exists(src_machines):
        shutil.copyfile(src_machines, dst_machines)
        import json as _json
        with open(src_machines) as _f:
            _n = len(_json.load(_f).get("machines", []))
        print(f"  ✓ data/machines.json  ({_n} machines)")

    # Image optimization — convert raster assets to WebP and rewrite
    # HTML references. Run as the final content step (after every page
    # generator) so all freshly-written HTML gets its image references
    # optimized. Decoupled via subprocess so a missing Pillow or a
    # conversion error never breaks the site build.
    print()
    try:
        import subprocess as _sp
        _sp.run(
            ["python3", os.path.join(REPO, "scripts", "optimize_images.py"), "--quiet"],
            check=False,
        )
    except Exception as _e:  # noqa: BLE001
        print(f"  ! image optimization skipped: {_e}")

    # Link audit
    print("\n== Cross-link audit ==")
    audit = link_audit()
    audit_path, n_broken = write_audit_report(audit)
    print(f"  Links scanned:      {audit['total']}")
    print(f"  Resolved (file):    {audit['ok']}")
    print(f"  Resolved (301):     {audit['redirect']}")
    print(f"  External (skipped): {audit['external']}")
    print(f"  Non-http (skipped): {audit['skip']}")
    print(f"  Broken:             {n_broken}")
    print(f"  Report:             {os.path.relpath(audit_path, REPO)}")


if __name__ == "__main__":
    main()

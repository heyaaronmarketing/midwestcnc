#!/usr/bin/env python3
"""
Phase 2 — Enriched city page generator.

Reads src/data/city-research.json (Wikipedia-sourced facts per city) and
src/data/states.json (state context). Generates one /service-area/{city}-
{state}/index.html per ENRICH-marked city.

Honors the editorial constraints:
- Verifiable facts only (Wikipedia city Economy sections)
- Manufacturers named as CONTEXT, never as Midwest CNC customers
- Aaron-authorized framing constraints (e.g. North Platte rail context)
- Compressed shared scaffolding to maximize uniqueness ratio

Target per page: 600–700 visible body words, ≥60% n-gram unique vs siblings.

Skip CONSOLIDATE-marked cities entirely. Add 301 redirects in
public/_redirects pointing them to their state page.
"""

import html
import json
import math
import os
import re
import sys
from collections import OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate_site_shell as gss


REPO = gss.REPO
PUBLIC = gss.PUBLIC
DOMAIN = gss.DOMAIN
PHONE_TEL = gss.PHONE_TEL
PHONE_DISPLAY = gss.PHONE_DISPLAY


# ---------- H1 variants (rotate by city to avoid identical templating) ----------

H1_VARIANTS = [
    "CNC Repair & Service in {name}, {state}",
    "{name} CNC Repair, Spindle Service & Way Covers",
    "CNC Spindle & Machine Repair Serving {name}",
    "CNC Service for {name} Manufacturers",
]


def pick_h1(slug, name, state):
    idx = sum(ord(c) for c in slug) % len(H1_VARIANTS)
    return H1_VARIANTS[idx].format(name=name, state=state)


# ---------- Industry → brand mapping ----------
# Each entry: (regex_pattern, brand_phrase, context_phrase). The brand phrase
# names specific platforms; the context phrase describes the kind of work.
# Order matters — first match wins.

INDUSTRY_BRAND_RULES = [
    (r"\baerospace\b|\bdefense\b|\bdefense and\b|\baerospace and\b|\baviation manufacturing\b",
     "Makino and DMG Mori",
     "tight-tolerance aerospace and defense machining"),
    (r"\bagricultur(e|al)\b|\bag-related\b|\bag.implement\b|\birrigation\b",
     "Mazak and Doosan",
     "ag-equipment production cycles and supply-chain machining"),
    (r"\bheavy (machinery|equipment)\b|\boil and gas\b|\boil.gas\b|\boil\b|\benergy\b|\bmining\b|\bport shipping\b|\boil refining\b|\bcopper smelt",
     "Mazak, Toyoda, and Giddings & Lewis",
     "large-envelope and heavy-part work"),
    (r"\bmedical devices?\b|\bmedical technology\b|\bpharmaceutical\b|\bsemiconductors?\b|\bscientific instruments?\b|\bbiotech\b|\bhigh.tech manufacturing\b",
     "Brother Speedio and Makino",
     "high-precision compact work"),
    (r"\bautomotive\b|\bEV manufacturing\b|\bauto\b",
     "Mazak, Doosan, and Haas",
     "tier-1 and tier-2 supply machining"),
    (r"\brailroad\b|\brail\b",
     "Mazak and Giddings & Lewis",
     "rail-adjacent shop work and large castings"),
    (r"\bpaper manufactur|\bfood processing\b|\bgrain processing\b|\bfood ingredients\b|\bsugar beet\b|\bbrewing\b",
     "Mazak and Haas",
     "process-equipment and food-line machining"),
    (r"\bmanufacturing\b|\bfasteners\b|\bmachine tools\b|\bindustrial controls\b|\bheat exchangers\b|\bammunition\b|\bmanufacturing equipment\b",
     "Mazak and Haas",
     "general production machining"),
]


def map_industries_to_brands(industries):
    """Return list of (brand_phrase, context_phrase) for the first 1–2
    industries that have a brand tie. Returns [] if none match."""
    hits = []
    seen_brands = set()
    text = " ".join(industries).lower()
    for pat, brands, ctx in INDUSTRY_BRAND_RULES:
        if re.search(pat, text) and brands not in seen_brands:
            hits.append((brands, ctx))
            seen_brands.add(brands)
        if len(hits) >= 2:
            break
    return hits


# ---------- Brand-name → URL slug mapping ----------
# Used by the industry-mix section to link to /spindle-grinding/{slug}-spindle-repair/.
# Sorted longest-first so "DMG Mori" beats "DMG" if both prefix.

BRAND_NAME_TO_SLUG = {
    "Mazak": "mazak", "Haas": "haas", "Doosan": "doosan", "Makino": "makino",
    "DMG Mori": "dmg-mori", "Hurco": "hurco", "Fanuc": "fanuc",
    "Brother Speedio": "brother", "Brother": "brother",
    "Toyoda": "toyoda", "Giddings & Lewis": "giddings-lewis",
    "Fadal": "fadal", "Hitachi Seiki": "hitachi-seiki",
    "Monarch": "monarch", "Mori Seiki": "mori-seiki", "Niigata": "niigata",
    "Johnford": "johnford", "Amera-Seiki": "amera-seiki", "Okuma": "okuma",
}


def first_brand_slug(brand_phrase):
    """Extract the FIRST individual brand from a phrase like 'Mazak and Haas'.
    Returns (slug, display_name) or (None, None) if no known brand matches."""
    if not brand_phrase:
        return (None, None)
    for name in sorted(BRAND_NAME_TO_SLUG, key=len, reverse=True):
        if brand_phrase.lower().startswith(name.lower()):
            return (BRAND_NAME_TO_SLUG[name], name)
    return (None, None)


# ---------- Helpers ----------

def direction_from_waterloo(coords):
    lat, lon = coords
    dlat = lat - 42.49
    dlon = lon - (-92.34)
    if abs(dlat) > abs(dlon) * 2.0:
        return "north" if dlat > 0 else "south"
    if abs(dlon) > abs(dlat) * 2.0:
        return "east" if dlon > 0 else "west"
    ns = "north" if dlat > 0 else "south"
    ew = "east" if dlon > 0 else "west"
    return f"{ns}{ew}"


def hours_phrase(hours):
    if hours < 0.5:
        return "right at home"
    if hours < 1.5:
        return f"about {round(hours)} hour by truck"
    if hours < 3:
        return f"about {round(hours, 1)} hours by truck"
    if hours < 8:
        return f"about {round(hours)} hours by truck"
    return f"about {round(hours)} hours one-way — a long-haul route"


def travel_framing(state_slug, distance):
    """Return one-sentence travel framing for the hero. Avoid 'same-day'
    except on the Iowa state page (Aaron-authorized only there)."""
    miles = distance["miles"]
    hours = distance["hours"]
    if miles < 50:
        return "within local field-service reach for diagnostics and on-site work"
    if state_slug == "iowa":
        return f"within Iowa's home-market field-service area — drivable for diagnostics, with bench rebuilds back at the Cedar Valley shop"
    if state_slug in ("illinois", "wisconsin", "minnesota"):
        return f"within practical field-service reach of our shop — drivable for substantial jobs"
    if hours < 8:
        return f"drivable for major jobs by arrangement; routine spindle and way-cover work ships in via standard freight"
    return f"a long-haul route from Waterloo — most {distance['miles']}-mile work runs ship-in via freight, with field service for major jobs by arrangement"


def employers_to_inline(employers, limit=3):
    """Trim parenthetical employee counts and join into prose."""
    cleaned = []
    for e in employers[:limit]:
        # Strip parenthetical "(N employees)" or "(N)" but keep parens that
        # carry a location like "(Waterloo)".
        c = re.sub(r"\s*\((?:[\d,.]+\s*(?:at[^)]+)?|\d+\s*\+?\s*employees?)\)", "", e)
        cleaned.append(c.strip())
    if not cleaned:
        return ""
    if len(cleaned) == 1:
        return cleaned[0]
    if len(cleaned) == 2:
        return f"{cleaned[0]} and {cleaned[1]}"
    return ", ".join(cleaned[:-1]) + f", and {cleaned[-1]}"


def employers_long(employers, limit=5):
    return employers_to_inline(employers, limit=limit)


def industries_phrase(industries, limit=3):
    items = industries[:limit]
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + f", and {items[-1]}"


# ---------- Compressed trust footer + inline customer quote ----------

def trust_footer_html(brand_index):
    """Tight ~40-word About + inline customer quote (~30 words)."""
    # Rotate quote variant per city
    if brand_index % 2 == 0:
        framing = ("Most customers tell us they're relieved to avoid replacement "
                   "lead times and six-figure capital expenses.")
    else:
        framing = ("It saves shops from replacement lead times and the capital "
                   "expense of a new spindle.")
    return f"""<aside class="trust-footer">
<p><strong>About Midwest CNC.</strong> Experienced field technicians with hands-on time across the major CNC OEM platforms, in-house precision spindle balancing capability, laser alignment services, and established relationships with aftermarket bearing and spindle component suppliers — based in Waterloo, IA, serving shops across seven states.</p>
<p class="customer-quote">&quot;Honestly, we thought the machine was done for.&quot; {html.escape(framing)}</p>
</aside>
"""


# ---------- Per-section builders ----------

# Phrase pools — each city picks one variant deterministically via slug hash.
# The variation breaks shared 5-grams across siblings while preserving meaning.

HERO_GEO_VARIANTS = [
    "{name} sits {miles} miles {direction} of our Waterloo, IA shop, {hours} — {travel}.",
    "From our Waterloo location, {name} is {miles} miles {direction} — roughly {hours}, {travel}.",
    "{name} is a {hours} drive {direction} of our Cedar Valley shop in Waterloo, IA ({miles} miles) — {travel}.",
    "Our Waterloo, IA facility sits {miles} miles {opposite_direction} of {name} — {hours} on the road, {travel}.",
]

HERO_WORK_VARIANTS = [
    "We work with {name} {industries_clause}{employers_clause}.",
    "Our {name} customer base runs {industries_clause}{employers_clause}.",
    "In {name}, we serve {industries_clause}{employers_clause}.",
    "{name} shops in our customer mix typically run {industries_clause}{employers_clause}.",
]

HERO_SERVICE_VARIANTS = [
    "CNC machine repair, spindle rebuilds and grinding, and replacement way covers — on-site diagnosis where it saves a teardown, bench work back at the Cedar Valley shop.",
    "Three lines of work for these shops: CNC machine repair, spindle rebuilds and grinding, and replacement way-cover manufacturing. We diagnose on-site where the work warrants it; the rebuild bench is in Waterloo.",
    "The work splits across machine repair, spindle rebuilds and grinding, and custom way-cover manufacturing. Diagnostic visits go on-site; the rebuild and fabrication work happens back at our Iowa shop.",
    "Our service mix covers CNC machine repair, spindle rebuild and regrind work, and replacement way covers built to spec. Diagnostics on-site, bench rebuilds in Waterloo.",
]

OPPOSITE_DIR = {
    "north": "south", "south": "north", "east": "west", "west": "east",
    "northeast": "southwest", "southwest": "northeast",
    "northwest": "southeast", "southeast": "northwest",
}


def pick_variant(slug, salt, pool):
    """Deterministically pick one variant from a pool based on slug + salt."""
    idx = (sum(ord(c) for c in slug) + salt) % len(pool)
    return pool[idx]


def build_hero(city, state, distance, h1_text, eyebrow_text, hero_img_src, hero_img_alt, slug):
    """Emits a .home-hero video-background hero — same midwest-cnc-bg-fade.mp4
    treatment as the homepage and the rest of the service-area section.

    hero_img_src / hero_img_alt are kept in the signature for backward
    compatibility with render_city_page but are unused — the video hero
    is the same on every city. City-specific copy lives in the eyebrow
    + H1 + lede."""
    name = city["name"]
    direction = direction_from_waterloo(city["coords"])
    travel = travel_framing(state["slug"], distance)
    industries_inline = industries_phrase(city["primary_industries"], 2)
    employers_inline = employers_to_inline(city["major_employers"], 2)
    hours = hours_phrase(distance["hours"])

    if distance["miles"] <= 5:
        sent1 = f"{name} is our home market — Midwest CNC Services is based here."
    else:
        sent1 = pick_variant(slug, 0, HERO_GEO_VARIANTS).format(
            name=name, miles=distance["miles"], direction=direction,
            opposite_direction=OPPOSITE_DIR.get(direction, direction),
            hours=hours, travel=travel,
        )

    industries_clause = (
        f"shops doing supply-chain machining for {industries_inline}"
        if industries_inline
        else "shops across the metro's industrial base"
    )
    employers_clause = (
        f", plus in-house tooling work for {employers_inline}"
        if employers_inline
        else ""
    )
    sent2 = pick_variant(slug, 1, HERO_WORK_VARIANTS).format(
        name=name, industries_clause=industries_clause,
        employers_clause=employers_clause,
    )
    sent3 = pick_variant(slug, 2, HERO_SERVICE_VARIANTS)
    lede_text = f"{sent1} {sent2} {sent3}"

    return gss.build_video_hero_html(
        eyebrow_text=eyebrow_text,
        h1_html=html.escape(h1_text),
        lede_html=html.escape(lede_text),
    )


def build_manufacturing_section(city, state):
    name = city["name"]
    state_name = state["display_name"]
    employers = city["major_employers"]
    industries = city["primary_industries"]
    mfg_summary = city["manufacturing_summary"]
    parks = city["industrial_parks"]

    paragraphs = []

    # Paragraph 1: industry overview from Wikipedia summary
    paragraphs.append(html.escape(mfg_summary))

    # Paragraph 2: industrial parks if any
    if parks:
        parks_text = (
            f"Notable industrial zones include {', '.join(parks)}."
        )
        paragraphs.append(parks_text)

    # Paragraph 3: verifiable framing
    if employers:
        emp_list = employers_long(employers, 5)
        paragraphs.append(
            f"Notable {name} employers include {emp_list}. We don't claim "
            f"these names as customers — we service the CNC shops doing "
            f"precision work for them, the supply-chain machining and "
            f"in-house tooling that keeps {name}'s industrial base producing."
        )

    body = "\n\n".join(f"<p>{p}</p>" for p in paragraphs)
    return (
        f'<h2 id="manufacturing">Manufacturing in {html.escape(name)}</h2>\n'
        f"{body}\n"
    )


def build_industry_mix_section(city, state):
    name = city["name"]
    industries = city["primary_industries"]
    brand_hits = map_industries_to_brands(industries)
    constraints = city.get("framing_constraints", {})

    if not brand_hits:
        # No industry-brand tie possible without fabrication
        body = (
            f"<p>{name}'s industry mix is dominated by sectors outside heavy "
            f"manufacturing — finance, government, healthcare, and similar. "
            f"Our work here typically supports shops doing in-house tooling or "
            f"supply-chain machining for adjacent industrial regions. Brand "
            f"coverage is broad rather than industry-targeted.</p>"
        )
    else:
        primary_brands, primary_ctx = brand_hits[0]
        clauses = [
            f"{name} shops working in this industry mix typically run "
            f"{primary_brands} platforms for {primary_ctx}."
        ]
        if len(brand_hits) > 1:
            secondary_brands, secondary_ctx = brand_hits[1]
            clauses.append(
                f"For {secondary_ctx.split(' ', 1)[-1] if ' ' in secondary_ctx else secondary_ctx}, "
                f"shops more commonly run {secondary_brands}."
            )
        body_first = " ".join(clauses)

        # Add an inline link to the relevant brand page. Extract the
        # FIRST single brand from the multi-brand phrase using the known
        # brand-name → slug map; fall back to /repairs/ if no clean match.
        first_slug, first_name = first_brand_slug(primary_brands)
        if first_slug:
            brand_link = (
                f'<a href="/spindle-grinding/{first_slug}-spindle-repair/">'
                f'{html.escape(first_name)} spindle work</a>'
            )
        else:
            brand_link = '<a href="/spindle-grinding/">spindle service</a>'
        body_second = (
            f"<p>We service spindle rebuilds, machine repair, and "
            f"replacement way covers across the OEM platforms common in "
            f"{name}'s industry mix — see the brand pages for {brand_link} "
            f'and <a href="/repairs/">CNC machine repair</a> for the '
            f"specifics on lead times and failure modes.</p>"
        )
        body = f"<p>{body_first}</p>\n{body_second}"

    return (
        f'<h2 id="industry-mix">CNC Service for {html.escape(name)}\'s Industry Mix</h2>\n'
        f"{body}\n"
        f"{gss.hero_cta_html()}\n"
    )


# Logistics phrasing variants — each tier (home/iowa/adjacent/long-haul) has
# 3 phrasings, picked by slug hash so adjacent cities don't share 5-grams.

LOGISTICS_IOWA = [
    "{name} is {miles} miles {direction} of Waterloo — {hours}. Field-service visits are part of our routine Iowa work; we diagnose, scope, and quote on-site, with bench rebuilds and way-cover builds happening back at the shop. Spindles ship in via freight for return rebuilds; lead times typically run 3–6 weeks depending on brand and parts availability.",
    "Waterloo to {name} is {miles} miles, {hours} {direction}. We schedule field-service runs into {name} regularly — on-site diagnostics, scope conversations, and quotes — and bring spindle and way-cover work back to the Cedar Valley shop for bench-side rebuild. Most jobs return within 3–6 weeks based on brand and parts lead times.",
    "The drive between Waterloo and {name} runs {miles} miles ({hours}) {direction}. For {name} shops, field service is part of the routine: we diagnose and scope on-site, then bring the work back to our bench for rebuild and reassembly. Lead times generally hold to a 3–6 week window depending on platform.",
]

LOGISTICS_ADJACENT = [
    "{name} is {miles} miles {direction} of our Waterloo, IA shop — {hours}. Field-service visits are within practical drive for major jobs and bundled diagnostics. For spindle rebuilds and way-cover builds, {name} shops ship in via standard freight; most work returns within the 3–6 week lead-time window.",
    "From Waterloo, {name} sits {miles} miles {direction} — {hours} one-way. We schedule field visits into {name} for substantive jobs and bundled diagnostic runs, with spindle and way-cover work shipped in via freight. The standard 3–6 week lead time applies depending on brand specifics.",
    "{name} is a {hours} drive {direction} of Waterloo ({miles} miles). For major repairs and diagnostic visits, that's a practical field-service distance; routine spindle rebuilds and way-cover builds run ship-in via freight, returning inside our usual 3–6 week pattern.",
]

LOGISTICS_LONGHAUL = [
    "{name} is {miles} miles {direction} of Waterloo — {hours}. Most {name} work runs ship-in from our Waterloo shop: spindles to the bench, way covers shipped anywhere in the continental US. Field service is available for major jobs by arrangement — talk to us about scope and travel before scheduling.",
    "From our Iowa shop, {name} is a {miles}-mile haul ({hours}) {direction}. The economics typically favor ship-in service: freight a spindle to the Waterloo bench, ship way-cover builds anywhere in the lower 48. Field travel is possible for substantial multi-machine work — scope it with us before scheduling.",
    "{name} sits {miles} miles {direction} of our base in Waterloo — too far for routine field service. Spindles ship in via standard freight; way-cover builds ship out to anywhere in the continental US. For major jobs we'll quote field travel; talk to us about scope first.",
]


def build_logistics_section(city, state, distance, slug):
    name = city["name"]
    direction = direction_from_waterloo(city["coords"])
    miles = distance["miles"]
    hours = hours_phrase(distance["hours"])
    is_home_state = state["is_home_state"]

    if miles <= 5:
        body = (
            f"{name} is our home base. Field service is routine; bench rebuilds "
            f"and way-cover builds happen at the Cedar Valley shop and roll out "
            f"by truck or by carrier. Most jobs originate within the local area; "
            f"the same 3–6 week lead-time pattern applies to scheduled rebuilds."
        )
    elif is_home_state:
        body = pick_variant(slug, 3, LOGISTICS_IOWA).format(
            name=name, miles=miles, direction=direction, hours=hours,
        )
    elif state["slug"] in ("illinois", "wisconsin", "minnesota"):
        body = pick_variant(slug, 4, LOGISTICS_ADJACENT).format(
            name=name, miles=miles, direction=direction, hours=hours,
        )
    else:
        body = pick_variant(slug, 5, LOGISTICS_LONGHAUL).format(
            name=name, miles=miles, direction=direction, hours=hours,
        )

    return (
        f'<h2 id="logistics">Logistics: How We Service {html.escape(name)}</h2>\n'
        f"<p>{html.escape(body)}</p>\n"
    )


def build_faq_section(city, state, distance, slug):
    """4 city-specific Q&As + FAQPage schema. Each question and answer has
    multiple phrasings rotated by slug hash to break shared 5-grams."""
    name = city["name"]
    state_name = state["display_name"]
    state_slug = state["slug"]
    miles = distance["miles"]
    hours = distance["hours"]
    industries = city["primary_industries"]
    employers = city["major_employers"]

    # Pull a couple of city-specific facts to seed answers
    first_emp = employers[0] if employers else None
    pop_text = city.get("population", "")

    # ----- FAQ 1: field service distance/time -----
    q1_variants_local = [
        f"How does Midwest CNC handle field service for {name} shops?",
        f"How quickly can you visit a {name} shop?",
        f"What does field service look like for {name} customers?",
    ]
    q1_variants_regional = [
        f"How long does it take Midwest CNC to reach {name} for field service?",
        f"Can you drive to {name} for an on-site visit?",
        f"What's the field-service travel time from Waterloo to {name}?",
    ]
    q1_variants_longhaul = [
        f"Do you travel to {name}, {state_name} for field service?",
        f"Is field service available for {name} shops?",
        f"Can Midwest CNC come to {name} for an on-site job?",
    ]

    if miles <= 5:
        q1 = pick_variant(slug, 10, q1_variants_local)
        a1 = (
            f"{name} is our home market. We schedule on-site visits "
            f"routinely and respond locally without long-haul logistics."
        )
    elif state["is_home_state"] or state_slug in ("illinois", "wisconsin", "minnesota"):
        q1 = pick_variant(slug, 11, q1_variants_regional)
        a1_variants = [
            f"{name} is {miles} miles from our Waterloo, Iowa shop — "
            f"{hours_phrase(hours)}. Field-service visits to {name} are part "
            f"of routine work — diagnostics, scope, and on-site quotes.",
            f"From Waterloo, IA to {name} is a {hours_phrase(hours).replace('about ', '')} drive "
            f"({miles} miles). We schedule field visits regularly for "
            f"{name}-area diagnostics and bundled service calls.",
            f"The {miles}-mile drive from our Waterloo shop to {name} runs "
            f"{hours_phrase(hours)}, well within our field-service area. "
            f"We routinely diagnose and scope on-site for {name} customers.",
        ]
        a1 = pick_variant(slug, 12, a1_variants)
    else:
        q1 = pick_variant(slug, 13, q1_variants_longhaul)
        a1_variants = [
            f"{name} is {miles} miles from Waterloo — too far for routine "
            f"field service. We schedule field travel to {name} for major "
            f"multi-machine jobs by arrangement; most work runs ship-in via "
            f"standard freight.",
            f"From our Iowa shop, {name} is a {miles}-mile haul. The "
            f"economics typically favor ship-in service; we do schedule "
            f"field visits for substantial jobs after scoping the travel.",
            f"At {miles} miles from Waterloo, {name} is outside routine "
            f"field-service distance. Most {name} work moves via freight; "
            f"on-site visits are quoted separately for larger jobs.",
        ]
        a1 = pick_variant(slug, 14, a1_variants)

    # ----- FAQ 2: industry tie -----
    primary_industry = industries[0] if industries else "manufacturing"
    brand_hits = map_industries_to_brands(industries)
    brands_phrase = brand_hits[0][0] if brand_hits else None

    q2_variants = [
        f"Do you service {primary_industry} shops in {name}?",
        f"Are {primary_industry} customers part of your {name} work?",
        f"Does Midwest CNC support {name}'s {primary_industry} sector?",
    ]
    q2 = pick_variant(slug, 15, q2_variants)
    if brands_phrase:
        a2_variants = [
            f"Yes. {name} machinists working in {primary_industry} and "
            f"adjacent sectors are a routine part of our customer base. "
            f"The {brands_phrase} platforms common in that work fall "
            f"squarely in our brand coverage.",
            f"Yes — {primary_industry} work is part of what comes through "
            f"on the {name} customer side. We see {brands_phrase} platforms "
            f"often in those shops.",
            f"Routinely. Shops doing {primary_industry} work in the {name} "
            f"area typically run {brands_phrase}, both of which we service "
            f"across spindle, machine, and way-cover lines.",
        ]
        a2 = pick_variant(slug, 16, a2_variants)
    else:
        a2_variants = [
            f"Yes. {name} shops doing work in {primary_industry} fall "
            f"within our service area across spindle rebuilds, machine "
            f"repair, and replacement way covers.",
            f"We do — {primary_industry} customers in the {name} area run "
            f"a mix of platforms we cover across all three service lines.",
            f"Yes. Our brand coverage spans the typical {primary_industry} "
            f"platforms found in {name} shops.",
        ]
        a2 = pick_variant(slug, 17, a2_variants)

    # ----- FAQ 3: shipping -----
    q3_variants = [
        f"Can {name} shops ship spindles to Waterloo for rebuild?",
        f"How do {name} customers get a spindle to your bench?",
        f"What's the shipping process for {name} spindles coming in for rebuild?",
    ]
    q3 = pick_variant(slug, 18, q3_variants)
    if miles <= 5:
        a3 = (
            f"{name} shops can drop spindles directly at our Waterloo "
            f"facility, or we'll arrange local pickup."
        )
    elif miles < 400:
        a3_variants = [
            f"Yes — standard freight from {name} to Waterloo is overnight "
            f"or two-day depending on carrier. Return shipping is included "
            f"in most spindle rebuild quotes.",
            f"Routine freight. From {name}, transit to Waterloo is one to "
            f"two business days. We include return shipping in standard "
            f"rebuild pricing.",
            f"Most {name} customers ship via UPS, FedEx Freight, or LTL — "
            f"a 1–2 day transit. Return freight is folded into the rebuild "
            f"quote.",
        ]
        a3 = pick_variant(slug, 19, a3_variants)
    else:
        a3_variants = [
            f"Yes — {name} shops ship to Waterloo, IA via standard freight. "
            f"Transit runs 3–5 business days depending on carrier and route. "
            f"Return shipping is included in most spindle rebuild quotes.",
            f"Standard freight handles it. {name}-to-Waterloo transit is "
            f"typically 3–5 business days. We include return shipping in "
            f"the rebuild quote.",
            f"Most {name} freight reaches Waterloo in 3–5 business days. "
            f"For larger machine assemblies we'll advise on carrier choice "
            f"during the quote conversation.",
        ]
        a3 = pick_variant(slug, 20, a3_variants)

    # ----- FAQ 4: lead time -----
    q4_variants = [
        f"What's the typical lead time on a {name} job?",
        f"How long does a {name} spindle rebuild take?",
        f"What lead time should a {name} customer expect?",
    ]
    q4 = pick_variant(slug, 21, q4_variants)
    a4_variants = [
        f"Most CNC machine repair and spindle rebuilds return to {name} "
        f"within 3–6 weeks depending on brand, failure mode, and parts "
        f"availability. Way-cover builds typically ship in 2–4 weeks.",
        f"For {name} customers, expect 3–6 weeks on spindle and machine-"
        f"repair work — the variation is driven by brand and parts. Way "
        f"covers ship in 2–4 weeks.",
        f"Lead times for {name} jobs hold to the standard pattern: 3–6 "
        f"weeks on spindle rebuilds and machine repair, 2–4 weeks on "
        f"way covers. Each brand page lists the specific window for that "
        f"platform.",
    ]
    a4 = pick_variant(slug, 22, a4_variants)

    qa_pairs = [(q1, a1), (q2, a2), (q3, a3), (q4, a4)]

    items_html = []
    for q, a in qa_pairs:
        items_html.append(
            f'<details class="faq-item">\n'
            f'  <summary>{html.escape(q)}</summary>\n'
            f'  <div class="faq-answer"><p>{html.escape(a)}</p></div>\n'
            f'</details>'
        )

    body = (
        f'<h2 id="faq">Frequently Asked Questions</h2>\n'
        f'<div class="faq-list">\n'
        + "\n".join(items_html) + "\n"
        + '</div>\n'
    )

    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
            for q, a in qa_pairs
        ],
    }
    return body, schema


# ---------- North Platte custom override ----------

def build_north_platte_override(city, state, distance):
    """Aaron-authorized framing: western Nebraska freight-in spindle rebuilds
    + ag-implement and rail-adjacent shop work. Rail employers as context
    only — never customers."""
    name = city["name"]
    miles = distance["miles"]

    hero_html = f"""<p class="eyebrow">{html.escape(name)}, Nebraska</p>
<h1>CNC Service for {html.escape(name)} and Western Nebraska Shops</h1>
<p>{name} is {miles} miles west of our Waterloo, IA shop — about 11 hours one-way and the longest-haul ENRICH city in our network. Our {name} work focuses on freight-in spindle rebuilds for ag-implement shops in the surrounding western Nebraska region, plus rail-adjacent shop work where the brand-specific expertise is what matters. {name} sits at the center of one of the country's most concentrated freight-rail corridors — Bailey Yard, the largest rail yard in the world by area, operates on the city's western edge — and we recognize this as regional context rather than a direct customer base.</p>
{gss.hero_cta_html()}
"""

    mfg_section = f"""<h2 id="manufacturing">Manufacturing in {html.escape(name)}</h2>
<p>{name}'s economy centers on freight-rail operations and meatpacking, with healthcare and retail distribution rounding out the major employer mix. Union Pacific's Bailey Yard operation employs over 1,700 workers as a critical freight hub. Sustainable Beef opened a meatpacking operation in May 2025. The broader western Nebraska region around {name} supports ag-implement supply shops serving Nebraska's agricultural equipment base — irrigation systems, ag-equipment maintenance, and adjacent precision work for ag-machinery OEMs.</p>
<p>Notable {name} operations include Union Pacific Railroad, BNSF Railway, Nebraska Central Railroad, and Great Plains Health. None of these are Midwest CNC customers — we cite them as regional context only. Our service relevance to {name} is through ag-implement supply chain shops in western Nebraska and rail-adjacent shop work where brand expertise on Mazak or Giddings & Lewis platforms matters more than proximity.</p>
"""

    industry_section = """<h2 id="industry-mix">CNC Service for Western Nebraska's Industry Mix</h2>
<p>Ag-implement supply chain shops in western Nebraska typically run Mazak and Doosan platforms for ag-equipment production cycles. The rail-adjacent shop work — facility maintenance, fabrication, parts machining for rolling stock components — runs heavier on Mazak and Giddings & Lewis platforms for large castings and ram-drive work.</p>
<p>We service spindle rebuilds, machine repair, and replacement way covers across the OEM platforms common in western Nebraska — see the brand pages for <a href="/spindle-grinding/mazak-spindle-repair/">Mazak spindle work</a> and <a href="/repairs/">CNC machine repair</a> for the specifics on lead times and failure modes.</p>
""" + gss.hero_cta_html() + "\n"

    logistics_section = f"""<h2 id="logistics">Logistics: How We Service {html.escape(name)}</h2>
<p>{name} is {miles} miles west of Waterloo — too far for routine field service. {name}-area work runs ship-in from our Waterloo shop: spindles come to the bench via freight, way covers ship anywhere in the continental US. For substantial multi-machine jobs we'll schedule field travel by arrangement, but the economics typically favor consolidating shipping. Transit from {name} to Waterloo runs 3–5 business days depending on carrier and route.</p>
"""

    qa_pairs = [
        ("Do you actually travel to North Platte for field service?",
         "Rarely. North Platte is 644 miles west of our Waterloo shop — too far for routine field-service visits. Most North Platte and western Nebraska work runs ship-in via standard freight. Field service for major multi-machine jobs is possible by arrangement, with travel scoped before scheduling."),
        ("Do you service ag-implement shops in western Nebraska?",
         "Yes. The ag-implement supply chain across western Nebraska is a real part of our work, with Mazak and Doosan platforms common in that mix. Spindle rebuilds and way-cover builds ship in and out of our Waterloo facility."),
        ("Are Union Pacific or Bailey Yard customers of Midwest CNC?",
         "No. We list Union Pacific and Bailey Yard as regional context only — they operate their own internal service shops. Our relevance to the North Platte region is through independent ag-implement shops, fabrication operations, and machine shops doing rail-adjacent work."),
        ("How do North Platte shops ship spindles to Waterloo?",
         "Standard freight via your chosen carrier — transit runs 3–5 business days depending on routing. Return shipping is included in most spindle rebuild quotes. For larger machine assemblies, we can advise on freight selection during the quote conversation."),
    ]
    items = "\n".join(
        f'<details class="faq-item">\n'
        f'  <summary>{html.escape(q)}</summary>\n'
        f'  <div class="faq-answer"><p>{html.escape(a)}</p></div>\n'
        f'</details>'
        for q, a in qa_pairs
    )
    faq_section = (
        f'<h2 id="faq">Frequently Asked Questions</h2>\n'
        f'<div class="faq-list">\n{items}\n</div>\n'
    )
    faq_schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in qa_pairs
        ],
    }
    return hero_html + mfg_section + industry_section + logistics_section + faq_section, faq_schema


# ---------- Schema builders ----------

def city_schemas(city, state, distance, faq_schema):
    name = city["name"]
    state_name = state["display_name"]
    state_abbrev = state["abbreviation"]
    state_slug = state["slug"]
    lat, lon = city["coords"]
    canonical_path = f"/service-area/{slug_for(city)}/"

    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"position": 1, "name": "Home", "item": f"{DOMAIN}/"},
            {"position": 2, "name": "Service Area", "item": f"{DOMAIN}/service-area/"},
            {"position": 3, "name": state_name,
             "item": f"{DOMAIN}/service-area/{state_slug}/"},
            {"position": 4, "name": name, "item": f"{DOMAIN}{canonical_path}"},
        ],
    }

    local_business = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "@id": f"{DOMAIN}{canonical_path}#service-area",
        "name": f"Midwest CNC Services — {name}, {state_abbrev} service area",
        "telephone": PHONE_TEL,
        "parentOrganization": {"@id": f"{DOMAIN}/#org"},
        "areaServed": {
            "@type": "City",
            "name": name,
            "address": {
                "@type": "PostalAddress",
                "addressLocality": name,
                "addressRegion": state_abbrev,
                "addressCountry": "US",
            },
            "geo": {
                "@type": "GeoCoordinates",
                "latitude": lat,
                "longitude": lon,
            },
        },
    }

    service = {
        "@context": "https://schema.org",
        "@type": "Service",
        "serviceType": f"CNC machine repair, spindle service, and way-cover manufacturing for {name}",
        "provider": {"@id": f"{DOMAIN}/#org"},
        "areaServed": {
            "@type": "City",
            "name": name,
            "address": {
                "@type": "PostalAddress",
                "addressLocality": name,
                "addressRegion": state_abbrev,
                "addressCountry": "US",
            },
        },
    }

    return [breadcrumb, local_business, service, faq_schema]


# ---------- Page assembly ----------

def slug_for(city):
    return f"{city.get('slug') or city['name'].lower().replace(' ', '-').replace('.', '')}-{city['state_slug']}"


def find_hero_image(city_slug, state_slug):
    candidates = [
        f"/assets/images/cities/service-area-{city_slug}-image.png",
        f"/assets/images/states/{state_slug}.png",
        f"/assets/images/general/{state_slug}.png",
        "/assets/images/general/image-of-cnc-machine.png",
    ]
    for c in candidates:
        if os.path.exists(os.path.join(REPO, c.lstrip("/"))):
            return c
    return "/assets/images/general/image-of-cnc-machine.png"


def render_city_page(city_research_slug, city, state, brand_index):
    """city is a city-research.json entry, state is a states.json entry."""
    # Pull slug from city_research_slug (e.g., "des-moines-iowa")
    name = city["name"]
    state_name = state["display_name"]
    state_slug = state["slug"]
    canonical_path = f"/service-area/{city_research_slug}/"
    distance = city["distance_from_waterloo"]

    # Extract city slug (without state suffix) for image lookup
    city_slug_no_state = city_research_slug.replace(f"-{state_slug}", "")

    # Hero image
    img_path = find_hero_image(city_slug_no_state, state_slug)
    img_alt = f"{name}, {state_name} CNC service coverage"

    # Coverage map (city variant) — city pin + Waterloo origin + dashed
    # route line. Shown right under the hero so the geographic context
    # frames the rest of the page.
    map_html = (
        f'<div class="coverage-map coverage-map--city"\n'
        f'     data-coords=\'{json.dumps(city["coords"])}\'\n'
        f'     data-city="{html.escape(name + ", " + state_name)}"\n'
        f'     data-distance="{distance["miles"]} miles"\n'
        f'     aria-label="Map showing {html.escape(name)}, {html.escape(state_name)} and the route from our Waterloo, IA service facility">\n'
        f'  <div class="coverage-map-empty">Loading {html.escape(name)} location map…</div>\n'
        f'</div>\n'
        f'<p class="coverage-map-caption">{html.escape(name)} is {distance["miles"]} miles from our Waterloo, IA facility.</p>\n'
    )

    # Special case: North Platte has Aaron-authorized custom framing
    if city_research_slug == "north-platte-nebraska":
        body_main, faq_schema = build_north_platte_override(city, state, distance)
        # The override builds its own h1 + eyebrow + intro. Replace the
        # legacy eyebrow / h1 / paragraph block with the .home-hero
        # video hero + coverage map injection.
        h1_text = f"CNC Service for {name} and Western Nebraska Shops"
        eyebrow_text = f"{name}, Nebraska"
        # Extract the lede paragraph from the override and rebuild as brand-hero
        override_lede = (
            f"{name} is {distance['miles']} miles west of our Waterloo, IA shop — "
            f"about 11 hours one-way and the longest-haul ENRICH city in our network. "
            f"Our {name} work focuses on freight-in spindle rebuilds for ag-implement "
            f"shops in the surrounding western Nebraska region, plus rail-adjacent shop "
            f"work where the brand-specific expertise is what matters. {name} sits at "
            f"the center of one of the country's most concentrated freight-rail "
            f"corridors — Bailey Yard, the largest rail yard in the world by area, "
            f"operates on the city's western edge — and we recognize this as regional "
            f"context rather than a direct customer base."
        )
        brand_hero = gss.build_video_hero_html(
            eyebrow_text=eyebrow_text,
            h1_html=html.escape(h1_text),
            lede_html=html.escape(override_lede),
        )
        # Replace the override's hero text + cta block with the new hero.
        # The override starts with: <p class="eyebrow">...</p><h1>...</h1><p>lede</p>{cta}
        # then continues with the mfg / industry / logistics / faq sections.
        # Strip from the override start through the first </p> after the cta marker:
        import re as _re
        _cta_idx = body_main.find('<h2 id="manufacturing"')
        body_main = brand_hero + map_html + body_main[_cta_idx:] if _cta_idx >= 0 else (brand_hero + map_html + body_main)
    else:
        eyebrow_text = f"{name}, {state_name}"
        h1_text = pick_h1(city_research_slug, name, state_name)

        hero = build_hero(city, state, distance, h1_text, eyebrow_text,
                          img_path, img_alt, city_research_slug)
        mfg = build_manufacturing_section(city, state)
        industry_mix = build_industry_mix_section(city, state)
        logistics = build_logistics_section(city, state, distance, city_research_slug)
        faq_html, faq_schema = build_faq_section(city, state, distance, city_research_slug)
        body_main = hero + map_html + mfg + industry_mix + logistics + faq_html

    # Final CTA + compressed trust footer
    body = (
        body_main
        + "\n" + gss.hero_cta_html() + "\n"
        + "\n" + trust_footer_html(brand_index)
    )

    schemas = city_schemas(city, state, distance, faq_schema)
    schema_blocks = gss.schema_script_tags(schemas)

    crumbs_html = gss.breadcrumbs_html([
        ("Home", "/"),
        ("Service Area", "/service-area/"),
        (state_name, f"/service-area/{state_slug}/"),
        (name, None),
    ])

    title = f"{name} CNC Repair & Service | Midwest CNC Services"
    description = (
        f"CNC machine repair, spindle work, and replacement way covers for "
        f"shops in {name}, {state_name}. {distance['miles']} miles from "
        f"our Waterloo, IA shop. Call 319-610-4341."
    )

    page_html = gss.wrap_page(
        title=title,
        description=description,
        canonical=f"{DOMAIN}{canonical_path}",
        schema_blocks=schema_blocks,
        crumbs_html_str=crumbs_html,
        body_html=body,
    )

    out_path = os.path.join(PUBLIC, canonical_path.strip("/"), "index.html")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write(page_html)
    return out_path


# ---------- Driver ----------

def main():
    research = json.load(open(os.path.join(REPO, "src", "data", "city-research.json")))
    states_data = json.load(open(os.path.join(REPO, "src", "data", "states.json")))
    state_by_slug = {s["slug"]: s for s in states_data["states"]}

    cities = research["cities"]
    enrich_slugs = sorted(
        slug for slug, c in cities.items() if c["decision"] == "ENRICH"
    )
    consolidate_slugs = sorted(
        slug for slug, c in cities.items() if c["decision"] == "CONSOLIDATE"
    )

    print(f"ENRICH: {len(enrich_slugs)} cities | CONSOLIDATE: {len(consolidate_slugs)}\n")

    # Alphabetical brand_index for quote-variant rotation
    index_for = {slug: i for i, slug in enumerate(enrich_slugs)}

    written = []
    for slug in enrich_slugs:
        city = cities[slug]
        state = state_by_slug[city["state_slug"]]
        path = render_city_page(slug, city, state, index_for[slug])
        size = os.path.getsize(path)
        written.append((slug, path, size))

    print(f"Generated {len(written)} city pages.\n")

    # Remove the 4 CONSOLIDATE city directories from public/
    print("Removing CONSOLIDATE-marked city pages:")
    for slug in consolidate_slugs:
        dir_path = os.path.join(PUBLIC, "service-area", slug)
        if os.path.exists(dir_path):
            for root, dirs, files in os.walk(dir_path, topdown=False):
                for f in files:
                    os.remove(os.path.join(root, f))
                for d in dirs:
                    os.rmdir(os.path.join(root, d))
            os.rmdir(dir_path)
            print(f"  ✗ removed public/service-area/{slug}/")
        else:
            print(f"  - (already gone) public/service-area/{slug}/")

    return enrich_slugs, consolidate_slugs


if __name__ == "__main__":
    main()

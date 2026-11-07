#!/usr/bin/env python3
"""
Brand page generator for /spindle-grinding/*.

Reads src/data/spindle-brands.json (with Ken's confirmed content) and writes
one Markdown file per brand to src/content/spindle-brands/{slug}.md.

Discipline:
- Ken's exact sentences are the substance. Connective tissue is minimal.
- No claims that aren't traceable to ken_input or global_context (no
  "flat-rate pricing", "photo-verified", or specific certifications that
  Ken didn't mention).
- "bearing pack" wording is preferred over "front bearing wear" in our
  connective tissue only — Ken's own quotes keep his wording intact.
- Page types diverge: cnc_spindle vs press_brake_service vs
  laser_punch_service get framing-appropriate language. Amada and Trumpf
  are NOT described as spindle work.
"""

import html
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(REPO, "src", "data", "spindle-brands.json")
# Three content directories, one per service kind. Markdown files are
# written here; markdown_to_html.py picks them up and outputs to the
# canonical URL inside public/.
OUTDIR_SPINDLE = os.path.join(REPO, "src", "content", "spindle-brands")
OUTDIR_REPAIR  = os.path.join(REPO, "src", "content", "machine-repair")
OUTDIR_COVERS  = os.path.join(REPO, "src", "content", "way-covers")

PHONE_DISPLAY = "319-610-4341"
PHONE_TEL = "+13196104341"
STATES = ["Iowa", "Illinois", "Minnesota", "Wisconsin", "Nebraska", "Missouri", "Texas"]


# ---------- Helpers ----------

def clean_ken(text):
    """Strip worksheet conversational artifacts from Ken's answers."""
    text = (text or "").strip()
    for prefix in ("Confirmed. ", "Confirmed.", "Confirmed "):
        if text.startswith(prefix):
            return text[len(prefix):].lstrip()
    return text


def ensure_period(s):
    s = (s or "").rstrip()
    if not s:
        return s
    return s if s[-1] in ".!?" else s + "."


def lead_short(lt):
    """Pull the 'N–M weeks' fragment out of Ken's lead-time answer."""
    if not lt:
        return ""
    m = re.search(r"\d+\s*[–—\-]\s*\d+\s*weeks?", lt)
    if m:
        return re.sub(r"\s*[–—\-]\s*", "–", m.group(0))
    # fallback: first clause
    return lt.split(".")[0].strip()


def yaml_string(s):
    """Quote a string for YAML, escaping internal double quotes."""
    s = (s or "").replace("\\", "\\\\").replace('"', '\\"')
    return f'"{s}"'


# ---------- Brand-specific framing toggles ----------

# Brands whose ken_input.brand_specifics describes the work as
# standard/straightforward rather than brand-specifically complex. These
# get the "mainstream" "How We Approach" framing instead of the default
# "brand-specific factors drive how we plan the job" lead-in.
MAINSTREAM_BRANDS = {"fanuc", "hurco", "doosan", "amera-seiki"}

# When a brand's common_failure_mode starts with one of these words, it's
# a bare noun phrase that reads awkwardly after "What we see most on
# {Brand} spindles:". For these we use the alternative hero structure
# "{Brand} spindles tend to come in with {lowercased quote}".
NOUN_PHRASE_OPENERS = {
    "bearing", "front", "classic", "large", "heavy",
    "high", "high-speed", "motor", "pulley", "mostly",
    "optics",
}

# Page-type → machine-noun used in the noun-phrase hero variant.
MACHINE_NOUN = {
    "cnc_spindle":         "spindles",
    "press_brake_service": "machines",
    "laser_punch_service": "systems",
}

# Customer-quote framing — rotates per brand (alphabetical by slug). Both
# variants are appended *after* Ken's static opener inside the same
# blockquote, so every page still leads with his "machine was done for"
# line and only the framing changes.
QUOTE_OPENER = '"Honestly, we thought the machine was done for."'


def customer_quote_framing(brand_index, equipment_phrase):
    """Return the rotating framing sentence that follows QUOTE_OPENER.
    equipment_phrase varies by service kind (e.g. 'a new spindle',
    'a replacement machine', 'replacement way covers and the retrofit time')."""
    if brand_index % 2 == 0:
        return ("Most customers tell us they're relieved to avoid replacement "
                "lead times and six-figure capital expenses.")
    return (f"It saves shops from replacement lead times and the capital "
            f"expense of {equipment_phrase}.")


def hero_image_for(brand, service_kind):
    """Pick a hero image for a brand × service combination.
    service_kind: 'spindle', 'machine_repair', or 'way_covers'.
    Returns (path, alt) or (None, None) if nothing fits.
    """
    slug = brand["slug"]
    name = brand["brand_display_name"]

    if service_kind == "spindle":
        candidates = [
            (f"/assets/images/services/spindles-repair-{slug}-spindle-repair-image.png",
             f"{name} spindle on the rebuild bench at Midwest CNC Services"),
            (f"/assets/images/services/repairs-{slug}-cnc-machine-repair-image.png",
             f"{name} machine service work at Midwest CNC Services"),
        ]
        generic = ("/assets/images/general/image-of-spindle-grinding.png",
                   "CNC spindle grinding work at Midwest CNC Services")
    elif service_kind == "machine_repair":
        candidates = [
            (f"/assets/images/services/repairs-{slug}-cnc-machine-repair-image.png",
             f"{name} CNC machining center being serviced at Midwest CNC Services"),
            (f"/assets/images/services/spindles-repair-{slug}-spindle-repair-image.png",
             f"{name} machine service work at Midwest CNC Services"),
        ]
        generic = ("/assets/images/general/image-of-cnc-machine.png",
                   "CNC machine service work at Midwest CNC Services")
    elif service_kind == "way_covers":
        candidates = [
            (f"/assets/images/services/way-covers-{slug}-cnc-way-covers-image.png",
             f"Replacement {name} CNC way covers manufactured by Midwest CNC Services"),
        ]
        generic = ("/assets/images/general/image-of-way-covers.png",
                   "CNC way cover manufacturing at Midwest CNC Services")
    else:
        return None, None

    for path, alt in candidates:
        if os.path.exists(os.path.join(REPO, path.lstrip("/"))):
            return path, alt
    if os.path.exists(os.path.join(REPO, generic[0].lstrip("/"))):
        return generic
    return None, None


# ---------- Peer linking ----------

PEERS = {
    "mazak":          ["okuma", "dmg-mori", "mori-seiki"],
    "haas":           ["doosan", "hurco", "fadal"],
    "okuma":          ["mazak", "dmg-mori", "mori-seiki"],
    "dmg-mori":       ["mazak", "mori-seiki", "makino"],
    "mori-seiki":     ["dmg-mori", "mazak", "okuma"],
    "doosan":         ["haas", "hurco", "amera-seiki"],
    "brother":        ["makino", "fanuc", "hurco"],
    "hurco":          ["haas", "doosan", "brother"],
    "makino":         ["mazak", "dmg-mori", "brother"],
    "fanuc":          ["brother", "hurco", "makino"],
    "toyoda":         ["mazak", "dmg-mori", "niigata"],
    "fadal":          ["haas", "hurco", "monarch"],
    "hitachi-seiki":  ["mori-seiki", "mazak", "fadal"],
    "giddings-lewis": ["toyoda", "niigata", "makino"],
    "monarch":        ["fadal", "hitachi-seiki", "mazak"],
    "amera-seiki":    ["doosan", "johnford", "hurco"],
    "niigata":        ["makino", "toyoda", "mazak"],
    "johnford":       ["amera-seiki", "doosan", "hurco"],
}


def peer_lines(slug, brands_by_slug):
    peers = PEERS.get(slug, [])
    out = []
    for p in peers:
        n = brands_by_slug[p]["brand_display_name"]
        out.append(f"  - [{n} spindle grinding](/spindle-grinding/{p}-spindle-repair/)")
    return out


# ---------- Front matter ----------

def front_matter(brand, *, title, h1, meta_description,
                 service_type, canonical_path,
                 crumb_middle, crumb_leaf,
                 draft=False, verification_pending=None):
    """Build a page's YAML front matter. Each render function owns its
    own title, canonical, breadcrumb, and draft state — front_matter just
    formats them consistently."""
    slug = brand["slug"]
    lines = [
        "---",
        f"title: {yaml_string(title)}",
        f"meta_description: {yaml_string(meta_description)}",
        f"h1: {yaml_string(h1)}",
        f"slug: {yaml_string(slug)}",
        f"page_type: {yaml_string(brand['page_type'])}",
    ]
    if draft:
        lines.append("draft: true")
    if verification_pending:
        lines.append(f"verification_pending: {yaml_string(verification_pending)}")
    lines += [
        "schema_data:",
        "  service:",
        "    \"@type\": Service",
        f"    serviceType: {yaml_string(service_type)}",
        "    provider:",
        "      \"@id\": \"#org\"",
        "    areaServed:",
    ]
    for s in STATES:
        lines.append(f"      - {s}")
    lines += [
        "  local_business:",
        "    \"@type\": LocalBusiness",
        "    \"@id\": \"#org\"",
        f"    name: {yaml_string('Midwest CNC Services')}",
        f"    telephone: {yaml_string(PHONE_TEL)}",
        "    # address, geo, openingHours filled in by template at build time",
        "  breadcrumb:",
        "    \"@type\": BreadcrumbList",
        "    itemListElement:",
        f"      - {{ position: 1, name: Home, item: {yaml_string(absolute_url('/'))} }}",
        f"      - {{ position: 2, name: {yaml_string(crumb_middle[0])}, item: {yaml_string(absolute_url(crumb_middle[1]))} }}",
        f"      - {{ position: 3, name: {yaml_string(crumb_leaf)}, item: {yaml_string(absolute_url(canonical_path))} }}",
        "---",
        "",
    ]
    return "\n".join(lines)


CANONICAL_DOMAIN = "https://midwestcncservices.com"


def absolute_url(path):
    """Prefix an internal path with the canonical domain (for schema)."""
    if not path:
        return path
    if path.startswith(("http://", "https://")):
        return path
    return f"{CANONICAL_DOMAIN}{path}"


def make_h1_and_eyebrow(brand):
    """Per-brand H1 + eyebrow. The eyebrow is the service category
    (matching breadcrumb-style taxonomy); the H1 is the SEO-targeted
    brand+service phrase. Amada and Trumpf have no eyebrow — their H1 IS
    the service category, so a duplicated eyebrow would add nothing."""
    name = brand["brand_display_name"]
    pt = brand["page_type"]
    if pt == "press_brake_service":
        return ("Amada Press Brake & Punch Service", None)
    if pt == "laser_punch_service":
        return ("Trumpf Laser & Punch Service", None)
    # cnc_spindle — longer brand names drop the "& Rebuilds" suffix to keep
    # the H1 readable.
    if len(name) > 11:
        h1 = f"{name} Spindle Repair"
    else:
        h1 = f"{name} Spindle Repair & Rebuilds"
    return (h1, f"{name} Spindle Repair & Grinding")


def _alt_title(brand):
    if brand["slug"] == "amada":
        return "Amada Press Brake & Punch Service"
    if brand["slug"] == "trumpf":
        return "Trumpf Laser & Punch Service"
    return f"{brand['brand_display_name']} Service"


def _alt_breadcrumb(brand):
    if brand["slug"] == "amada":
        return "Amada Press Brake & Punch Service"
    if brand["slug"] == "trumpf":
        return "Trumpf Laser & Punch Service"
    return f"{brand['brand_display_name']} Service"


# ---------- CTAs and shared blocks ----------

def hero_cta():
    return f"[Get a Quote](#quote) · [{PHONE_DISPLAY}](tel:{PHONE_TEL})"


def machine_lookup_html():
    """Site-wide MachineLookup widget. Emits markup + inline JS that fetches
    /data/machines.json on demand, fuzzy-matches user input against
    model + alias strings (case + dash insensitive, partial match after
    3 chars), and routes to the matching series-spoke page.

    The script is inlined per page so the widget works without a build
    pipeline. CSS lives in m2h.CSS under .machine-lookup."""
    return """<div class="machine-lookup" id="machine-lookup">
  <label for="machine-lookup-input" class="machine-lookup-label">Find your machine</label>
  <input
    type="text"
    id="machine-lookup-input"
    class="machine-lookup-input"
    placeholder="Enter your machine model (e.g. QTN-250, VF-2SS, Puma 2600SY, DMU 50)"
    autocomplete="off"
    aria-controls="machine-lookup-results"
    aria-expanded="false">
  <div class="machine-lookup-results" id="machine-lookup-results" role="listbox" hidden></div>
</div>
<script>
(function () {
  var lookup  = document.getElementById('machine-lookup');
  if (!lookup) return;
  var input   = document.getElementById('machine-lookup-input');
  var results = document.getElementById('machine-lookup-results');
  var machines = null;
  var loading  = null;

  function normalize(s) {
    return (s || '').toLowerCase().replace(/[\\s\\-]/g, '');
  }
  function escapeHTML(s) {
    return String(s).replace(/[&<>\"']/g, function (c) {
      return ({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',\"'\":'&#39;'})[c];
    });
  }
  function loadData() {
    if (machines) return Promise.resolve(machines);
    if (loading)  return loading;
    loading = fetch('/data/machines.json')
      .then(function (r) { return r.json(); })
      .then(function (d) { machines = d.machines || []; return machines; })
      .catch(function ()  { machines = []; return machines; });
    return loading;
  }
  function scoreMachine(m, nq) {
    var candidates = [m.model].concat(m.aliases || []);
    var best = 0;
    for (var i = 0; i < candidates.length; i++) {
      var nc = normalize(candidates[i]);
      if (!nc) continue;
      if (nc === nq)            return 100;
      if (nc.indexOf(nq) === 0) best = Math.max(best, 80);
      else if (nc.indexOf(nq) >= 0) best = Math.max(best, 50);
    }
    return best;
  }
  function search(q) {
    var nq = normalize(q);
    if (nq.length < 3 || !machines) return [];
    var scored = [];
    for (var i = 0; i < machines.length; i++) {
      var s = scoreMachine(machines[i], nq);
      if (s > 0) scored.push({ m: machines[i], score: s });
    }
    scored.sort(function (a, b) { return b.score - a.score; });
    return scored.slice(0, 5).map(function (x) { return x.m; });
  }
  function renderResults(matches) {
    if (!matches.length) {
      results.innerHTML =
        '<div class=\"machine-lookup-empty\">' +
          'We service older and obscure machines too. ' +
          '<a href=\"/get-a-quote/\">Get a quote</a> or call ' +
          '<a href=\"tel:+13196104341\">319-610-4341</a>.' +
        '</div>';
    } else {
      results.innerHTML = matches.map(function (m) {
        // Context-aware URL routing: machines.json stores the repair-section
        // spoke URL; when the user is on a /spindle-grinding/ or /way-covers/
        // page we rewrite the URL to the corresponding service-line spoke so
        // the user lands on the right content without a context switch.
        var href = m.spoke_url;
        if (/^\\/spindle-grinding\\//.test(window.location.pathname)) {
          href = href.replace(/^\\/repairs\\/([\\w-]+)-cnc-machine-repair\\//,
                              '/spindle-grinding/$1-spindle-repair/');
        } else if (/^\\/way-covers\\//.test(window.location.pathname)) {
          href = href.replace(/^\\/repairs\\/([\\w-]+)-cnc-machine-repair\\//,
                              '/way-covers/$1-cnc-way-covers/');
        }
        return (
          '<a class=\"machine-lookup-result\" href=\"' + escapeHTML(href) + '\" role=\"option\">' +
            '<span class=\"machine-lookup-result-brand\">'  + escapeHTML(m.brand)  + '</span>' +
            '<span class=\"machine-lookup-result-model\">'  + escapeHTML(m.model)  + '</span>' +
            '<span class=\"machine-lookup-result-series\">' + escapeHTML(m.series) + '</span>' +
            '<span class=\"machine-lookup-result-arrow\" aria-hidden=\"true\">&rarr;</span>' +
          '</a>'
        );
      }).join('');
    }
    results.hidden = false;
    input.setAttribute('aria-expanded', 'true');
  }
  function hideResults() {
    results.hidden = true;
    input.setAttribute('aria-expanded', 'false');
  }
  var debounceId;
  input.addEventListener('input', function () {
    clearTimeout(debounceId);
    debounceId = setTimeout(function () {
      var q = input.value.trim();
      if (q.length < 3) { hideResults(); return; }
      loadData().then(function () { renderResults(search(q)); });
    }, 100);
  });
  input.addEventListener('focus', function () {
    var q = input.value.trim();
    if (q.length >= 3 && machines) renderResults(search(q));
  });
  document.addEventListener('click', function (e) {
    if (!lookup.contains(e.target)) hideResults();
  });
  // Pre-warm the data file on the first interaction with the page
  document.addEventListener('mousemove', function init() {
    document.removeEventListener('mousemove', init);
    loadData();
  }, { once: true });
})();
</script>
"""


def workflow_block(noun, step3_body):
    """noun: 'spindle rebuild', 'service', 'job' — what gets quoted."""
    return f"""**Step 1 — Contact Us.** Call 319-610-4341 or use the quote form below. [Get a Quote](#quote)

**Step 2 — Grab Model #.** We'll fire back price, lead time, and shipping ETA after reviewing your details. [Get a Quote](#quote)

**Step 3 — Approve & Rebuild.** {step3_body}

*Quote form rendered here at build time.*
"""


def trust_block(g, brand_page_type, brand_index, equipment_phrase):
    """Trim Ken's certifications to the brand's page type, then append
    the rotating customer-quote framing with a service-appropriate
    equipment_phrase (e.g. 'a new spindle', 'a replacement machine',
    'replacement way covers and the retrofit time')."""
    if brand_page_type == "cnc_spindle":
        certs = clean_ken(g["certifications"])
    elif brand_page_type == "press_brake_service":
        certs = ("Experienced field technicians and established relationships "
                 "with aftermarket parts suppliers.")
    elif brand_page_type == "laser_punch_service":
        certs = ("Experienced field technicians, laser alignment capability, "
                 "and experience navigating Trumpf's OEM parts network on "
                 "planned-downtime jobs.")
    else:
        certs = clean_ken(g["certifications"])

    framing = customer_quote_framing(brand_index, equipment_phrase)
    return f"""## Why Shops Trust Us

{certs}

> {QUOTE_OPENER} {framing}
"""


def _self_urls(brand):
    """URLs that resolve to the current page (for self-link filtering, fix 5)."""
    s = {brand.get("current_url")}
    if brand.get("old_url"):
        s.add(brand["old_url"])
    return {u for u in s if u}


def _can_link_way_covers(b):
    """Don't link to draft way-cover pages from anywhere else (SAFEGUARD)."""
    return (b.get("services_offered", {}).get("way_covers")
            and not b.get("way_covers_verification_pending"))


def related_block_cnc(brand, brands_by_slug):
    """Related Services on a brand's spindle page. TASK 5 restores the
    cross-service links (machine repair + way covers) gated on
    services_offered, and filters out any link pointing at the current
    page or a way-covers page still flagged for verification."""
    name = brand["brand_display_name"]
    slug = brand["slug"]
    self_urls = _self_urls(brand)
    so = brand.get("services_offered", {})

    # /spindles-repair/{slug}-spindle-repair/ is intentionally NOT listed —
    # it 301-redirects to this page (see public/_redirects).
    candidate_links = []
    if so.get("machine_repair"):
        candidate_links.append(
            (f"{name} CNC machine repair", f"/repairs/{slug}-cnc-machine-repair/")
        )
    if _can_link_way_covers(brand):
        candidate_links.append(
            (f"{name} CNC way covers", f"/way-covers/{slug}-cnc-way-covers/")
        )
    sibling_links = [(t, u) for (t, u) in candidate_links if u not in self_urls]

    peer_lis = []
    for p in PEERS.get(slug, []):
        n = brands_by_slug[p]["brand_display_name"]
        url = brands_by_slug[p].get("current_url", f"/spindle-grinding/{p}-spindle-repair/")
        if url in self_urls:
            continue
        peer_lis.append(f"  - [{n} spindle grinding]({url})")

    out = [f"## Related {name} Services\n"]
    for t, u in sibling_links:
        out.append(f"- [{t}]({u})")
    if peer_lis:
        out.append("- See also spindle grinding on related platforms:")
        out.extend(peer_lis)
    out.append("")
    out.append(
        "We serve shops across " + ", ".join(STATES[:-1]) + ", and " + STATES[-1] + "."
    )
    return "\n".join(out) + "\n"


def related_block_machine_repair(brand):
    """Related Services on a brand's machine-repair page. Card grid
    instead of plain bullets — uses .related-grid class for the polished
    card treatment. Self = the machine-repair canonical, NOT the brand's
    main current_url (the spindle page is a valid cross-link from here)."""
    name = brand["brand_display_name"]
    slug = brand["slug"]
    self_url = f"/repairs/{slug}-cnc-machine-repair/"
    so = brand.get("services_offered", {})

    cards = []
    if so.get("spindle"):
        url = f"/spindle-grinding/{slug}-spindle-repair/"
        if url != self_url:
            cards.append(
                f'<li><a href="{url}">'
                f'<span>{html.escape(name)} spindle repair</span>'
                f'</a></li>'
            )
    if _can_link_way_covers(brand):
        url = f"/way-covers/{slug}-cnc-way-covers/"
        if url != self_url:
            cards.append(
                f'<li><a href="{url}">'
                f'<span>{html.escape(name)} CNC way covers</span>'
                f'</a></li>'
            )

    if not cards:
        return ""

    states_inline = ", ".join(STATES[:-1]) + ", and " + STATES[-1]
    return (
        f'\n<h2 id="related-services">Related {html.escape(name)} Services</h2>\n'
        f'<ul class="related-grid">{"".join(cards)}</ul>\n'
        f'<p class="related-coverage">We serve shops across {states_inline}.</p>\n'
    )


def related_block_way_covers(brand):
    """Related Services on a brand's way-covers page. Self = the
    way-covers canonical. cnc_spindle brands cross-link to their spindle +
    machine-repair pages; Amada/Trumpf link back to their main service page."""
    name = brand["brand_display_name"]
    slug = brand["slug"]
    self_url = f"/way-covers/{slug}-cnc-way-covers/"
    so = brand.get("services_offered", {})

    lines = [f"## Related {name} Services\n"]
    if so.get("spindle"):
        url = f"/spindle-grinding/{slug}-spindle-repair/"
        if url != self_url:
            lines.append(f"- [{name} spindle repair]({url})")
    if so.get("machine_repair"):
        url = f"/repairs/{slug}-cnc-machine-repair/"
        if url != self_url:
            lines.append(f"- [{name} CNC machine repair]({url})")
    elif brand.get("current_url"):
        # Non-spindle brand (Amada/Trumpf): link back to the brand's main page
        main = brand["current_url"]
        if main != self_url:
            lines.append(f"- [{_alt_breadcrumb(brand)}]({main})")
    lines.append("")
    lines.append(
        "We serve shops across " + ", ".join(STATES[:-1]) + ", and " + STATES[-1] + "."
    )
    return "\n".join(lines) + "\n"


def related_block_alt(brand, brands_by_slug):
    """Related Services for Amada and Trumpf — link to each other plus the
    /repairs/ and /service-area/ hubs (fix 6). Filters self-links (fix 5)."""
    name = brand["brand_display_name"]
    self_urls = _self_urls(brand)

    # The "peer" non-spindle brand for cross-linking
    peer_slug = "trumpf" if brand["slug"] == "amada" else "amada"
    peer = brands_by_slug.get(peer_slug)

    lines = [f"## Related {name} Services\n"]
    if peer:
        peer_name = peer["brand_display_name"]
        peer_url = peer.get("current_url", "")
        if peer_url and peer_url not in self_urls:
            label = ("Trumpf laser & punch service"
                     if peer_slug == "trumpf"
                     else "Amada press brake & punch service")
            lines.append(f"- [{label}]({peer_url})")

    for label, url in (("All CNC repair services", "/repairs/"),
                       ("Service-area coverage", "/service-area/")):
        if url not in self_urls:
            lines.append(f"- [{label}]({url})")

    lines.append("")
    lines.append(
        f"We serve shops across {', '.join(STATES[:-1])}, and {STATES[-1]} "
        f"from our Waterloo, Iowa shop."
    )
    return "\n".join(lines) + "\n"


def blog_block():
    return """## Recent from the Blog

*Rendered by the blog teaser component at build time.*
"""


# ---------- Brand → regional emphasis (Phase 4 cross-links) ----------
# Maps each brand to 2–3 states + cities where the brand has the strongest
# presence per Aaron's state briefs + Ken's brand_specifics. Used for
# inline cross-links on brand pages.

BRAND_REGIONAL_EMPHASIS = {
    "mazak":          [("iowa", ["waterloo-iowa", "davenport-iowa"]),
                       ("illinois", ["peoria-illinois"]),
                       ("texas", ["fort-worth-texas"])],
    "haas":           [("wisconsin", ["milwaukee-wisconsin", "kenosha-wisconsin"]),
                       ("illinois", ["chicago-illinois", "naperville-illinois"]),
                       ("minnesota", ["minneapolis-minnesota"])],
    "okuma":          [("minnesota", ["minneapolis-minnesota", "rochester-minnesota"]),
                       ("illinois", ["rockford-illinois"]),
                       ("wisconsin", ["madison-wisconsin"])],
    "dmg-mori":       [("missouri", ["st-louis-missouri"]),
                       ("texas", ["fort-worth-texas"]),
                       ("illinois", ["rockford-illinois"])],
    "mori-seiki":     [("iowa", ["cedar-rapids-iowa"]),
                       ("illinois", ["rockford-illinois"]),
                       ("minnesota", ["minneapolis-minnesota"])],
    "doosan":         [("iowa", ["davenport-iowa", "waterloo-iowa"]),
                       ("illinois", ["peoria-illinois"]),
                       ("nebraska", ["lincoln-nebraska"])],
    "brother":        [("minnesota", ["rochester-minnesota", "minneapolis-minnesota"]),
                       ("wisconsin", ["madison-wisconsin"]),
                       ("texas", ["austin-texas"])],
    "hurco":          [("iowa", ["cedar-rapids-iowa", "ames-iowa"]),
                       ("illinois", ["naperville-illinois"]),
                       ("wisconsin", ["madison-wisconsin"])],
    "makino":         [("missouri", ["st-louis-missouri"]),
                       ("texas", ["fort-worth-texas"]),
                       ("minnesota", ["rochester-minnesota"])],
    "fanuc":          [("wisconsin", ["milwaukee-wisconsin"]),
                       ("illinois", ["rockford-illinois", "chicago-illinois"]),
                       ("texas", ["austin-texas"])],
    "toyoda":         [("iowa", ["davenport-iowa"]),
                       ("illinois", ["peoria-illinois"]),
                       ("texas", ["houston-texas"])],
    "fadal":          [("iowa", ["cedar-rapids-iowa"]),
                       ("illinois", ["rockford-illinois"]),
                       ("missouri", ["springfield-missouri"])],
    "hitachi-seiki":  [("illinois", ["rockford-illinois"]),
                       ("wisconsin", ["milwaukee-wisconsin"]),
                       ("missouri", ["kansas-city-missouri"])],
    "giddings-lewis": [("illinois", ["peoria-illinois"]),
                       ("iowa", ["davenport-iowa"]),
                       ("texas", ["houston-texas"])],
    "monarch":        [("iowa", ["cedar-rapids-iowa"]),
                       ("illinois", ["rockford-illinois"]),
                       ("wisconsin", ["milwaukee-wisconsin"])],
    "amera-seiki":    [("iowa", ["ames-iowa"]),
                       ("nebraska", ["kearney-nebraska"]),
                       ("missouri", ["springfield-missouri"])],
    "niigata":        [("wisconsin", ["green-bay-wisconsin"]),
                       ("illinois", ["peoria-illinois"]),
                       ("texas", ["houston-texas"])],
    "johnford":       [("iowa", ["davenport-iowa"]),
                       ("nebraska", ["kearney-nebraska"]),
                       ("texas", ["houston-texas"])],
    "amada":          [("wisconsin", ["green-bay-wisconsin"]),
                       ("illinois", ["chicago-illinois"]),
                       ("texas", ["fort-worth-texas"])],
    "trumpf":         [("missouri", ["st-louis-missouri"]),
                       ("texas", ["fort-worth-texas", "dallas-texas"]),
                       ("wisconsin", ["milwaukee-wisconsin"])],
}


# Manufacturer sameAs URLs (Service schema enrichment)
BRAND_SAMEAS = {
    "mazak":          "https://www.mazakusa.com/",
    "haas":           "https://www.haascnc.com/",
    "okuma":          "https://www.okuma.com/americas",
    "dmg-mori":       "https://us.dmgmori.com/",
    "mori-seiki":     "https://us.dmgmori.com/",
    "doosan":         "https://www.dn-solutions.com/",
    "brother":        "https://www.brothermachinetools.com/",
    "hurco":          "https://www.hurco.com/",
    "makino":         "https://www.makino.com/",
    "fanuc":          "https://www.fanucamerica.com/",
    "toyoda":         "https://www.toyoda.com/",
    "fadal":          None,  # defunct manufacturer
    "hitachi-seiki":  None,
    "giddings-lewis": None,
    "monarch":        None,
    "amera-seiki":    "https://www.ameraseiki.com/",
    "niigata":        "https://www.niigatausa.com/",
    "johnford":       "https://www.absolutemachine.com/johnford/",
    "amada":          "https://www.amada.com/america",
    "trumpf":         "https://www.trumpf.com/en_US/",
}


def brand_industry_phrase(brand, ki):
    """Return a short industries phrase for the hero industry-tie sentence.
    Pulls from brand_specifics + cross-references known industry-brand ties."""
    slug = brand["slug"]
    # Industry shorthand by brand — Ken-derived where possible
    industry_map = {
        "mazak":          "Iowa and Illinois ag-equipment and heavy-machinery supply chains",
        "haas":           "Midwest job shops doing broad-coverage CNC work",
        "okuma":          "Minnesota medical-device and Illinois aerospace shops",
        "dmg-mori":       "St. Louis and Fort Worth aerospace and defense supply chains",
        "mori-seiki":     "long-running mid-sized Mori shops across the Midwest",
        "doosan":         "ag-equipment supply chains and Midwest production shops",
        "brother":        "Twin Cities medical-device and Madison biotech precision work",
        "hurco":          "small and mid-sized Midwest job shops running mixed work",
        "makino":         "aerospace, mold/die, and high-precision medical operations",
        "fanuc":          "broad production environments — controls familiarity matters",
        "toyoda":         "heavy-machining Iowa, Illinois, and Houston O&G work",
        "fadal":          "long-running Fadal installs still cutting daily across the Midwest",
        "hitachi-seiki":  "legacy HMC and mill-turn shops from the 1980s–90s, still in service",
        "giddings-lewis": "heavy-bore and large-part work — Peoria, Quad Cities, Houston",
        "monarch":        "older Monarch lathe shops doing heritage rebuild and restoration work",
        "amera-seiki":    "value-oriented Taiwanese installs in mid-sized Midwest shops",
        "niigata":        "Wisconsin HMC and specialty-gear shops",
        "johnford":       "heavy Taiwanese-built machines in price-conscious shops",
        "amada":          "press brake and turret punch shops across the Wisconsin–Illinois corridor",
        "trumpf":         "DFW aerospace laser cutting and Milwaukee fabrication shops",
    }
    return industry_map.get(slug, "Midwest manufacturing shops across our service area")


def brand_cross_links_section(brand, brands_by_slug):
    """Phase 4 cross-link section — links to states + cities where this brand
    has strongest documented presence. Skip if brand has no emphasis mapping."""
    slug = brand["slug"]
    name = brand["brand_display_name"]
    emphasis = BRAND_REGIONAL_EMPHASIS.get(slug, [])
    if not emphasis:
        return ""

    items = []
    for state_slug, city_slugs in emphasis:
        state_display = state_slug.replace("-", " ").title()
        if state_slug == "dmg-mori":  # safety
            state_display = "DMG Mori"
        state_link = f'<a href="/service-area/{state_slug}/">{state_display}</a>'
        city_links = []
        for cs in city_slugs:
            city_disp = cs.replace(f"-{state_slug}", "").replace("-", " ").title()
            city_disp = city_disp.replace("St ", "St. ")
            city_links.append(f'<a href="/service-area/{cs}/">{html.escape(city_disp)}</a>')
        if city_links:
            cities_phrase = " and ".join(city_links) if len(city_links) <= 2 \
                else ", ".join(city_links[:-1]) + ", and " + city_links[-1]
            items.append(f"<li>{state_link} — particularly {cities_phrase}</li>")
        else:
            items.append(f"<li>{state_link}</li>")

    return (
        f'<h2 id="regional-presence">Where {html.escape(name)} Work Concentrates</h2>\n'
        f"<p>{name} platforms have strong regional concentration in our service "
        f"area:</p>\n"
        f"<ul>{''.join(items)}</ul>\n"
    )


def brand_faq_section(brand, ki, service_kind):
    """Phase 4: 3-4 FAQs per brand page, pulling from Ken's data.
    service_kind: 'spindle', 'machine_repair', 'way_covers'."""
    name = brand["brand_display_name"]
    slug = brand["slug"]
    failure = clean_ken(ki.get("common_failure_mode", ""))
    lead_time = clean_ken(ki.get("typical_lead_time", ""))
    specifics = clean_ken(ki.get("brand_specifics", ""))
    is_legacy = "legacy_context" in brand
    parts = clean_ken(ki.get("parts_situation", ""))

    qa_pairs = []

    if service_kind == "spindle":
        # Q0: geo-intent "near me" query (answer-first for AEO)
        qa_pairs.append((
            f"Where can I get {name} spindle repair near me?",
            f"Midwest CNC Services rebuilds {name} spindles from our Waterloo, "
            f"Iowa shop and ships finished work to any continental US destination. "
            f"Direct service covers Iowa, Illinois, Wisconsin, Minnesota, Nebraska, "
            f"Missouri, and Texas. Call 319-610-4341 to scope the job.",
        ))
        # Q0b: cost intent
        qa_pairs.append((
            f"How much does a {name} spindle rebuild cost?",
            f"{name} spindle rebuild cost depends on the failure mode — "
            f"bearing-pack replacement, taper damage, preload loss, and crash "
            f"recovery all scope differently. We quote after reviewing the "
            f"symptoms, model, and photos where available. Most quotes go out "
            f"within one business day with a lead time and parts breakdown.",
        ))
        # Q1: lead time
        if lead_time:
            qa_pairs.append((
                f"What's the typical lead time on a {name} spindle rebuild?",
                f"{lead_time} Each job is scoped during the quote — bearing-pack "
                f"damage, parts availability, and crash-related work all shift the "
                f"window.",
            ))
        # Q2: common failure mode
        if failure:
            qa_pairs.append((
                f"What's the most common {name} spindle failure you see?",
                f"{failure}",
            ))
        # Q3: brand-specifics or grinding
        if specifics:
            qa_pairs.append((
                f"What should I know about {name} spindle rebuilds specifically?",
                f"{specifics}",
            ))
        # Q4: parts (legacy brands) or general
        if is_legacy and parts:
            qa_pairs.append((
                f"How do you handle {name} parts sourcing on a rebuild?",
                f"{parts}",
            ))
        else:
            qa_pairs.append((
                f"Do you grind {name} spindles back to factory tolerance?",
                f"Yes — precision spindle balancing and grinding to runout is "
                f"part of every rebuild we do, with photo verification at sign-off.",
            ))

    elif service_kind == "machine_repair":
        # Q0: geo-intent "near me"
        qa_pairs.append((
            f"Where can I find {name} CNC machine repair near me?",
            f"Midwest CNC Services repairs {name} CNC machines across seven "
            f"Midwest states — Iowa, Illinois, Wisconsin, Minnesota, Nebraska, "
            f"Missouri, and Texas. Field service for drivable Midwest routes; "
            f"ship-in work for the rest. Call 319-610-4341 or request a quote "
            f"at midwestcncservices.com/get-a-quote.",
        ))
        # Q0b: cost intent
        qa_pairs.append((
            f"How much does {name} CNC machine repair cost?",
            f"{name} CNC machine repair cost varies by what's actually broken — "
            f"spindle work, control-board diagnostics, ATC rebuilds, and way "
            f"alignment all scope differently. We don't quote without scoping "
            f"the actual work. Most quotes go out within one business day of "
            f"receiving the model and symptoms.",
        ))
        qa_pairs.append((
            f"What can you fix on a {name} CNC machine?",
            f"Spindle, control, ATC, drive systems, and way alignment are the "
            f"routine work. We diagnose before we quote — sometimes what looks "
            f"like a spindle problem is something cheaper.",
        ))
        if lead_time:
            qa_pairs.append((
                f"How long is a typical {name} machine repair?",
                f"Lead time varies more than spindle work — diagnostic is fast, "
                f"parts and rebuild time depend on the job. {lead_time}",
            ))
        if specifics:
            qa_pairs.append((
                f"Anything unusual about {name} machine repair?",
                f"{specifics}",
            ))
        if is_legacy and parts:
            qa_pairs.append((
                f"Can you still get parts for older {name} machines?",
                f"{parts}",
            ))
        else:
            qa_pairs.append((
                f"Do you service older {name} machines?",
                f"Yes — older {name} platforms are routine work. Bring us the "
                f"machine model and the symptoms; we'll scope what's repairable "
                f"versus what's better replaced.",
            ))

    elif service_kind == "way_covers":
        # Q0: geo-intent "near me"
        qa_pairs.append((
            f"Where can I buy {name} way covers near me?",
            f"Midwest CNC Services builds replacement {name} way covers at our "
            f"Waterloo, Iowa shop and ships to any continental US destination. "
            f"Direct sales to shops across Iowa, Illinois, Wisconsin, Minnesota, "
            f"Nebraska, Missouri, and Texas. Most orders ship in 2–4 weeks. "
            f"Call 319-610-4341 to discuss your machine.",
        ))
        # Q0b: price intent
        qa_pairs.append((
            f"How much do replacement {name} way covers cost?",
            f"Replacement {name} way cover pricing depends on dimensions, style "
            f"(bellows, telescoping steel, or roll-up), and material. We quote "
            f"from your measurements, drawings, or the original cover. Most "
            f"quotes include freight to major Midwest metros and go out within "
            f"one business day.",
        ))
        qa_pairs.append((
            f"What way-cover styles do you build for {name} machines?",
            f"Three styles — bellows, telescoping steel, and roll-up — selected "
            f"based on machine design, debris environment, and clearance constraints. "
            f"We measure from your original or build to drawing.",
        ))
        qa_pairs.append((
            f"How long does a replacement {name} way cover take to build?",
            f"Most way-cover orders ship in 2–4 weeks depending on dimensions and "
            f"material. Rush options are available — call to discuss.",
        ))
        qa_pairs.append((
            f"Can you match an existing {name} way cover I have?",
            f"Yes. Send us the original (or measurements) and we'll build a "
            f"replacement to spec. We routinely match older inventory across the "
            f"full {name} platform range.",
        ))
        qa_pairs.append((
            f"Do you ship {name} way covers nationally?",
            f"Yes. We ship anywhere in the continental US. The build happens at "
            f"our Waterloo, IA shop; freight is included in most quotes for major "
            f"metros.",
        ))

    if not qa_pairs:
        return "", None

    items = []
    for q, a in qa_pairs:
        items.append(
            f'<details class="faq-item">\n'
            f'  <summary>{html.escape(q)}</summary>\n'
            f'  <div class="faq-answer"><p>{html.escape(a)}</p></div>\n'
            f'</details>'
        )

    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in qa_pairs
        ],
    }
    schema_script = (
        '\n<script type="application/ld+json">\n'
        + json.dumps(schema, indent=2, ensure_ascii=False)
        + '\n</script>\n'
    )
    return (
        f'<h2 id="faq">Frequently Asked Questions</h2>\n'
        f'<div class="faq-list">\n'
        + "\n".join(items) + "\n"
        + '</div>\n'
        + schema_script,
        schema,
    )


def write_redirects(brands, outpath, extras=None):
    """Emit public/_redirects covering brand-page URL moves plus any
    `extras` list of (group_title, [(source, destination, code), ...]).
       1. URL relocations (Amada, Trumpf) — old_url → current_url.
       2. /spindles-repair/ duplicates → canonical URLs.
       3. extras — additional groups (e.g. Phase-1 state-page placeholders).
    """
    moves, dups = [], []
    for b in brands:
        if b.get("old_url") and b.get("current_url"):
            moves.append((b["old_url"], b["current_url"]))
    for b in brands:
        old = f"/spindles-repair/{b['slug']}-spindle-repair/"
        new = b.get("current_url")
        if not new or old == new:
            continue
        dups.append((old, new))

    groups = []
    if moves:
        groups.append((
            "Brand page URL relocations — Amada and Trumpf aren't spindle work",
            [(s, d, 301) for s, d in moves],
        ))
    if dups:
        groups.append((
            "/spindles-repair/ URLs duplicate the spindle-grinding / repairs pages",
            [(s, d, 301) for s, d in dups],
        ))
    if extras:
        groups.extend(extras)

    all_rows = [(s, d) for _, rows in groups for (s, d, _) in rows]
    width_src = max((len(s) for s, _ in all_rows), default=60)
    width_dst = max((len(d) for _, d in all_rows), default=55)

    lines = []
    n = 0
    for title, rows in groups:
        if not rows:
            continue
        lines.append(f"# {title}")
        for src, dst, code in rows:
            lines.append(f"{src:<{width_src}}  {dst:<{width_dst}}  {code}")
            n += 1
        lines.append("")

    with open(outpath, "w") as f:
        f.write("\n".join(lines))
    return n


# ---------- CNC spindle page ----------

def build_brand_hero_html(eyebrow_text, h1_text, lede_text, img_path, img_alt):
    """Reusable .brand-hero HTML block used by render_cnc_spindle,
    render_way_covers, render_amada, render_trumpf, and the brand-hub
    renderers. Full-bleed image background, dark gradient overlay,
    centered white text. wrap_into_sections() recognises the leading
    <section class='brand-hero'> tag and wraps it in a hero band."""
    bg_img = (
        f'<img class="brand-hero-bg" src="{img_path}" alt="{html.escape(img_alt)}" loading="eager">\n'
        if img_path else ""
    )
    return (
        f'<section class="brand-hero">\n'
        f'{bg_img}'
        f'  <div class="brand-hero-overlay" aria-hidden="true"></div>\n'
        f'  <div class="brand-hero-content">\n'
        f'    <p class="eyebrow">{html.escape(eyebrow_text)}</p>\n'
        f'    <h1>{html.escape(h1_text)}</h1>\n'
        f'    <p>{lede_text}</p>\n'
        f'    <div class="cta-row">\n'
        f'      <a class="cta-button" href="#quote">Get a Quote</a>\n'
        f'      <a class="cta-phone" href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a>\n'
        f'    </div>\n'
        f'  </div>\n'
        f'</section>\n\n'
    )


def browse_series_section_for_service(brand_slug, brand_display_name, service_kind):
    """Browse-by-Series block for the spindle/way-covers pages. Links
    route to the corresponding repair-section spokes since that's where
    series-specific technical content lives. Returns empty string for
    brands without series structure (Fanuc and the 12 non-hub brands)."""
    hub_data = BRAND_HUB_DATA.get(brand_slug, {})
    series_list = hub_data.get("browse_series", [])
    if not series_list:
        return ""
    # Skip Fanuc — its 'browse_series' field is the brand-cross-link
    # ("Brands that ship Fanuc controls"), not actual machine series.
    if brand_slug == "fanuc":
        return ""
    service_phrase = {
        "spindle":    "spindle work",
        "way_covers": "way covers",
    }.get(service_kind, "service")
    items = "".join(
        f'<li><a href="{u}"><strong>{html.escape(name)}</strong> — {html.escape(desc)}</a></li>'
        for name, u, desc in series_list
    )
    return (
        f'\n<h2 id="browse-by-series">Browse by machine series</h2>\n'
        f'<p>We service {html.escape(brand_display_name)} {service_phrase} '
        f'across the full lineup. Pick your series for platform-specific '
        f'repair and service detail.</p>\n'
        f'<ul class="browse-list">{items}</ul>\n'
    )


def render_cnc_spindle(brand, g, brands_by_slug, brand_index):
    # HUB-AND-SPOKE DISPATCH: any brand with an entry in SPINDLE_HUB_DATA
    # gets the new spindle hub-and-spoke template (Mazak, Haas, DMG Mori,
    # Doosan, Okuma, Fanuc). The remaining 12 brands use the standard
    # template below.
    if brand["slug"] in SPINDLE_HUB_DATA:
        return render_brand_spindle_hub(brand, g, brands_by_slug, brand_index)
    name = brand["brand_display_name"]
    slug = brand["slug"]
    ki = brand["ken_input"]
    is_legacy = "legacy_context" in brand

    failure   = ensure_period(clean_ken(ki["common_failure_mode"]))
    specifics = ensure_period(clean_ken(ki["brand_specifics"]))
    war_story = ensure_period(clean_ken(ki["war_story"]))
    lead_time = ensure_period(clean_ken(ki["typical_lead_time"]))
    lead_pref = lead_short(ki["typical_lead_time"])
    models    = ki["models"]
    parts     = clean_ken(ki.get("parts_situation", ""))

    legacy_tag = " (legacy platform)" if is_legacy else ""
    service_type = f"{name} CNC Spindle Repair and Grinding{legacy_tag}"

    meta_extra = " — keeping legacy machines running" if is_legacy else ""
    meta_desc = (
        f"Expert {name} spindle repair across the Midwest{meta_extra}. "
        f"{lead_pref} on most rebuilds. Experienced field technicians."
    )

    h1_text, eyebrow_text = make_h1_and_eyebrow(brand)
    fm = front_matter(
        brand,
        title=f"{name} Spindle Repair",
        h1=h1_text,
        meta_description=meta_desc,
        service_type=service_type,
        canonical_path=brand["current_url"],
        crumb_middle=("Spindle Grinding", "/spindle-grinding/"),
        crumb_leaf=f"{name} Spindle Repair",
    )

    # Hero image — becomes the .brand-hero background
    img_path, img_alt = hero_image_for(brand, "spindle")

    # Inline model list for the hero (use Ken's exact names).
    if not models:
        model_inline = ""
    elif len(models) == 1:
        model_inline = models[0]
    elif len(models) == 2:
        model_inline = f"{models[0]} and {models[1]}"
    else:
        model_inline = ", ".join(models[:-1]) + f", and {models[-1]}"

    # Hero opener — preserves the failure-mode-specific opening from the
    # previous renderer (Ken-authored brand specificity). Two patterns:
    #   - sentence (verb-led): "What we see most on {Brand} spindles: ..."
    #   - noun phrase: "{Brand} spindles tend to come in with ..."
    first_word = re.match(r"\w+", failure or "")
    is_noun_phrase = (
        first_word is not None
        and first_word.group(0).lower() in NOUN_PHRASE_OPENERS
    )
    if is_noun_phrase:
        cleaned_failure = re.sub(
            r"\s+(?:are|is)\s+common(?=[,.])", "", failure,
        )
        hero_opener = (
            f"{name} spindles tend to come in with "
            f"{_lower_first(cleaned_failure)}"
        )
    else:
        hero_opener = (
            f"What we see most on {name} spindles: {_lower_first(failure)}"
        )

    # Build the lede text (will be inside the .brand-hero white-on-dark)
    lede_text = (
        f"{html.escape(hero_opener)} "
        f"We rebuild, regrind, and rebalance across the {html.escape(name)} platform"
        f"{' &mdash; ' + html.escape(model_inline) if model_inline else ''} &mdash; "
        f"with most jobs running {html.escape(lead_pref)} and field troubleshooting "
        f"where it can save a teardown."
    )
    hero = build_brand_hero_html(
        eyebrow_text or f"{name} Spindle Repair",
        h1_text,
        lede_text,
        img_path, img_alt,
    )
    # Lookup widget + cross-link Browse-by-Series immediately under the hero
    hero += machine_lookup_html()
    hero += browse_series_section_for_service(slug, name, "spindle")

    # Models — fix 9: removed "no model left behind"
    model_bullets = "\n".join(f"- {m}" for m in models) if models else ""
    models_section = (
        f"\n## {name} Models We Support\n\n"
        f"Our {name} work covers the full lineup. "
        f"Whether the job is a precision bearing pack replacement, a full rebuild, "
        f"or a regrind to restore tolerance, we handle:\n\n"
        f"{model_bullets}\n\n"
        f"[Get a Quote](#quote)\n"
    )

    # "How We Approach" — two variants. Default lead-in implies brand-specific
    # complexity worth planning around. Mainstream variant is used where Ken
    # explicitly described the work as standard/straightforward.
    if slug in MAINSTREAM_BRANDS:
        # If the hero already used failure_mode in noun-phrase form (e.g.
        # Fanuc, Amera-Seiki), skip repeating it here — drop the "What we
        # focus on" tail and let brand_specifics carry the section.
        if is_noun_phrase:
            how = (
                f"\n## How We Approach {name} Spindle Work\n\n"
                f"{name} work is one of the more straightforward calls in our "
                f"queue — {_lower_first(specifics)}\n"
            )
        else:
            how = (
                f"\n## How We Approach {name} Spindle Work\n\n"
                f"{name} work is one of the more straightforward calls in our "
                f"queue — {_lower_first(specifics)} "
                f"What we focus on is the spindle condition itself: "
                f"{_lower_first(failure)}\n"
            )
    else:
        # Fix 3: drop the generic "brand-specific factors on {name} drive
        # how we plan the job" lead-in. Lead directly with Ken's specifics.
        # The H2 itself supplies the brand-name context.
        how = (
            f"\n## How We Approach {name} Spindle Work\n\n"
            f"{specifics}\n"
        )

    # Parts sourcing (legacy only). Two patterns:
    #   - Fadal / Hitachi Seiki: legacy_context is a directive ("pages should
    #     mention..."), so don't render it. Use ken_input.parts_situation as
    #     the section body.
    #   - Monarch: legacy_context is written as direct page content. Use it
    #     as the section body when parts_situation isn't present.
    parts_section = ""
    if is_legacy:
        legacy_ctx = brand.get("legacy_context", "")
        is_directive = (
            "pages should" in legacy_ctx.lower()
            or "should mention" in legacy_ctx.lower()
        )
        if parts:
            body = ensure_period(parts)
            intro = (
                f"{name} machines are still cutting daily in Midwest shops, "
                f"but factory support has been gone for years and parts hunts "
                f"can stretch a rebuild's timeline more than the bench work does."
            )
        elif legacy_ctx and not is_directive:
            body = ensure_period(legacy_ctx)
            intro = (
                f"{name} machines are still cutting daily in Midwest shops, "
                f"but factory support has been gone for years."
            )
        else:
            body = (
                "_Parts sourcing details for this brand are still being "
                "confirmed — call us for the latest._"
            )
            intro = (
                f"{name} machines are still cutting daily in Midwest shops, "
                f"but factory support has been gone for years."
            )
        parts_section = (
            f"\n## Parts Sourcing for Legacy {name} Machines\n\n"
            f"{intro} {body}\n"
        )

    # Fix 11: "What We Focus On" section removed — themes will live on the
    # home page hero instead.

    # War story
    war_section = (
        f"\n## A Recent {name} Job\n\n"
        f"A recent example of the kind of work that comes through here: "
        f"{_lower_first(war_story)}\n"
    )

    # Lead time + workflow
    step3 = "We rebuild the spindle, verify balance and runout, and return it ready to run."
    lead_section = (
        f"\n## Lead Time & Process\n\n"
        f"{lead_time} Our three-step workflow keeps it transparent:\n\n"
        f"{workflow_block('rebuild', step3)}\n"
    )

    trust = trust_block(g, brand["page_type"], brand_index, "a new spindle")
    related = related_block_cnc(brand, brands_by_slug)
    cross_links = brand_cross_links_section(brand, brands_by_slug)
    faq_html, faq_schema = brand_faq_section(brand, ki, "spindle")
    # blog_block() removed — was rendering as dashed-border placeholder

    return (
        fm + hero + models_section + how + parts_section + war_section
        + lead_section + "\n" + trust + "\n" + faq_html + "\n"
        + cross_links + "\n" + related + "\n"
    )


def _lower_first(s):
    """Lowercase the first letter so Ken's sentence-start lands inside ours."""
    if not s:
        return s
    return s[0].lower() + s[1:]


# ---------- Amada (press brake / punch) ----------

def render_amada(brand, g, brands_by_slug, brand_index):
    ki = brand["ken_input"]
    failure   = ensure_period(clean_ken(ki["common_failure_mode"]))
    specifics = ensure_period(clean_ken(ki["brand_specifics"]))
    war_story = ensure_period(clean_ken(ki["war_story"]))
    lead_time = ensure_period(clean_ken(ki["typical_lead_time"]))
    lead_pref = lead_short(ki["typical_lead_time"])

    meta_desc = (
        "Amada press brake and turret punch service across the Midwest. "
        "Hydraulic service, ram alignment, backgauge, and tooling troubleshooting."
    )

    h1_text, eyebrow_text = make_h1_and_eyebrow(brand)
    fm = front_matter(
        brand,
        title="Amada Press Brake & Punch Service",
        h1=h1_text,
        meta_description=meta_desc,
        service_type="Amada Press Brake and Turret Punch Service",
        canonical_path=brand["current_url"],
        crumb_middle=("Repairs", "/repairs/"),
        crumb_leaf="Amada Press Brake & Punch Service",
    )

    img_path, img_alt = hero_image_for(brand, "machine_repair")

    first_word = re.match(r"\w+", failure or "")
    is_noun_phrase = (
        first_word is not None
        and first_word.group(0).lower() in NOUN_PHRASE_OPENERS
    )
    if is_noun_phrase:
        cleaned_failure = re.sub(
            r"\s+(?:are|is)\s+common(?=[,.])", "", failure,
        )
        hero_opener = (
            f"Amada {MACHINE_NOUN['press_brake_service']} tend to come in with "
            f"{_lower_first(cleaned_failure)}"
        )
    else:
        hero_opener = (
            f"When your Amada brake or punch goes down, the call we hear most "
            f"is the same: {_lower_first(failure)}"
        )
    lede_text = (
        f"{html.escape(hero_opener)} "
        f"We service press brakes and turret punches across the Amada lineup &mdash; "
        f"ram alignment, hydraulic troubleshooting, backgauge calibration, "
        f"and turret tooling work. Simple alignments turn around quickly; "
        f"major hydraulic work is typically {html.escape(lead_pref)}."
    )
    hero = build_brand_hero_html(
        eyebrow_text or "Amada Press Brake & Punch",
        h1_text,
        lede_text,
        img_path, img_alt,
    )
    hero += machine_lookup_html()

    # No model list for Amada (Ken didn't supply one). Use service scope instead.
    scope = (
        "\n## Amada Service We Provide\n\n"
        "Most of our Amada work falls into a few buckets — ram alignment and "
        "hydraulic service on press brakes, backgauge calibration, and "
        "turret punch tooling and maintenance. We come in on the calls where "
        "a brake or punch isn't producing the part the way it used to.\n\n"
        f"[Get a Quote](#quote)\n"
    )

    how = (
        f"\n## How We Approach Amada Work\n\n"
        f"{specifics}\n"
    )

    war_section = (
        f"\n## A Recent Amada Job\n\n"
        f"A recent example of the kind of work that comes through here: "
        f"{_lower_first(war_story)}\n"
    )

    step3 = "We complete the service, verify the machine is back to spec, and return it ready to run."
    lead_section = (
        f"\n## Lead Time & Process\n\n"
        f"{lead_time} Our three-step workflow keeps it transparent:\n\n"
        f"{workflow_block('job', step3)}\n"
    )

    trust = trust_block(g, brand["page_type"], brand_index, "new equipment")
    related = related_block_alt(brand, brands_by_slug)
    blog = blog_block()

    return fm + hero + scope + how + war_section + lead_section + "\n" + trust + "\n" + related + "\n" + blog


# ---------- Trumpf (laser / punch) ----------

def render_trumpf(brand, g, brands_by_slug, brand_index):
    ki = brand["ken_input"]
    failure   = ensure_period(clean_ken(ki["common_failure_mode"]))
    specifics = ensure_period(clean_ken(ki["brand_specifics"]))
    war_story = ensure_period(clean_ken(ki["war_story"]))
    lead_time = ensure_period(clean_ken(ki["typical_lead_time"]))
    lead_pref = lead_short(ki["typical_lead_time"])

    meta_desc = (
        "Trumpf laser and punch service across the Midwest. Optics, "
        "resonator work on CO2 systems, cooling faults, and punch press maintenance."
    )

    h1_text, eyebrow_text = make_h1_and_eyebrow(brand)
    fm = front_matter(
        brand,
        title="Trumpf Laser & Punch Service",
        h1=h1_text,
        meta_description=meta_desc,
        service_type="Trumpf Laser and Punch Press Service",
        canonical_path=brand["current_url"],
        crumb_middle=("Repairs", "/repairs/"),
        crumb_leaf="Trumpf Laser & Punch Service",
    )

    img_path, img_alt = hero_image_for(brand, "machine_repair")

    first_word = re.match(r"\w+", failure or "")
    is_noun_phrase = (
        first_word is not None
        and first_word.group(0).lower() in NOUN_PHRASE_OPENERS
    )
    if is_noun_phrase:
        cleaned_failure = re.sub(
            r"\s+(?:are|is)\s+common(?=[,.])", "", failure,
        )
        hero_opener = (
            f"Trumpf {MACHINE_NOUN['laser_punch_service']} tend to come in with "
            f"{_lower_first(cleaned_failure)}"
        )
    else:
        hero_opener = (
            f"What we see most on Trumpf systems: {_lower_first(failure)}"
        )

    lede_text = (
        f"{html.escape(hero_opener)} "
        f"We service laser source and optics work on TruLaser and older CO2 "
        f"systems, plus drive and tooling work on TruPunch machines &mdash; "
        f"most jobs run {html.escape(lead_pref)}."
    )
    hero = build_brand_hero_html(
        eyebrow_text or "Trumpf Laser & Punch Service",
        h1_text,
        lede_text,
        img_path, img_alt,
    )
    hero += machine_lookup_html()

    scope = (
        "\n## Trumpf Service We Provide\n\n"
        "Most of our Trumpf work falls into laser source service, resonator "
        "work on older CO2 systems, optics contamination cleanup and "
        "alignment, and punch press drive issues on TruPunch machines. "
        "We come in on the calls where cut quality has fallen off or the "
        "system is faulting on cooling or power.\n\n"
        f"[Get a Quote](#quote)\n"
    )

    how = (
        f"\n## How We Approach Trumpf Work\n\n"
        f"{specifics}\n"
    )

    war_section = (
        f"\n## A Recent Trumpf Job\n\n"
        f"A recent example of the kind of work that comes through here: "
        f"{_lower_first(war_story)}\n"
    )

    step3 = "We complete the work, verify alignment and cut quality, and return the machine ready to run."
    lead_section = (
        f"\n## Lead Time & Process\n\n"
        f"{lead_time} Our three-step workflow keeps it transparent:\n\n"
        f"{workflow_block('job', step3)}\n"
    )

    trust = trust_block(g, brand["page_type"], brand_index, "new laser equipment")
    related = related_block_alt(brand, brands_by_slug)
    blog = blog_block()

    return fm + hero + scope + how + war_section + lead_section + "\n" + trust + "\n" + related + "\n" + blog


# ---------- Hub-and-spoke architecture (Mazak pilot) ----------
# Per docs/cnc-repair-hub-spoke-prompt: each brand repair hub becomes
# a true hub with three browse lenses (series / control / service)
# linking to spoke pages. Pilot on Mazak; propagate to other 5 brands
# after Aaron validates.

_MAZAK_HUB_BROWSE_SERIES = [
    ("Quick Turn / QTN",                    "/repairs/mazak-cnc-machine-repair/quick-turn/",
     "Horizontal turning. QT-8 through QTN-450, MS/MSY twin-spindle variants, current Compact/Smart/Primos/Ez/Ultra."),
    ("Integrex",                            "/repairs/mazak-cnc-machine-repair/integrex/",
     "Mill-turn multitasking. 100/200/300/400 i-series, e-500H through e-1850V, j and i-V and i-H."),
    ("Variaxis",                            "/repairs/mazak-cnc-machine-repair/variaxis/",
     "5-axis trunnion verticals. i-300 through i-800, J-500/J-600, C-600, and legacy 500/630/730."),
    ("Vertical Machining Centers (VTC + VCN)", "/repairs/mazak-cnc-machine-repair/vertical-machining-centers/",
     "Production verticals, mid-size to long-bed. VTC-16 through VTC-800, VCN-410 through VCN-700, FJV and AJV."),
    ("HCN Horizontals",                     "/repairs/mazak-cnc-machine-repair/hcn-horizontal/",
     "Pallet-changer horizontals for production. HCN-4000 through HCN-10800, plus legacy PFH and H-series."),
    ("Turning Legacy",                      "/repairs/mazak-cnc-machine-repair/turning-legacy/",
     "Slant Turn, Multiplex, Megaturn, HQR. Older platforms still in service — M-Plus and Fusion 640 controls."),
]

_MAZAK_HUB_BROWSE_CONTROL = [
    ("Mazatrol Legacy",   "/repairs/mazak-cnc-machine-repair/mazatrol-legacy/",
     "M-2, M-32, M-Plus, Fusion 640 — roughly 1981-2005. Battery loss, CRT failures, MDI board, floppy and PCMCIA obsolescence."),
    ("Mazatrol Matrix",   "/repairs/mazak-cnc-machine-repair/mazatrol-matrix/",
     "Matrix and Matrix 2 — roughly 2005-2013. HDD failure (SSD upgrades routine), CF card corruption, MMC board, touchscreen drift."),
    ("Mazatrol Smooth",   "/repairs/mazak-cnc-machine-repair/smooth-control/",
     "SmoothX, SmoothG, SmoothAi — 2013-present. Networking, MTConnect setup, parameter backup, USB media handling."),
]

# Expanded FAQ for the Mazak hub (≥5 Qs including the prompt-specified
# legacy-control / which-series / SSD-upgrade questions).
_MAZAK_HUB_FAQ = [
    ("What can you fix on a Mazak CNC machine?",
     "Spindle, control, ATC, drive systems, and way alignment are the routine work. We diagnose before we quote — sometimes what looks like a spindle problem is something cheaper."),
    ("Which Mazak series do you see most often?",
     "Quick Turn and Quick Turn Nexus lathes plus VTC and VCN verticals are the most common. Integrex multitasking work tends to be higher-value but lower frequency. HCN horizontals come in for pallet-changer faults and B-axis indexer wear."),
    ("Do you service older Mazak machines with Mazatrol M-Plus or Fusion 640 controls?",
     "Yes. Legacy Mazatrol controls — M-2, M-32, M-Plus, and Fusion 640 — are routine work. The common issues are dead memory batteries, CRT failures (LCD retrofits are available), keyboard membrane failures, and floppy or PCMCIA media obsolescence. Board-level repair runs through remanufacturing specialists where OEM parts have gone out of stock."),
    ("Can you upgrade a Mazatrol Matrix to an SSD?",
     "Yes — SSD upgrades on Matrix and Matrix 2 controls are one of the highest-ROI service items on older Mazak machines. Replacing the original spinning HDD eliminates the single most common control failure point on that generation and recovers boot and program-load times."),
    ("How long does a typical Mazak machine repair take?",
     "Lead time on machine repair depends on what's wrong. Diagnostic is fast; parts and rebuild time vary by the job. 3 to 5 weeks is realistic on most jobs depending on cartridge damage and OEM bearing or board availability."),
    ("Do you service Mazak machines outside Iowa?",
     "Yes. We service shops across Iowa, Illinois, Wisconsin, Minnesota, Nebraska, Missouri, and Texas. Field service is most economical in Iowa and adjacent states; longer-haul jobs typically run ship-in to our Waterloo facility."),
]

# Per-spoke content. Each spoke renders an independent page nested
# under the Mazak hub. Models lists come from machines.json; here we
# carry the prose (intro, failures, controls used, lead-time framing).
_MAZAK_SERIES_SPOKES = {
    "quick-turn": {
        "title":   "Mazak Quick Turn Repair & Service",
        "slug":    "mazak-quick-turn",
        "subtitle":"Quick Turn and Quick Turn Nexus",
        "url":     "/repairs/mazak-cnc-machine-repair/quick-turn/",
        "intro":   "Quick Turn and Quick Turn Nexus lathes are the highest-volume Mazak platform we see. The line spans entry QT-8 chuckers through QTN-450 large-bore turning, plus the MS and MSY twin-spindle variants and the current Compact, Smart, Primos, Ez, and Ultra families. We work on all of them — turret indexing, sub-spindle alignment, Y-axis backlash, tailstock quill wear, and chuck cylinder leaks are routine.",
        "failures": [
            "Turret indexing faults — solenoid, indexer pawl, or position-encoder issues.",
            "Sub-spindle alignment drift on MS and MSY twin-spindle machines.",
            "Y-axis backlash from ballscrew wear or backlash-comp drift after a crash.",
            "Tailstock quill wear and hydraulic pressure loss.",
            "Chuck cylinder leaks and draw-tube issues on high-cycle bar work.",
        ],
        "controls_paragraph": "Older Quick Turn machines ran the Mazatrol Fusion 640T control (see our [Mazatrol Legacy spoke](/repairs/mazak-cnc-machine-repair/mazatrol-legacy/) for memory, CRT, and PCMCIA obsolescence). Mid-2000s through early-2010s Quick Turn Nexus shipped on [Matrix and Matrix 2](/repairs/mazak-cnc-machine-repair/mazatrol-matrix/) — HDD failures and SSD upgrades are the most common service item on that generation. Current Compact, Smart, and Ultra ship on [SmoothG and SmoothAi](/repairs/mazak-cnc-machine-repair/smooth-control/).",
        "siblings": [
            ("Integrex",   "/repairs/mazak-cnc-machine-repair/integrex/"),
            ("Turning Legacy", "/repairs/mazak-cnc-machine-repair/turning-legacy/"),
        ],
    },
    "integrex": {
        "title":   "Mazak Integrex Repair & Service",
        "slug":    "mazak-integrex",
        "subtitle":"Mill-turn multitasking",
        "url":     "/repairs/mazak-cnc-machine-repair/integrex/",
        "intro":   "The Integrex line is Mazak's mill-turn multitasking platform — Integrex 100 through 400 (with S, ST, SY, IV, V, e, i, j, and i-H variants), the e-500H through e-1850V/10 family, plus the compact Integrex j and the vertical i-V. Multitasking tolerances mean spindle and B-axis work needs more careful alignment than on a straight VMC or lathe. We do the work and verify it back to spec.",
        "failures": [
            "B-axis milling spindle bearing wear, particularly on i-series and i-H models.",
            "Lower turret faults on e-series machines.",
            "ATC chain or ATC arm faults on i-H horizontals.",
            "Sub-spindle synchronization drift on multi-tasking jobs.",
            "Hydraulic counterbalance system leaks on larger e-series.",
        ],
        "controls_paragraph": "Original Integrex i-series machines shipped with [Mazatrol Matrix](/repairs/mazak-cnc-machine-repair/mazatrol-matrix/); current i-H, e-V, and i-V ship on [SmoothX](/repairs/mazak-cnc-machine-repair/smooth-control/). Older Integrex 100/200 may still be running [Mazatrol legacy controls](/repairs/mazak-cnc-machine-repair/mazatrol-legacy/) — those are still serviceable but the parts situation is increasingly aftermarket-only.",
        "siblings": [
            ("Variaxis",   "/repairs/mazak-cnc-machine-repair/variaxis/"),
            ("Quick Turn", "/repairs/mazak-cnc-machine-repair/quick-turn/"),
        ],
    },
    "variaxis": {
        "title":   "Mazak Variaxis Repair & Service",
        "slug":    "mazak-variaxis",
        "subtitle":"5-axis trunnion verticals",
        "url":     "/repairs/mazak-cnc-machine-repair/variaxis/",
        "intro":   "Variaxis covers Mazak's 5-axis trunnion-table verticals — i-300 through i-800 plus the J-series and C-series, and the older 500/630/730 platforms. The work is precision 5-axis: aerospace, mold and die, complex part work. RTCP drift after a crash, trunnion bearings, and C-axis brake faults are the common entry points.",
        "failures": [
            "Trunnion A-axis backlash and zero-point drift after a crash.",
            "C-axis brake faults — hydraulic pressure, brake disc wear, or clamp solenoid.",
            "Swarf and coolant intrusion at trunnion bearings on heavy-coolant production work.",
            "RTCP and kinematic drift after spindle or trunnion work — requires re-calibration.",
            "5-axis spindle bearing failure on higher-RPM i-series.",
        ],
        "controls_paragraph": "Variaxis i-series ships on [SmoothX](/repairs/mazak-cnc-machine-repair/smooth-control/); legacy 500/630/730 was [Mazatrol Matrix](/repairs/mazak-cnc-machine-repair/mazatrol-matrix/) or earlier. Variaxis kinematic alignment after any trunnion work is brand-specific — we run the calibration as part of the rebuild rather than handing it back for the shop to fix.",
        "siblings": [
            ("Integrex",   "/repairs/mazak-cnc-machine-repair/integrex/"),
            ("Vertical Machining Centers", "/repairs/mazak-cnc-machine-repair/vertical-machining-centers/"),
        ],
    },
    "vertical-machining-centers": {
        "title":   "Mazak Vertical Machining Center Repair (VTC + VCN)",
        "slug":    "mazak-vertical-machining-centers",
        "subtitle":"Production verticals",
        "url":     "/repairs/mazak-cnc-machine-repair/vertical-machining-centers/",
        "intro":   "VTC and VCN are Mazak's production verticals — VTC-16 through VTC-800 (the long-bed VTCs see the most wear), VCN-410A through VCN-700 (high-RPM spindle work), plus the FJV and AJV gantry platforms. These are the workhorse machines on most Mazak shop floors and the most common reason a shop calls.",
        "failures": [
            "ATC drum indexing faults — solenoid wear, indexer pawl, position sensor.",
            "Ballscrew wear on long-bed VTC-800s with heavy axial production.",
            "High-speed spindle bearing failure on VCN-510C and VCN-530C with high-coolant work.",
            "Way cover damage from chip intrusion or crash.",
            "Z-axis ballnut and bearing wear from heavy production.",
        ],
        "controls_paragraph": "Older VTC machines run [Mazatrol legacy controls](/repairs/mazak-cnc-machine-repair/mazatrol-legacy/); mid-2000s VCN and VTC ran [Matrix](/repairs/mazak-cnc-machine-repair/mazatrol-matrix/); current VCN-510C, VCN-530C, VCN-700 and VCN-Compact ship on [SmoothG](/repairs/mazak-cnc-machine-repair/smooth-control/). VTC-800 with SmoothX is the long-bed current platform.",
        "siblings": [
            ("HCN Horizontals", "/repairs/mazak-cnc-machine-repair/hcn-horizontal/"),
            ("Variaxis",        "/repairs/mazak-cnc-machine-repair/variaxis/"),
        ],
    },
    "hcn-horizontal": {
        "title":   "Mazak HCN Horizontal Machining Center Repair",
        "slug":    "mazak-hcn-horizontal",
        "subtitle":"Pallet-changer horizontals",
        "url":     "/repairs/mazak-cnc-machine-repair/hcn-horizontal/",
        "intro":   "HCN horizontals — HCN-4000 through HCN-10800, plus the legacy PFH and H-series — are production horizontals built around pallet changers and B-axis indexing. The pallet changer and B-axis are where most service calls originate; the rest is conventional horizontal machine work.",
        "failures": [
            "Pallet changer faults — clamp pressure loss, pallet seat alignment, position-sensor issues.",
            "B-axis indexer wear and backlash, especially on heavy-cut production.",
            "Coolant intrusion at the pallet seal — common on high-coolant work.",
            "Chip auger jams and chip evacuation problems.",
            "Hydraulic clamp pressure loss on the workpiece clamping system.",
        ],
        "controls_paragraph": "Mid-2000s HCN runs [Matrix](/repairs/mazak-cnc-machine-repair/mazatrol-matrix/); current HCN-8800 and HCN-10800 ship on [SmoothX](/repairs/mazak-cnc-machine-repair/smooth-control/). Legacy PFH and H-series typically run [Mazatrol Legacy](/repairs/mazak-cnc-machine-repair/mazatrol-legacy/) controls and the parts situation is increasingly aftermarket.",
        "siblings": [
            ("Vertical Machining Centers", "/repairs/mazak-cnc-machine-repair/vertical-machining-centers/"),
            ("Integrex",                   "/repairs/mazak-cnc-machine-repair/integrex/"),
        ],
    },
    "turning-legacy": {
        "title":   "Mazak Turning Legacy Repair",
        "slug":    "mazak-turning-legacy",
        "subtitle":"Slant Turn, Multiplex, Megaturn, HQR, Powermaster",
        "url":     "/repairs/mazak-cnc-machine-repair/turning-legacy/",
        "intro":   "Mazak's turning legacy platforms — Slant Turn 15/18/20 and Slant Turn Nexus, Multiplex 6000 through 6300, Megaturn vertical turning, HQR-150/200/250, and the Powermaster series — are still running on shop floors across the Midwest. The platforms are mechanically sound; what brings them in is control obsolescence and drive-side issues more often than spindle work.",
        "failures": [
            "M-Plus and Fusion 640 control board faults — board-level repair or remanufacturing where parts allow.",
            "Drive obsolescence — older servo amplifiers going scarce.",
            "Slant-bed way wear from years of production.",
            "Tailstock and turret indexing issues on Multiplex twin-turret platforms.",
            "Hydraulic system pressure loss on the older Megaturn vertical platforms.",
        ],
        "controls_paragraph": "These platforms ran [Mazatrol legacy controls](/repairs/mazak-cnc-machine-repair/mazatrol-legacy/) — M-Plus and Fusion 640 are the most common. Multiplex 6100 and later ran [Matrix](/repairs/mazak-cnc-machine-repair/mazatrol-matrix/). For the legacy generation, expect aftermarket-only parts on most boards and OEM-discontinued status on some servo amplifiers.",
        "siblings": [
            ("Quick Turn",                 "/repairs/mazak-cnc-machine-repair/quick-turn/"),
            ("Vertical Machining Centers", "/repairs/mazak-cnc-machine-repair/vertical-machining-centers/"),
        ],
    },
}

_MAZAK_CONTROL_SPOKES = {
    "mazatrol-legacy": {
        "title":   "Mazatrol Legacy Control Repair",
        "slug":    "mazak-mazatrol-legacy",
        "subtitle":"Mazatrol M-2, M-32, M-Plus, Fusion 640",
        "url":     "/repairs/mazak-cnc-machine-repair/mazatrol-legacy/",
        "era":     "Roughly 1981 through 2005",
        "intro":   "Mazatrol legacy is the family of pre-Matrix controls — M-2, M-32, M-Plus, and Fusion 640 — that shipped on Mazak lathes and verticals from the early 1980s through roughly 2005. In 2026 these controls are at the obsolescence stage: most boards have gone out of OEM stock, parts come through remanufacturing specialists, and the most common service work is preventive (battery replacement, media migration) rather than reactive repair.",
        "machines_paragraph": "Mazatrol legacy controls shipped on older [Quick Turn](/repairs/mazak-cnc-machine-repair/quick-turn/) lathes (pre-Nexus), [Turning Legacy](/repairs/mazak-cnc-machine-repair/turning-legacy/) platforms (Slant Turn, Multiplex, Megaturn, HQR), [Vertical Machining Centers](/repairs/mazak-cnc-machine-repair/vertical-machining-centers/) (VTC and FJV legacy), and the [HCN horizontals'](/repairs/mazak-cnc-machine-repair/hcn-horizontal/) PFH and H-series predecessors. If your machine predates 2005 and runs Mazatrol, it's almost certainly on this generation.",
        "failures": [
            "Dead memory battery — the most common single failure mode. Memory loss takes parameters and offsets with it; battery replacement on a powered-up control is the prevention.",
            "CRT failure — original tubes are mostly out of service. LCD retrofit kits are available and routine.",
            "Keyboard membrane failure — high-cycle keys go intermittent or stop responding.",
            "MDI board faults — generally aftermarket replacement at this point.",
            "Floppy and PCMCIA media obsolescence — physical drives still work but media sourcing and reader reliability are the issue. USB or CF migration is the typical fix.",
        ],
        "parts_paragraph": "Parts on legacy Mazatrol are increasingly aftermarket-only. Remanufactured boards through specialists are the path on most board-level work. We can scope what's repairable in-place versus what needs board exchange — the worst answer is sending out a board nobody is remanufacturing anymore, so we check parts availability before we quote.",
        "recovery_paragraph": "Battery, memory, and parameter recovery on legacy Mazatrol comes up regularly. The process is: capture parameters and offsets via the existing media path before any battery work; replace the battery on a powered control where possible; restore parameters if memory was lost. Floppy and PCMCIA migration to USB or CF media is part of the same conversation — we'll scope it together so we're not opening the control twice.",
        "siblings": [
            ("Mazatrol Matrix",  "/repairs/mazak-cnc-machine-repair/mazatrol-matrix/"),
            ("Mazatrol Smooth",  "/repairs/mazak-cnc-machine-repair/smooth-control/"),
        ],
    },
    "mazatrol-matrix": {
        "title":   "Mazatrol Matrix Control Repair (Matrix / Matrix 2)",
        "slug":    "mazak-mazatrol-matrix",
        "subtitle":"Mazatrol Matrix and Matrix 2",
        "url":     "/repairs/mazak-cnc-machine-repair/mazatrol-matrix/",
        "era":     "Roughly 2005 through 2013",
        "intro":   "Matrix and Matrix 2 are the Mazatrol generation that bridged Fusion 640 and SmoothX. They shipped on Mazak's mid-2000s through early-2010s production — Quick Turn Nexus, Integrex i-series, Variaxis 500/630/730, mid-life VCN and VTC, and HCN-4000 through HCN-6000. Matrix 2 is still well supported; Matrix-1 boards are starting to go scarce. The HDD-to-SSD upgrade is one of the highest-ROI service items on this generation.",
        "machines_paragraph": "Matrix controls shipped on [Quick Turn Nexus](/repairs/mazak-cnc-machine-repair/quick-turn/) (QTN-100 through QTN-450), [Integrex](/repairs/mazak-cnc-machine-repair/integrex/) i-series originals, [Vertical Machining Centers](/repairs/mazak-cnc-machine-repair/vertical-machining-centers/) (VTC-200 through VTC-800, VCN-410 through VCN-530), [HCN horizontals](/repairs/mazak-cnc-machine-repair/hcn-horizontal/) (HCN-4000 through HCN-6000), and the [Multiplex](/repairs/mazak-cnc-machine-repair/turning-legacy/) 6100 generation.",
        "failures": [
            "Hard drive failure — the most common single issue on this generation. SSD upgrades are routine and prevent recurrence.",
            "CF card corruption on Matrix-1 (memory card slot is the primary boot media on some configurations).",
            "MMC board faults — control board sees enough thermal cycling to fail over a decade of production.",
            "Touchscreen drift and calibration loss.",
            "Fan failure and resulting thermal damage to boards if not caught.",
        ],
        "parts_paragraph": "Matrix-2 boards are still actively supported through OEM and authorized channels. Matrix-1 boards are heading the same direction as Fusion 640 — moving toward aftermarket and remanufactured-only over the next few years. We check availability before quoting board-level work.",
        "recovery_paragraph": "SSD upgrades on Matrix and Matrix 2 are the highest-value preventive service item on this generation. Replacing the original spinning HDD eliminates the single most common control failure point, recovers boot and program-load time, and reduces the thermal load that contributes to fan and MMC board failures. Backup parameters and programs before swapping; we run the swap and verify the restore as a single visit.",
        "siblings": [
            ("Mazatrol Legacy",  "/repairs/mazak-cnc-machine-repair/mazatrol-legacy/"),
            ("Mazatrol Smooth",  "/repairs/mazak-cnc-machine-repair/smooth-control/"),
        ],
    },
    "smooth-control": {
        "title":   "Mazatrol Smooth Control Repair",
        "slug":    "mazak-smooth-control",
        "subtitle":"Mazatrol SmoothX, SmoothG, SmoothAi",
        "url":     "/repairs/mazak-cnc-machine-repair/smooth-control/",
        "era":     "2013 through present",
        "intro":   "Smooth is Mazatrol's current generation — SmoothX on high-end multitasking and 5-axis platforms, SmoothG on production lathes and VMCs, SmoothAi on the latest Ultra and current-flagship machines. The Smooth generation is recent enough that hardware failure is uncommon; most service work is integration, networking, MTConnect setup, parameter backup, and USB media handling rather than reactive repair.",
        "machines_paragraph": "Smooth ships on current [Integrex](/repairs/mazak-cnc-machine-repair/integrex/) (i-H, i-V, e-V/10), current [Variaxis](/repairs/mazak-cnc-machine-repair/variaxis/) i-series, [Vertical Machining Centers](/repairs/mazak-cnc-machine-repair/vertical-machining-centers/) (VTC-800 and VCN current), current [HCN horizontals](/repairs/mazak-cnc-machine-repair/hcn-horizontal/) (HCN-8800, HCN-10800), and current [Quick Turn](/repairs/mazak-cnc-machine-repair/quick-turn/) Compact, Smart, Primos, Ez, and Ultra.",
        "failures": [
            "Networking and Ethernet configuration drift after a shop network change.",
            "MTConnect setup and parameter mapping when integrating with shop-floor monitoring.",
            "USB media reliability — periodic clean and verify on the boot media path.",
            "Touchscreen calibration drift on heavily-used panels.",
            "Parameter backup discipline — Smooth controls store more parameters than legacy generations, and a clean backup process matters.",
        ],
        "parts_paragraph": "Smooth-generation parts are fully supported through OEM channels. The work here is integration and configuration more than parts.",
        "recovery_paragraph": "Smooth controls support a clean parameter backup workflow over network or USB. The discipline is doing the backup before any service work, not after. We document the parameter set at the start of every service visit and verify the restore at sign-off.",
        "siblings": [
            ("Mazatrol Matrix",  "/repairs/mazak-cnc-machine-repair/mazatrol-matrix/"),
            ("Mazatrol Legacy",  "/repairs/mazak-cnc-machine-repair/mazatrol-legacy/"),
        ],
    },
}


_HAAS_SERIES_SPOKES = {
    "vf-series": {
        "title":   "Haas VF Series Repair & Service",
        "slug":    "haas-vf-series",
        "subtitle":"VF Series Vertical Mills",
        "url":     "/repairs/haas-cnc-machine-repair/vf-series/",
        "intro":   "The VF series is the workhorse on most Haas shop floors — VF-1 through VF-12, plus the YT extended-Y variants, the SS super-speed builds, and the VFEXT extended-Z platforms. The series has been continuously refined since the early 1990s, so we see everything from Haas Classic Control machines still in production to the latest NGC builds.",
        "failures": [
            "ATC carousel faults — solenoid wear, indexer pawl, position-sensor issues.",
            "Spindle bearing failure on SS (Super-Speed) variants from high-RPM production.",
            "Way cover damage from chip intrusion or crash.",
            "Z-axis ballscrew wear on heavy-use VF-4 and larger.",
            "MOCON board failures on Classic-control vintage machines.",
        ],
        "controls_paragraph": "Older VF machines run [Haas Classic Control](/repairs/haas-cnc-machine-repair/haas-classic-control/) (pre-2014) — keypad, monitor, MOCON board, and drive faults are the routine work. 2014-and-later VF builds ship on [Haas Next Generation Control (NGC)](/repairs/haas-cnc-machine-repair/haas-ngc/) — service work is mostly SSD upgrades, USB media, and networking.",
        "siblings": [
            ("ST Series",   "/repairs/haas-cnc-machine-repair/st-series/"),
            ("UMC Series",  "/repairs/haas-cnc-machine-repair/umc-series/"),
        ],
    },
    "st-series": {
        "title":   "Haas ST Series Lathe Repair & Service",
        "slug":    "haas-st-series",
        "subtitle":"ST Series Lathes",
        "url":     "/repairs/haas-cnc-machine-repair/st-series/",
        "intro":   "The ST series is Haas's production lathe lineup — ST-10 through ST-55, plus the SSY Y-axis variants and the DS-30 dual-spindle. The platform spans roughly fifteen years of Haas turning evolution, so we see Classic-control vintage machines alongside current NGC builds.",
        "failures": [
            "Turret indexing faults — solenoid, indexer pawl, or position-encoder.",
            "Tailstock issues — quill wear and hydraulic pressure loss.",
            "Chuck cylinder leaks on high-cycle bar work.",
            "Spindle bearing wear on high-use ST-10 and ST-20 chuckers.",
            "Sub-spindle alignment drift on DS-30 dual-spindle builds.",
        ],
        "controls_paragraph": "Older ST machines run [Haas Classic Control](/repairs/haas-cnc-machine-repair/haas-classic-control/); current ST-10 through ST-55 ship on [NGC](/repairs/haas-cnc-machine-repair/haas-ngc/). DS-30 builds are typically on NGC by now; older ones on Classic.",
        "siblings": [
            ("VF Series",       "/repairs/haas-cnc-machine-repair/vf-series/"),
            ("Toolroom Lathes", "/repairs/haas-cnc-machine-repair/toolroom-lathes/"),
        ],
    },
    "umc-series": {
        "title":   "Haas UMC Series Repair & Service",
        "slug":    "haas-umc-series",
        "subtitle":"UMC Series Universal 5-Axis",
        "url":     "/repairs/haas-cnc-machine-repair/umc-series/",
        "intro":   "UMC is Haas's universal 5-axis platform — trunnion-table machines from UMC-350 compact through UMC-1600 large-envelope, plus the SS super-speed builds. Most UMC work centers on the 5-axis side: trunnion calibration, A/C-axis encoders, and RTCP setup are where calls come from.",
        "failures": [
            "Trunnion calibration drift after a crash — A and C axis zero-point recovery.",
            "A/C-axis encoder faults — contamination, signal loss, or backlash drift.",
            "RTCP setup drift — kinematic re-calibration after spindle or trunnion work.",
            "Swarf and coolant intrusion at the trunnion on heavy-coolant production.",
            "Spindle bearing failure on SS variants from high-RPM work.",
        ],
        "controls_paragraph": "All UMC machines ship on [Haas NGC](/repairs/haas-cnc-machine-repair/haas-ngc/) — Classic Control never made it to the UMC line. NGC service work on UMCs is mostly kinematic calibration and the occasional SSD or networking job.",
        "siblings": [
            ("VF Series",  "/repairs/haas-cnc-machine-repair/vf-series/"),
            ("EC Series",  "/repairs/haas-cnc-machine-repair/ec-series/"),
        ],
    },
    "ec-series": {
        "title":   "Haas EC Series Horizontal Repair & Service",
        "slug":    "haas-ec-series",
        "subtitle":"EC Series Horizontals",
        "url":     "/repairs/haas-cnc-machine-repair/ec-series/",
        "intro":   "EC is Haas's horizontal machining lineup — EC-300 through EC-3000 production horizontals, plus the PP (pallet-pool) builds and the 4-axis variants. The series is built around pallet-changer reliability and B-axis indexing; that's where most service calls come from.",
        "failures": [
            "Pallet changer faults on PP units — clamp pressure, pallet seat alignment, position sensors.",
            "B-axis indexer wear from heavy-cut production.",
            "Coolant intrusion at the pallet seal on high-coolant work.",
            "Chip auger jams and chip evacuation problems.",
            "Hydraulic clamp pressure loss on the workpiece clamping system.",
        ],
        "controls_paragraph": "Older EC machines run [Haas Classic Control](/repairs/haas-cnc-machine-repair/haas-classic-control/); current EC-500 and EC-550 plus the EC-1600/2000/3000 large builds ship on [NGC](/repairs/haas-cnc-machine-repair/haas-ngc/).",
        "siblings": [
            ("VF Series",   "/repairs/haas-cnc-machine-repair/vf-series/"),
            ("UMC Series",  "/repairs/haas-cnc-machine-repair/umc-series/"),
        ],
    },
    "mini-mill-toolroom": {
        "title":   "Haas Mini Mill, Toolroom, DT, DM, and VM Repair",
        "slug":    "haas-mini-mill-toolroom",
        "subtitle":"Mini Mill / Toolroom / DT / DM / VM",
        "url":     "/repairs/haas-cnc-machine-repair/mini-mill-toolroom/",
        "intro":   "The compact and toolroom families — Mini Mill, Super Mini Mill, the TM Toolroom Mill series, the DT and DM drill-tap centers, and the VM mold-machine line — share many components but see different wear patterns based on use. DTs see high-cycle ATC wear; Mini Mills see ATC reliability issues; older Toolroom machines see control-panel work.",
        "failures": [
            "ATC reliability on Mini Mills — solenoid, pawl, and carousel-position wear.",
            "Spindle bearing failure on DT (drill/tap) machines from high-cycle production.",
            "Way cover failure on older TM toolroom mills.",
            "Control panel issues on older Toolroom builds.",
            "Ballscrew and bearing wear on DM mold-machine work.",
        ],
        "controls_paragraph": "Most of this family ran [Haas Classic Control](/repairs/haas-cnc-machine-repair/haas-classic-control/) through 2014; newer DT, DM, and Super Mini Mill 2 builds ship on [NGC](/repairs/haas-cnc-machine-repair/haas-ngc/). TM toolroom mills with Classic-vintage panels are common candidates for control-side service.",
        "siblings": [
            ("VF Series",       "/repairs/haas-cnc-machine-repair/vf-series/"),
            ("Toolroom Lathes", "/repairs/haas-cnc-machine-repair/toolroom-lathes/"),
        ],
    },
    "toolroom-lathes": {
        "title":   "Haas Toolroom Lathe Repair & Service",
        "slug":    "haas-toolroom-lathes",
        "subtitle":"TL and CL Toolroom Lathes",
        "url":     "/repairs/haas-cnc-machine-repair/toolroom-lathes/",
        "intro":   "Toolroom lathes — TL-1 through TL-4 and the CL-1 — bridge manual lathe operation and CNC. They're production-capable but used differently than the ST series, and the wear patterns reflect that: tailstock alignment, manual-mode reliability, and ballscrew wear are the routine work.",
        "failures": [
            "Tailstock alignment drift on heavily used machines.",
            "Manual-mode reliability issues — handwheel encoders, mode-select switch wear.",
            "Ballscrew wear from production-style cycles on a toolroom platform.",
            "Spindle bearing wear on long-running shop-floor TL-2 and TL-3 units.",
        ],
        "controls_paragraph": "TL machines ran [Haas Classic Control](/repairs/haas-cnc-machine-repair/haas-classic-control/) through 2014; current TL and CL-1 ship on [NGC](/repairs/haas-cnc-machine-repair/haas-ngc/).",
        "siblings": [
            ("ST Series",  "/repairs/haas-cnc-machine-repair/st-series/"),
            ("VF Series",  "/repairs/haas-cnc-machine-repair/vf-series/"),
        ],
    },
}
_HAAS_CONTROL_SPOKES = {
    "haas-classic-control": {
        "title":   "Haas Classic Control Repair (pre-NGC)",
        "slug":    "haas-haas-classic-control",
        "subtitle":"Haas Classic Control",
        "url":     "/repairs/haas-cnc-machine-repair/haas-classic-control/",
        "era":     "Through roughly 2014",
        "intro":   "Haas Classic Control is the family of pre-NGC controls that shipped on Haas machines through roughly 2014. Most of the early-2000s through early-2010s Haas fleet on Midwest shop floors is on Classic. The most common service work is keypad, monitor (CRT and early LCD), MOCON board, drive system, and memory battery.",
        "machines_paragraph": "Classic Control shipped on most of the Haas fleet through 2014 — the original [VF Series](/repairs/haas-cnc-machine-repair/vf-series/) (VF-1 through VF-12), [ST Series](/repairs/haas-cnc-machine-repair/st-series/) lathes, [EC Series](/repairs/haas-cnc-machine-repair/ec-series/) horizontals, original [Mini Mill, TM Toolroom, and DT/DM](/repairs/haas-cnc-machine-repair/mini-mill-toolroom/) machines, and the [TL Toolroom Lathes](/repairs/haas-cnc-machine-repair/toolroom-lathes/). UMC machines never shipped on Classic.",
        "failures": [
            "Keypad failure — high-cycle keys go intermittent or stop responding.",
            "Monitor failure — original CRTs are mostly out of service. Early LCDs are now hitting end-of-life too.",
            "MOCON board faults — the motion-control board sees enough thermal cycling to fail over a decade of production.",
            "Drive amplifier faults on heavier production work.",
            "Memory battery loss — parameters and offsets vanish if the battery dies on a powered-down control.",
        ],
        "parts_paragraph": "Haas Classic parts are still available through Haas channels for most board-level items, but the supply chain is thinning as NGC matures. Aftermarket replacement keypads and LCD retrofits are widely available. We check parts availability before quoting.",
        "recovery_paragraph": "Battery and parameter recovery on Classic Control is the standard process: capture parameters and offsets before any battery work, replace the battery on a powered control where possible, restore parameters if memory was lost. For machines being upgraded to NGC, we coordinate parameter migration as part of the conversation.",
        "siblings": [
            ("Haas Next Generation Control (NGC)", "/repairs/haas-cnc-machine-repair/haas-ngc/"),
        ],
    },
    "haas-ngc": {
        "title":   "Haas Next Generation Control (NGC) Repair",
        "slug":    "haas-haas-ngc",
        "subtitle":"Haas NGC",
        "url":     "/repairs/haas-cnc-machine-repair/haas-ngc/",
        "era":     "2014 to present",
        "intro":   "NGC is Haas's current control generation, introduced in 2014. It's mature enough now that we see real service work — SSD upgrades on the early units, USB media issues, networking and MyHaas integration, parameter backup discipline. Hardware failures are less common than on Classic, but the integration and configuration work is steady.",
        "machines_paragraph": "NGC ships on every current Haas machine — [VF Series](/repairs/haas-cnc-machine-repair/vf-series/), [ST Series](/repairs/haas-cnc-machine-repair/st-series/), all [UMC](/repairs/haas-cnc-machine-repair/umc-series/) 5-axis machines, [EC Series](/repairs/haas-cnc-machine-repair/ec-series/) horizontals, current [Mini Mill, DT, DM](/repairs/haas-cnc-machine-repair/mini-mill-toolroom/) and the [TL/CL Toolroom Lathes](/repairs/haas-cnc-machine-repair/toolroom-lathes/).",
        "failures": [
            "SSD upgrade work on early NGC builds — replacing the original drives recovers boot and program-load times.",
            "USB media reliability — boot-media path cleaning and verification.",
            "Networking configuration drift after a shop network change.",
            "MyHaas integration setup for shop-floor monitoring.",
            "Parameter backup discipline — clean backup before any service work.",
        ],
        "parts_paragraph": "NGC parts are fully supported through Haas channels. The work is more configuration and integration than reactive parts swapping.",
        "recovery_paragraph": "NGC supports a clean parameter backup workflow over network and USB. The discipline is doing the backup before any service work, not after. We document the parameter set at the start of every service visit and verify the restore at sign-off.",
        "siblings": [
            ("Haas Classic Control", "/repairs/haas-cnc-machine-repair/haas-classic-control/"),
        ],
    },
}

_DMG_MORI_SERIES_SPOKES = {
    "nlx-turning": {
        "title":   "DMG Mori NLX / ALX Turning Repair",
        "slug":    "dmg-mori-nlx-turning",
        "subtitle":"NLX / ALX Universal Turning",
        "url":     "/repairs/dmg-mori-cnc-machine-repair/nlx-turning/",
        "intro":   "NLX and ALX are DMG Mori's universal-turning workhorses — NLX-1500 through NLX-6000, ALX 1500 through 2500, with bed-length suffixes (/500, /700, /1500) and MC/SMC/Y/SY/MY configuration options. The line covers everything from compact 2-axis bar work to large mill-turn jobs. Most calls are turret, sub-spindle, or Y-axis work.",
        "failures": [
            "Turret indexing faults — solenoid, indexer pawl, or position-encoder issues.",
            "Sub-spindle alignment drift on SY and SMC twin-spindle configurations.",
            "Y-axis wear and backlash drift from heavy cuts.",
            "Tailstock quill issues on long-bed NLX-6000 builds.",
        ],
        "controls_paragraph": "NLX and ALX ship on [Siemens 840D](/repairs/dmg-mori-cnc-machine-repair/siemens-840d/) (typically 840D solutionline on newer builds), wrapped in the DMG Mori [CELOS](/repairs/dmg-mori-cnc-machine-repair/celos/) HMI layer. Service work spans both the control hardware and the CELOS-side integration.",
        "siblings": [
            ("CTX / CLX",  "/repairs/dmg-mori-cnc-machine-repair/ctx-clx-turning/"),
            ("NTX",        "/repairs/dmg-mori-cnc-machine-repair/ntx/"),
        ],
    },
    "ctx-clx-turning": {
        "title":   "DMG Mori CTX / CLX Turning Repair (including TC variants)",
        "slug":    "dmg-mori-ctx-clx-turning",
        "subtitle":"CTX / CLX Turning + TC",
        "url":     "/repairs/dmg-mori-cnc-machine-repair/ctx-clx-turning/",
        "intro":   "CTX and CLX cover DMG Mori's broader turning lineup — CLX 350/450/550 entry production, CTX 310 through 850 with alpha/beta/gamma variants, and the TC turn-mill builds (CTX Beta 800 TC, Beta 1250 TC, Gamma 2000 TC, Gamma 3000 TC). The TC machines add a milling B-axis that becomes the focal point for most service calls.",
        "failures": [
            "B-axis milling spindle wear on TC variants — bearing pack and alignment work.",
            "Lower turret faults on twin-turret configurations.",
            "Hydraulic chuck issues on heavy-cut production.",
            "Tailstock alignment on long-bed CTX 650 and CTX 850.",
        ],
        "controls_paragraph": "CTX and CLX ship on [Siemens 840D](/repairs/dmg-mori-cnc-machine-repair/siemens-840d/) under the [CELOS](/repairs/dmg-mori-cnc-machine-repair/celos/) HMI. TC variants with the added B-axis put more configuration work on the control side.",
        "siblings": [
            ("NLX / ALX",  "/repairs/dmg-mori-cnc-machine-repair/nlx-turning/"),
            ("NTX",        "/repairs/dmg-mori-cnc-machine-repair/ntx/"),
        ],
    },
    "ntx": {
        "title":   "DMG Mori NTX Integrated Mill-Turn Repair",
        "slug":    "dmg-mori-ntx",
        "subtitle":"NTX Integrated Mill-Turn",
        "url":     "/repairs/dmg-mori-cnc-machine-repair/ntx/",
        "intro":   "NTX is the integrated mill-turn flagship — NTX 1000 (1st and 2nd Gen), 1000/SZM, 2000, 2500, 3000, and 4000 with SZ, SZM, S, and S2 configuration suffixes. These are high-capability multitasking platforms with full B-axis milling spindles. Most service calls center on the B-axis or the sub-spindle synchronization.",
        "failures": [
            "B-axis milling spindle bearing wear — the highest-stress component on these platforms.",
            "Sub-spindle synchronization drift on multi-tasking part transfer.",
            "Tool changer reliability — heavy ATC use on long-cycle parts.",
            "Spindle drive faults from sustained heavy cuts.",
        ],
        "controls_paragraph": "NTX ships on [Siemens 840D](/repairs/dmg-mori-cnc-machine-repair/siemens-840d/) under [CELOS](/repairs/dmg-mori-cnc-machine-repair/celos/). The B-axis kinematics need re-calibration after any milling-spindle work.",
        "siblings": [
            ("CTX / CLX",  "/repairs/dmg-mori-cnc-machine-repair/ctx-clx-turning/"),
            ("DMU / DMC",  "/repairs/dmg-mori-cnc-machine-repair/dmu-dmc/"),
        ],
    },
    "dmu-dmc": {
        "title":   "DMG Mori DMU / DMC 5-Axis Repair",
        "slug":    "dmg-mori-dmu-dmc",
        "subtitle":"DMU / DMC 5-Axis Universal and Cube",
        "url":     "/repairs/dmg-mori-cnc-machine-repair/dmu-dmc/",
        "intro":   "DMU and DMC are DMG Mori's 5-axis workhorses — DMU 50 through DMU 340, plus monoBLOCK and duoBLOCK builds, the DMU eVo, and DMC variants from 1035V through 160 U. The DMU Portal and DMU Gantry handle very large parts. Most failure work centers on the trunnion (DMU) or the swivel head (monoBLOCK).",
        "failures": [
            "Trunnion calibration drift after a crash — A and C axis zero-point recovery.",
            "Swivel head bearing wear on monoBLOCK builds.",
            "RTCP and kinematic drift after any 5-axis component work.",
            "Swarf intrusion at trunnion bearings on heavy-coolant production.",
        ],
        "controls_paragraph": "DMU machines mostly ship on [Heidenhain TNC](/repairs/dmg-mori-cnc-machine-repair/heidenhain-tnc/) (iTNC 530 on legacy builds, TNC 640 on current). DMC builds typically ship on [Siemens 840D](/repairs/dmg-mori-cnc-machine-repair/siemens-840d/). All run under [CELOS](/repairs/dmg-mori-cnc-machine-repair/celos/).",
        "siblings": [
            ("NHX / NH",   "/repairs/dmg-mori-cnc-machine-repair/nhx-horizontals/"),
            ("NVX / NV",   "/repairs/dmg-mori-cnc-machine-repair/nvx-verticals/"),
        ],
    },
    "nhx-horizontals": {
        "title":   "DMG Mori NHX / NH Horizontal Repair",
        "slug":    "dmg-mori-nhx-horizontals",
        "subtitle":"NHX / NH Horizontals",
        "url":     "/repairs/dmg-mori-cnc-machine-repair/nhx-horizontals/",
        "intro":   "NHX and the older NH are DMG Mori's horizontal lineup — NHX 4000 through 10000 plus the legacy NH 4000/5000/6300. These are production horizontals built around pallet-changer reliability and B-axis indexing.",
        "failures": [
            "Pallet changer faults — clamp pressure, pallet seat alignment, position sensors.",
            "B-axis indexer wear from heavy-cut production.",
            "Coolant intrusion at the pallet seal on high-coolant work.",
            "Chip evacuation — auger jams and conveyor reliability.",
        ],
        "controls_paragraph": "NHX and NH ship on [Siemens 840D](/repairs/dmg-mori-cnc-machine-repair/siemens-840d/) under [CELOS](/repairs/dmg-mori-cnc-machine-repair/celos/).",
        "siblings": [
            ("DMU / DMC",  "/repairs/dmg-mori-cnc-machine-repair/dmu-dmc/"),
            ("NVX / NV",   "/repairs/dmg-mori-cnc-machine-repair/nvx-verticals/"),
        ],
    },
    "nvx-verticals": {
        "title":   "DMG Mori NVX / NV / NVD Vertical Repair",
        "slug":    "dmg-mori-nvx-verticals",
        "subtitle":"NVX / NV / NVD Verticals",
        "url":     "/repairs/dmg-mori-cnc-machine-repair/nvx-verticals/",
        "intro":   "NVX is DMG Mori's high-end vertical lineup — NVX 4000 through 7000. The older NV 4000 and NV 5000 still see service work on mid-life machines. NVD with DCG (Driven at the Center of Gravity) construction targets high-acceleration production.",
        "failures": [
            "ATC reliability — solenoid, indexer pawl, carousel-position drift.",
            "Ballscrew wear from heavy production cycles.",
            "Spindle bearing failure on high-RPM NVX 5060 and similar.",
            "Way cover damage from chip intrusion or crash.",
        ],
        "controls_paragraph": "NVX, NV, and NVD ship on [Siemens 840D](/repairs/dmg-mori-cnc-machine-repair/siemens-840d/) under [CELOS](/repairs/dmg-mori-cnc-machine-repair/celos/).",
        "siblings": [
            ("DMU / DMC",     "/repairs/dmg-mori-cnc-machine-repair/dmu-dmc/"),
            ("NHX / NH",      "/repairs/dmg-mori-cnc-machine-repair/nhx-horizontals/"),
        ],
    },
    "cmx": {
        "title":   "DMG Mori CMX / CMX U Repair",
        "slug":    "dmg-mori-cmx",
        "subtitle":"CMX Entry and 5-Sided",
        "url":     "/repairs/dmg-mori-cnc-machine-repair/cmx/",
        "intro":   "CMX is DMG Mori's entry-level production line — CMX 600V through CMX 1300V verticals, CMX 50U and 70U 5-axis universals, and the CMX 320 V compact. The platform is built for accessibility and cost; service patterns reflect more wear in heavy-use environments than the high-end DMU and NVX lines.",
        "failures": [
            "ATC reliability — solenoid wear and pawl alignment on heavy-cycle work.",
            "Spindle bearing wear on machines pushed to upper RPM limits.",
            "Way cover damage in busy production environments.",
            "Coolant intrusion at the spindle nose on high-coolant work.",
        ],
        "controls_paragraph": "CMX machines ship on [Siemens 840D](/repairs/dmg-mori-cnc-machine-repair/siemens-840d/) under [CELOS](/repairs/dmg-mori-cnc-machine-repair/celos/).",
        "siblings": [
            ("DMU / DMC",     "/repairs/dmg-mori-cnc-machine-repair/dmu-dmc/"),
            ("DMP / Milltap", "/repairs/dmg-mori-cnc-machine-repair/dmp-milltap/"),
        ],
    },
    "dmp-milltap": {
        "title":   "DMG Mori DMP / Milltap Compact Production Repair",
        "slug":    "dmg-mori-dmp-milltap",
        "subtitle":"DMP / Milltap Compact Production",
        "url":     "/repairs/dmg-mori-cnc-machine-repair/dmp-milltap/",
        "intro":   "DMP and Milltap cover the compact, high-cycle production end of the DMG Mori range — DMP 35 through 70, the dual-spindle DMP 500, and the Milltap 700. These are high-throughput drill-tap and small-part machines; wear patterns track the cycle count.",
        "failures": [
            "High-cycle ATC wear from short-cycle production.",
            "Ballscrew wear on heavy-throughput drill-tap work.",
            "Spindle bearing failure on high-RPM, short-cycle use.",
            "Way wear in dirty production environments.",
        ],
        "controls_paragraph": "DMP and Milltap ship on [Siemens 840D](/repairs/dmg-mori-cnc-machine-repair/siemens-840d/) under [CELOS](/repairs/dmg-mori-cnc-machine-repair/celos/).",
        "siblings": [
            ("CMX",            "/repairs/dmg-mori-cnc-machine-repair/cmx/"),
            ("NVX / NV",       "/repairs/dmg-mori-cnc-machine-repair/nvx-verticals/"),
        ],
    },
    "sprint-multisprint": {
        "title":   "DMG Mori SPRINT / MULTISPRINT Repair",
        "slug":    "dmg-mori-sprint-multisprint",
        "subtitle":"SPRINT / MULTISPRINT Swiss-Production",
        "url":     "/repairs/dmg-mori-cnc-machine-repair/sprint-multisprint/",
        "intro":   "SPRINT and MULTISPRINT are DMG Mori's Swiss-style and production-turning platforms — SPRINT 20/32/50/65, MULTISPRINT 25 and 36. Swiss-type platforms have their own service patterns: guide bushing wear, sub-spindle sync, and bar-feed integration are the routine work.",
        "failures": [
            "Guide bushing wear from sustained Swiss-style production.",
            "Sub-spindle synchronization drift on part-transfer work.",
            "Bar feeder integration — sync and bar-end detection issues.",
            "Live-tool indexing on the multi-tool variants.",
        ],
        "controls_paragraph": "SPRINT and MULTISPRINT ship on [Siemens 840D](/repairs/dmg-mori-cnc-machine-repair/siemens-840d/) under [CELOS](/repairs/dmg-mori-cnc-machine-repair/celos/).",
        "siblings": [
            ("NLX / ALX",      "/repairs/dmg-mori-cnc-machine-repair/nlx-turning/"),
            ("CTX / CLX",      "/repairs/dmg-mori-cnc-machine-repair/ctx-clx-turning/"),
        ],
    },
}
_DMG_MORI_CONTROL_SPOKES = {
    "siemens-840d": {
        "title":   "Siemens 840D Repair on DMG Mori",
        "slug":    "dmg-mori-siemens-840d",
        "subtitle":"Siemens 840D / 840D solutionline",
        "url":     "/repairs/dmg-mori-cnc-machine-repair/siemens-840d/",
        "era":     "Late 1990s through present (solutionline current)",
        "intro":   "Siemens 840D is the most common DMG Mori control. The original 840D shipped through the mid-2000s; 840D solutionline (sl) is the current generation. Service work splits between hardware repair on older builds (NCU and PCU boards, drive faults) and configuration work on solutionline.",
        "machines_paragraph": "840D ships on the [NLX/ALX](/repairs/dmg-mori-cnc-machine-repair/nlx-turning/), [CTX/CLX](/repairs/dmg-mori-cnc-machine-repair/ctx-clx-turning/), [NTX](/repairs/dmg-mori-cnc-machine-repair/ntx/), [NHX/NH](/repairs/dmg-mori-cnc-machine-repair/nhx-horizontals/), [NVX/NV/NVD](/repairs/dmg-mori-cnc-machine-repair/nvx-verticals/), [CMX](/repairs/dmg-mori-cnc-machine-repair/cmx/), [DMP/Milltap](/repairs/dmg-mori-cnc-machine-repair/dmp-milltap/), [SPRINT/MULTISPRINT](/repairs/dmg-mori-cnc-machine-repair/sprint-multisprint/), and the [DMC](/repairs/dmg-mori-cnc-machine-repair/dmu-dmc/) builds in the DMU/DMC family.",
        "failures": [
            "PCU (Panel Control Unit) board faults — battery, fan, or HDD failure.",
            "NCU (Numerical Control Unit) board issues — generally board-level repair.",
            "Drive amplifier faults on heavy production work.",
            "Memory battery loss leading to parameter and program memory loss.",
            "MMC (Man-Machine Communication) failures on older 840D.",
        ],
        "parts_paragraph": "Siemens 840D parts are still well supported through Siemens and authorized service partners. Original 840D (non-solutionline) boards are heading toward aftermarket and remanufactured-only over the next several years. Solutionline parts are fully current.",
        "recovery_paragraph": "Parameter backup on 840D is a documented Siemens process — back up via the operator panel before any battery or board work. We capture the parameter set at the start of every service visit and verify the restore at sign-off. CF card and HDD migration on older 840D PCUs is part of the same conversation.",
        "siblings": [
            ("Heidenhain TNC",  "/repairs/dmg-mori-cnc-machine-repair/heidenhain-tnc/"),
            ("CELOS",           "/repairs/dmg-mori-cnc-machine-repair/celos/"),
        ],
    },
    "heidenhain-tnc": {
        "title":   "Heidenhain TNC Repair on DMG Mori (iTNC 530, TNC 640)",
        "slug":    "dmg-mori-heidenhain-tnc",
        "subtitle":"Heidenhain TNC",
        "url":     "/repairs/dmg-mori-cnc-machine-repair/heidenhain-tnc/",
        "era":     "iTNC 530 from roughly 2001, TNC 640 from 2012",
        "intro":   "Heidenhain TNC is the common control on DMG Mori's DMU and DMC 5-axis lines — iTNC 530 on legacy builds and TNC 640 on current. The TNC family is heavily used in mold and die work where its conversational programming and geometric capability shine. Service work mostly centers on keypad, encoder, and drive system.",
        "machines_paragraph": "Heidenhain TNC ships on the [DMU/DMC](/repairs/dmg-mori-cnc-machine-repair/dmu-dmc/) 5-axis family — DMU 50 through DMU 340, monoBLOCK and duoBLOCK builds, DMU eVo, and the DMC universals. Most of the high-end DMG Mori 5-axis work runs on this control.",
        "failures": [
            "Keypad failure — heavy daily use makes this the most common single failure mode.",
            "Encoder drift — particularly on rotary-axis encoders for trunnion machines.",
            "Drive system faults on heavy 5-axis cuts.",
            "MC (Main Computer) board faults on older iTNC 530 builds.",
            "Memory battery loss.",
        ],
        "parts_paragraph": "Heidenhain TNC parts are well supported through Heidenhain and authorized service partners. iTNC 530 is heading toward late-life status; TNC 640 is fully current.",
        "recovery_paragraph": "Heidenhain TNC backup is well documented — back up parameters and tool tables to the network or USB before any work. We verify the restore at sign-off.",
        "siblings": [
            ("Siemens 840D",  "/repairs/dmg-mori-cnc-machine-repair/siemens-840d/"),
            ("CELOS",         "/repairs/dmg-mori-cnc-machine-repair/celos/"),
        ],
    },
    "celos": {
        "title":   "CELOS / CELOS X / Operate Service on DMG Mori",
        "slug":    "dmg-mori-celos",
        "subtitle":"CELOS HMI Layer",
        "url":     "/repairs/dmg-mori-cnc-machine-repair/celos/",
        "era":     "CELOS from 2014, CELOS X current",
        "intro":   "CELOS is the DMG Mori HMI layer that sits on top of the underlying Siemens or Heidenhain control. It's the operator-facing interface and the integration point for shop-floor monitoring, job preparation, and digital twin work. Service is more about configuration and integration than hardware repair.",
        "machines_paragraph": "CELOS runs on every current DMG Mori machine — every [NLX/ALX](/repairs/dmg-mori-cnc-machine-repair/nlx-turning/), [CTX/CLX](/repairs/dmg-mori-cnc-machine-repair/ctx-clx-turning/), [NTX](/repairs/dmg-mori-cnc-machine-repair/ntx/), [DMU/DMC](/repairs/dmg-mori-cnc-machine-repair/dmu-dmc/), [NHX/NH](/repairs/dmg-mori-cnc-machine-repair/nhx-horizontals/), [NVX/NV/NVD](/repairs/dmg-mori-cnc-machine-repair/nvx-verticals/), [CMX](/repairs/dmg-mori-cnc-machine-repair/cmx/), [DMP/Milltap](/repairs/dmg-mori-cnc-machine-repair/dmp-milltap/), and [SPRINT](/repairs/dmg-mori-cnc-machine-repair/sprint-multisprint/) machines.",
        "failures": [
            "IPC (Industrial PC) reliability — boot drive and fan issues on older CELOS hardware.",
            "Network configuration drift after shop-floor IT changes.",
            "App integration issues — CELOS apps interacting with shop-floor monitoring systems.",
            "Touchscreen calibration drift.",
        ],
        "parts_paragraph": "CELOS hardware (the IPC) is fully supported through DMG Mori. The control underneath (Siemens or Heidenhain) follows its own parts lifecycle — see the respective control spokes.",
        "recovery_paragraph": "CELOS configuration backup is part of the standard DMG Mori service workflow. Networking, MTConnect/OPC UA, and CELOS app configuration get documented before any service work and verified at sign-off.",
        "siblings": [
            ("Siemens 840D",  "/repairs/dmg-mori-cnc-machine-repair/siemens-840d/"),
            ("Heidenhain TNC","/repairs/dmg-mori-cnc-machine-repair/heidenhain-tnc/"),
        ],
    },
}

_DOOSAN_SERIES_SPOKES = {
    "puma": {
        "title":   "Doosan Puma Horizontal Turning Repair",
        "slug":    "doosan-puma",
        "subtitle":"Puma Horizontal Turning",
        "url":     "/repairs/doosan-cnc-machine-repair/puma/",
        "intro":   "The Puma series is the Doosan turning workhorse — Puma 230 through Puma 800, with M/MS/LM/LY/Y/SY/SY II configuration variants, the heavier 4100 and 5100 builds, the GT compact lineup, the TT twin-turret builds, and the TW gantry-loaded variants. Most Midwest shop floors running Doosan have at least one Puma.",
        "failures": [
            "Turret indexing — solenoid, indexer pawl, position-encoder issues.",
            "Sub-spindle alignment drift on SY twin-spindle configurations.",
            "Y-axis backlash and ballscrew wear from heavy cuts.",
            "Tailstock quill wear and pressure loss on long-bed builds.",
            "Lower turret faults on the TT twin-turret builds.",
        ],
        "controls_paragraph": "Puma ships primarily on Fanuc — entry and mid-range Puma builds run [Fanuc 0i](/repairs/fanuc-cnc-machine-repair/series-0i/) (typically 0i-D or 0i-F), and higher-end Puma 2600SY, 3100, 4100, 5100, 700, and 800 builds run [Fanuc 30i](/repairs/fanuc-cnc-machine-repair/series-30i-31i-32i/).",
        "siblings": [
            ("Puma MX / SMX",  "/repairs/doosan-cnc-machine-repair/puma-mx-smx/"),
            ("Lynx",           "/repairs/doosan-cnc-machine-repair/lynx/"),
        ],
    },
    "puma-mx-smx": {
        "title":   "Doosan Puma MX / SMX Multitasking Repair",
        "slug":    "doosan-puma-mx-smx",
        "subtitle":"Puma MX / SMX Multitasking",
        "url":     "/repairs/doosan-cnc-machine-repair/puma-mx-smx/",
        "intro":   "Puma MX and SMX are Doosan's mill-turn multitasking lineup — MX 1600 through 3100 with T/ST/SY configuration variants, and the newer SMX 2100, 2600, and 3100 with ST and S variants. These are high-capability platforms with B-axis milling spindles; most service calls center on the B-axis.",
        "failures": [
            "B-axis milling spindle wear — highest-stress component on these platforms.",
            "Lower turret faults on twin-turret configurations.",
            "ATC reliability on the multitasking ATC.",
            "Sub-spindle synchronization on multi-axis transfer work.",
        ],
        "controls_paragraph": "Puma MX and SMX ship on [Fanuc 30i](/repairs/fanuc-cnc-machine-repair/series-30i-31i-32i/) — typically 30i-B on current builds. The multi-axis kinematics make Fanuc 30i the right fit for these platforms.",
        "siblings": [
            ("Puma",  "/repairs/doosan-cnc-machine-repair/puma/"),
            ("DVF",   "/repairs/doosan-cnc-machine-repair/5-axis-verticals/"),
        ],
    },
    "puma-vertical-turning": {
        "title":   "Doosan Puma V / VT / VTR Vertical Turning Repair",
        "slug":    "doosan-puma-vertical-turning",
        "subtitle":"Puma V / VT / VTR Vertical Turning",
        "url":     "/repairs/doosan-cnc-machine-repair/puma-vertical-turning/",
        "intro":   "Puma V, VT, and VTR are Doosan's vertical turning lineup — Puma V400 through V9300 chuckers, the VT 750/900/1100 vertical turning centers, and the VTR ram-type machines. These platforms handle large, heavy parts where vertical orientation makes the load and chip evacuation easier.",
        "failures": [
            "Large-table bearing wear from sustained heavy-cut production.",
            "ATC reliability on the V-series with integrated milling.",
            "Hydraulic clamp pressure loss on the workpiece clamping system.",
            "Way wear on the long ram travel of VTR machines.",
        ],
        "controls_paragraph": "Puma V, VT, and VTR ship on [Fanuc 30i](/repairs/fanuc-cnc-machine-repair/series-30i-31i-32i/) on most current builds. Older V400 may still run [Fanuc 0i](/repairs/fanuc-cnc-machine-repair/series-0i/).",
        "siblings": [
            ("Puma",        "/repairs/doosan-cnc-machine-repair/puma/"),
            ("DNM",         "/repairs/doosan-cnc-machine-repair/dnm-verticals/"),
        ],
    },
    "lynx": {
        "title":   "Doosan Lynx Compact Turning Repair",
        "slug":    "doosan-lynx",
        "subtitle":"Lynx Compact Turning",
        "url":     "/repairs/doosan-cnc-machine-repair/lynx/",
        "intro":   "Lynx is Doosan's compact turning lineup — Lynx 220, 2100, 2600, and 300 with a wide range of M, MS, LM, LSY, LY, LMA, MA, II and similar configuration variants. The compact platform is heavily used in small-shop bar work and bar-fed production; service patterns track high-cycle wear.",
        "failures": [
            "Turret indexing — the most common single failure on Lynx compact platforms.",
            "Bar feeder integration issues — sync and bar-end detection.",
            "Sub-spindle alignment on LSY configurations.",
            "Chuck cylinder leaks from sustained bar-work cycles.",
        ],
        "controls_paragraph": "Lynx ships on [Fanuc 0i](/repairs/fanuc-cnc-machine-repair/series-0i/) — typically 0i-D or 0i-F. The compact platform doesn't need the higher-end 30i family.",
        "siblings": [
            ("Puma",  "/repairs/doosan-cnc-machine-repair/puma/"),
            ("Swiss / DST",  "/repairs/doosan-cnc-machine-repair/swiss-turning/"),
        ],
    },
    "dnm-verticals": {
        "title":   "Doosan DNM Vertical Machining Repair",
        "slug":    "doosan-dnm-verticals",
        "subtitle":"DNM Vertical Machining",
        "url":     "/repairs/doosan-cnc-machine-repair/dnm-verticals/",
        "intro":   "DNM is Doosan's vertical machining lineup — DNM 200 through DNM 750, with the higher-end DNM 4000/5700/6700 production builds, plus the DNM 200/5AX 5-axis variant. The platform is broad and the most common Doosan vertical on Midwest shop floors.",
        "failures": [
            "ATC carousel faults — solenoid, indexer pawl, carousel-position drift.",
            "Ballscrew wear from sustained production.",
            "Spindle bearing failure on high-RPM production work.",
            "Way cover damage from chip intrusion or crash.",
        ],
        "controls_paragraph": "DNM ships on [Fanuc 0i](/repairs/fanuc-cnc-machine-repair/series-0i/) on entry and mid-range builds, and [Fanuc 30i](/repairs/fanuc-cnc-machine-repair/series-30i-31i-32i/) on the higher-end DNM 4000/5700/6700/750 production verticals.",
        "siblings": [
            ("Horizontals (NHM/NHP/HC)",  "/repairs/doosan-cnc-machine-repair/horizontals/"),
            ("5-Axis Verticals (DVF)",     "/repairs/doosan-cnc-machine-repair/5-axis-verticals/"),
        ],
    },
    "horizontals": {
        "title":   "Doosan Horizontal Repair (NHM / NHP / HC)",
        "slug":    "doosan-horizontals",
        "subtitle":"NHM / NHP / HC Horizontals",
        "url":     "/repairs/doosan-cnc-machine-repair/horizontals/",
        "intro":   "Doosan's horizontals — NHM 4000 through 8000, NHP 4000 through 6300, HC 400 and 500 — are production-focused platforms with pallet changers and B-axis indexing. Most calls come from the pallet changer or the B-axis.",
        "failures": [
            "Pallet changer faults — clamp pressure, pallet seat, position sensors.",
            "B-axis indexer wear from heavy-cut production.",
            "Coolant intrusion at the pallet seal on high-coolant work.",
            "Chip evacuation reliability — auger and conveyor work.",
        ],
        "controls_paragraph": "NHM, NHP, and HC ship on [Fanuc 30i](/repairs/fanuc-cnc-machine-repair/series-30i-31i-32i/). The multi-axis pallet handling fits the 30i family.",
        "siblings": [
            ("DNM Verticals",  "/repairs/doosan-cnc-machine-repair/dnm-verticals/"),
            ("Puma",           "/repairs/doosan-cnc-machine-repair/puma/"),
        ],
    },
    "5-axis-verticals": {
        "title":   "Doosan DVF / FM 5-Axis Vertical Repair",
        "slug":    "doosan-5-axis-verticals",
        "subtitle":"DVF / FM 5-Axis Verticals",
        "url":     "/repairs/doosan-cnc-machine-repair/5-axis-verticals/",
        "intro":   "DVF and FM are Doosan's 5-axis vertical line — DVF 5000, 6500, 8000 trunnion-table 5-axis, and the FM 200/5AX Linear-motor build. Most calls center on the trunnion, the rotary-axis encoders, or RTCP drift after crash work.",
        "failures": [
            "Trunnion calibration drift after a crash.",
            "A and C-axis encoder faults — contamination or signal loss.",
            "RTCP drift after spindle or trunnion work.",
            "Linear-motor drive issues on the FM 200/5AX.",
        ],
        "controls_paragraph": "DVF and FM ship on [Fanuc 30i](/repairs/fanuc-cnc-machine-repair/series-30i-31i-32i/) — typically 30i-B on current builds. The 5-axis kinematics need 30i's higher feature set.",
        "siblings": [
            ("DNM Verticals",   "/repairs/doosan-cnc-machine-repair/dnm-verticals/"),
            ("Puma MX / SMX",   "/repairs/doosan-cnc-machine-repair/puma-mx-smx/"),
        ],
    },
    "swiss-turning": {
        "title":   "Doosan Swiss-Type / DST Repair",
        "slug":    "doosan-swiss-turning",
        "subtitle":"Swiss-Type / DST",
        "url":     "/repairs/doosan-cnc-machine-repair/swiss-turning/",
        "intro":   "Doosan's Swiss-style platforms — SwiftTurn 32 and 38, plus the DST series — handle high-precision small-diameter bar work. Swiss-type service patterns are specific: guide bushing wear, sub-spindle sync, and bar feed integration are the routine work.",
        "failures": [
            "Guide bushing wear from sustained Swiss-style production.",
            "Sub-spindle synchronization on part-transfer.",
            "Bar feed integration — bar-end detection and sync.",
            "Live tool indexing on multi-tool variants.",
        ],
        "controls_paragraph": "Doosan Swiss platforms ship on [Fanuc 30i](/repairs/fanuc-cnc-machine-repair/series-30i-31i-32i/).",
        "siblings": [
            ("Lynx",  "/repairs/doosan-cnc-machine-repair/lynx/"),
            ("Puma",  "/repairs/doosan-cnc-machine-repair/puma/"),
        ],
    },
}

_OKUMA_SERIES_SPOKES = {
    "lb-lu-lathes": {
        "title":   "Okuma LB / LU Lathe Repair",
        "slug":    "okuma-lb-lu-lathes",
        "subtitle":"LB / LU Horizontal Lathes",
        "url":     "/repairs/okuma-cnc-machine-repair/lb-lu-lathes/",
        "intro":   "LB and LU are Okuma's horizontal lathe workhorses — LB 200 through LB 5000 EX, LU 300 through LU 8000. The line spans entry production to large-bore turning. Live-tool variants add live-tool drive complexity; long-bed builds see spindle wear from extended cuts.",
        "failures": [
            "Turret indexing faults — solenoid, indexer pawl, position-encoder.",
            "Tailstock quill wear on long-bed LB 4000 and LB 5000.",
            "Spindle bearing wear on heavily used LB and LU long-bed.",
            "Live-tool indexing issues on the live-tool variants.",
        ],
        "controls_paragraph": "Older LB and LU run [OSP-P200](/repairs/okuma-cnc-machine-repair/osp-p200/); mid-life builds run [OSP-P300](/repairs/okuma-cnc-machine-repair/osp-p300/); the latest LB 3000 EX II and LB 4000/5000 EX run [OSP-P500](/repairs/okuma-cnc-machine-repair/osp-p500/) on current production. Legacy ES-L and ESV builds may still be on [OSP Legacy](/repairs/okuma-cnc-machine-repair/osp-legacy/).",
        "siblings": [
            ("Genos",   "/repairs/okuma-cnc-machine-repair/genos/"),
            ("MULTUS",  "/repairs/okuma-cnc-machine-repair/multus/"),
        ],
    },
    "genos": {
        "title":   "Okuma Genos L / Genos M Repair",
        "slug":    "okuma-genos",
        "subtitle":"Genos L / Genos M",
        "url":     "/repairs/okuma-cnc-machine-repair/genos/",
        "intro":   "Genos is Okuma's 'Affordable Excellence' line — Genos L lathes (L250, L300, L3000-e, L400, L4000) and Genos M verticals (M460-VE, M560-V, M660-V). The platform is built for accessibility; service patterns include more ATC wear and thermal issues than the higher-end MULTUS or MB/MA lines.",
        "failures": [
            "ATC wear from production cycles — solenoid and pawl alignment.",
            "Spindle thermal issues — heat-related drift on heavy cuts.",
            "Control panel reliability — keypad and touchscreen on older Genos.",
            "Way wear in dirty production environments.",
        ],
        "controls_paragraph": "Genos ships on [OSP-P300](/repairs/okuma-cnc-machine-repair/osp-p300/) — the standard control for the line through current builds.",
        "siblings": [
            ("LB / LU Lathes",       "/repairs/okuma-cnc-machine-repair/lb-lu-lathes/"),
            ("MB / MA Verticals",    "/repairs/okuma-cnc-machine-repair/mb-ma-verticals/"),
        ],
    },
    "mb-ma-verticals": {
        "title":   "Okuma MB / MA Vertical Machining Repair",
        "slug":    "okuma-mb-ma-verticals",
        "subtitle":"MB / MA Vertical Machining",
        "url":     "/repairs/okuma-cnc-machine-repair/mb-ma-verticals/",
        "intro":   "MB and MA are Okuma's vertical machining workhorses — MB-46V through MB-66V production verticals, the MB-4000H and MB-5000H horizontal-spindle builds, and the MA-400 through MA-8000 larger-envelope platforms. The line covers entry production to large-bed work.",
        "failures": [
            "ATC drum indexing — common on production-cycle machines.",
            "Ballscrew wear from sustained heavy cuts.",
            "Spindle bearing failure on high-RPM MB work.",
            "Way wear on MA-400 and MA-500 machines from extended production.",
        ],
        "controls_paragraph": "Older MB and MA run [OSP-P200](/repairs/okuma-cnc-machine-repair/osp-p200/); current MB and MA builds run [OSP-P300](/repairs/okuma-cnc-machine-repair/osp-p300/). Legacy MV and MX-45 are usually [OSP Legacy](/repairs/okuma-cnc-machine-repair/osp-legacy/).",
        "siblings": [
            ("Genos",    "/repairs/okuma-cnc-machine-repair/genos/"),
            ("MULTUS",   "/repairs/okuma-cnc-machine-repair/multus/"),
        ],
    },
    "multus": {
        "title":   "Okuma MULTUS B-Axis Multitasking Repair",
        "slug":    "okuma-multus",
        "subtitle":"MULTUS B-Axis Multitasking",
        "url":     "/repairs/okuma-cnc-machine-repair/multus/",
        "intro":   "MULTUS is Okuma's B-axis multitasking line — MULTUS B200 through B750 (with II variants), MULTUS U3000 through U5000 large-envelope builds, and the historic MacTurn predecessors. These platforms add a B-axis milling spindle to a turning chassis; service work centers on the B-axis and the lower turret.",
        "failures": [
            "B-axis milling spindle bearing wear — highest-stress component.",
            "Lower turret faults on twin-turret configurations.",
            "ATC chain reliability on the multitasking ATC.",
            "Sub-spindle alignment on dual-spindle MULTUS builds.",
        ],
        "controls_paragraph": "MULTUS runs on [OSP-P200](/repairs/okuma-cnc-machine-repair/osp-p200/) on older builds and [OSP-P300](/repairs/okuma-cnc-machine-repair/osp-p300/) on current. The flagship MULTUS U5000 and current B-II builds ship on [OSP-P500](/repairs/okuma-cnc-machine-repair/osp-p500/).",
        "siblings": [
            ("Twin-Spindle / Twin-Turret",  "/repairs/okuma-cnc-machine-repair/twin-spindle-twin-turret/"),
            ("LB / LU Lathes",              "/repairs/okuma-cnc-machine-repair/lb-lu-lathes/"),
        ],
    },
    "twin-spindle-twin-turret": {
        "title":   "Okuma Twin-Spindle / Twin-Turret Repair (MacTurn / 2SP / LT)",
        "slug":    "okuma-twin-spindle-twin-turret",
        "subtitle":"Twin-Spindle / Twin-Turret",
        "url":     "/repairs/okuma-cnc-machine-repair/twin-spindle-twin-turret/",
        "intro":   "Okuma's twin-spindle and twin-turret turning — 2SP-2500H, 2SP-V40, LT 200-MY through LT 300-MY, and the LT 2000 EX. The historic LT-25 and LT-15 still see service work. Twin-spindle platforms add sub-spindle sync complexity; twin-turret platforms add lower-turret reliability.",
        "failures": [
            "Sub-spindle synchronization on twin-spindle work.",
            "Lower turret indexing and reliability.",
            "Hydraulic system pressure loss on twin-spindle.",
            "Part-transfer reliability on parts catcher systems.",
        ],
        "controls_paragraph": "Twin-spindle and twin-turret platforms ship on [OSP-P200](/repairs/okuma-cnc-machine-repair/osp-p200/) on older builds, [OSP-P300](/repairs/okuma-cnc-machine-repair/osp-p300/) on the LT 300-MY and LT 2000 EX. Legacy LT-15 and LT-25 are typically [OSP Legacy](/repairs/okuma-cnc-machine-repair/osp-legacy/).",
        "siblings": [
            ("MULTUS",        "/repairs/okuma-cnc-machine-repair/multus/"),
            ("LB / LU Lathes","/repairs/okuma-cnc-machine-repair/lb-lu-lathes/"),
        ],
    },
    "vtm": {
        "title":   "Okuma VTM Vertical Turning Repair",
        "slug":    "okuma-vtm",
        "subtitle":"VTM Vertical Turning",
        "url":     "/repairs/okuma-cnc-machine-repair/vtm/",
        "intro":   "VTM is Okuma's vertical turning lineup — VTM-65, VTM-100, VTM-120, VTM-180. These handle large, heavy parts where vertical orientation simplifies chip evacuation and chucking large workpieces.",
        "failures": [
            "Table bearing wear on sustained heavy-cut production.",
            "ATC reliability on milling-capable VTM builds.",
            "Swarf evacuation around the table on heavy roughing.",
            "Hydraulic clamp pressure loss.",
        ],
        "controls_paragraph": "VTM runs on [OSP-P200](/repairs/okuma-cnc-machine-repair/osp-p200/) on older builds and [OSP-P300](/repairs/okuma-cnc-machine-repair/osp-p300/) on current.",
        "siblings": [
            ("MU / MCR (5-Axis & Bridge)",  "/repairs/okuma-cnc-machine-repair/v-bridge-mills/"),
            ("LAW / LFS Heavy Lathes",      "/repairs/okuma-cnc-machine-repair/heavy-lathes/"),
        ],
    },
    "v-bridge-mills": {
        "title":   "Okuma MU 5-Axis and MCR Bridge Mill Repair",
        "slug":    "okuma-v-bridge-mills",
        "subtitle":"MU 5-Axis / MCR Bridge",
        "url":     "/repairs/okuma-cnc-machine-repair/v-bridge-mills/",
        "intro":   "MU is Okuma's 5-axis vertical lineup — MU-400V through MU-8000V trunnion-table 5-axis machines. MCR-A5C and MCR-BIII are Okuma's bridge mills for very large parts. The two share Okuma's OSP control but the service patterns differ — MU is trunnion-driven; MCR is bridge geometry.",
        "failures": [
            "Trunnion calibration drift on MU builds — A and C-axis zero-point work.",
            "Bridge geometry calibration on MCR — large-span alignment.",
            "Spindle bearing wear on MU 5-axis builds from high-stress cuts.",
            "Linear scale issues on bridge machines.",
        ],
        "controls_paragraph": "MU and MCR ship on [OSP-P300](/repairs/okuma-cnc-machine-repair/osp-p300/) — the standard control for these platforms across the current generation.",
        "siblings": [
            ("MB / MA Verticals",  "/repairs/okuma-cnc-machine-repair/mb-ma-verticals/"),
            ("VTM",                "/repairs/okuma-cnc-machine-repair/vtm/"),
        ],
    },
    "heavy-lathes": {
        "title":   "Okuma Heavy Lathe Repair (LAW / LFS)",
        "slug":    "okuma-heavy-lathes",
        "subtitle":"LAW / LFS Heavy Lathes",
        "url":     "/repairs/okuma-cnc-machine-repair/heavy-lathes/",
        "intro":   "LAW and LFS are Okuma's heavy-duty turning — LAW 1000 through 3000 heavy lathes and LFS-590 flat-bed turning. These handle very large workpieces and very heavy cuts; failure patterns track the loads.",
        "failures": [
            "Large-bore spindle wear on sustained heavy roughing.",
            "Way wear from extended heavy-cut production.",
            "Hydraulic chuck pressure loss on large workpieces.",
            "Drive amplifier faults from heavy-cut loads.",
        ],
        "controls_paragraph": "LAW and LFS run on [OSP-P200](/repairs/okuma-cnc-machine-repair/osp-p200/) on older builds and [OSP-P300](/repairs/okuma-cnc-machine-repair/osp-p300/) on current.",
        "siblings": [
            ("LB / LU Lathes",  "/repairs/okuma-cnc-machine-repair/lb-lu-lathes/"),
            ("VTM",             "/repairs/okuma-cnc-machine-repair/vtm/"),
        ],
    },
}
_OKUMA_CONTROL_SPOKES = {
    "osp-p200": {
        "title":   "Okuma OSP-P200 Repair",
        "slug":    "okuma-osp-p200",
        "subtitle":"OSP-P200",
        "url":     "/repairs/okuma-cnc-machine-repair/osp-p200/",
        "era":     "Roughly 2003 through 2012",
        "intro":   "OSP-P200 is the Okuma control generation that shipped on most early-2000s through early-2010s Okuma machines. In 2026 it's at the late-life stage — HDD failures, MMC board issues, and keypad wear are the routine service work. Most P200 boards are still serviceable but heading toward aftermarket-only on some.",
        "machines_paragraph": "OSP-P200 shipped across the Okuma lineup — older [LB and LU lathes](/repairs/okuma-cnc-machine-repair/lb-lu-lathes/), [MB and MA verticals](/repairs/okuma-cnc-machine-repair/mb-ma-verticals/), older [MULTUS](/repairs/okuma-cnc-machine-repair/multus/) builds, [VTM](/repairs/okuma-cnc-machine-repair/vtm/) verticals, [twin-spindle and twin-turret](/repairs/okuma-cnc-machine-repair/twin-spindle-twin-turret/) builds, and [LAW heavy lathes](/repairs/okuma-cnc-machine-repair/heavy-lathes/).",
        "failures": [
            "HDD failure — the most common single issue. SSD upgrades aren't standard on P200 but board-level replacement is.",
            "MMC board faults — control board sees enough thermal cycling to fail over a decade.",
            "Keypad failure — high-cycle keys go intermittent.",
            "Monitor failure — original displays approaching end of life.",
            "Fan failure and resulting thermal damage if not caught.",
        ],
        "parts_paragraph": "P200 parts are still supported through Okuma channels for most board items, but some components are heading toward aftermarket-only. We check parts availability before quoting board-level work.",
        "recovery_paragraph": "Parameter backup on P200 is straightforward through the control's built-in path. Battery work and any board-level repair starts with capturing parameters. We verify the restore at sign-off.",
        "siblings": [
            ("OSP-P300",   "/repairs/okuma-cnc-machine-repair/osp-p300/"),
            ("OSP Legacy", "/repairs/okuma-cnc-machine-repair/osp-legacy/"),
        ],
    },
    "osp-p300": {
        "title":   "Okuma OSP-P300 Repair",
        "slug":    "okuma-osp-p300",
        "subtitle":"OSP-P300",
        "url":     "/repairs/okuma-cnc-machine-repair/osp-p300/",
        "era":     "Roughly 2012 through 2020",
        "intro":   "OSP-P300 is the Okuma control generation that succeeded P200. It's mid-life now — current enough that parts are fully supported, but old enough that real service work shows up. SSD upgrades on early builds are increasingly common, and the touchscreen on heavy-use machines starts showing drift.",
        "machines_paragraph": "OSP-P300 ships across the modern Okuma lineup — current [LB and LU lathes](/repairs/okuma-cnc-machine-repair/lb-lu-lathes/), [Genos](/repairs/okuma-cnc-machine-repair/genos/), current [MB and MA verticals](/repairs/okuma-cnc-machine-repair/mb-ma-verticals/), [MULTUS](/repairs/okuma-cnc-machine-repair/multus/) (except current U5000), [VTM](/repairs/okuma-cnc-machine-repair/vtm/), [MU and MCR](/repairs/okuma-cnc-machine-repair/v-bridge-mills/), [twin-spindle / twin-turret](/repairs/okuma-cnc-machine-repair/twin-spindle-twin-turret/), and [LAW](/repairs/okuma-cnc-machine-repair/heavy-lathes/) builds.",
        "failures": [
            "SSD upgrade availability — common preventive service on early-generation P300 builds.",
            "Touchscreen drift on heavily used machines.",
            "Ethernet and USB issues — networking and media path reliability.",
            "Parameter backup discipline on a control with more parameters than P200.",
        ],
        "parts_paragraph": "OSP-P300 parts are fully supported through Okuma channels.",
        "recovery_paragraph": "P300 supports a clean parameter backup workflow via network or USB. We capture the parameter set at the start of every visit and verify the restore at sign-off.",
        "siblings": [
            ("OSP-P200",  "/repairs/okuma-cnc-machine-repair/osp-p200/"),
            ("OSP-P500",  "/repairs/okuma-cnc-machine-repair/osp-p500/"),
        ],
    },
    "osp-p500": {
        "title":   "Okuma OSP-P500 Repair",
        "slug":    "okuma-osp-p500",
        "subtitle":"OSP-P500",
        "url":     "/repairs/okuma-cnc-machine-repair/osp-p500/",
        "era":     "2020 to present",
        "intro":   "OSP-P500 is Okuma's current control generation. It's recent enough that hardware failures are uncommon — most service work is integration, MTConnect setup, app deployment, and networking. The conversation is more about configuration than reactive repair.",
        "machines_paragraph": "OSP-P500 ships on Okuma's current flagship platforms — the latest [LB 3000 EX II and LB 4000/5000 EX](/repairs/okuma-cnc-machine-repair/lb-lu-lathes/), current [MULTUS U5000 and B-II](/repairs/okuma-cnc-machine-repair/multus/), and other current-generation builds.",
        "failures": [
            "Network and Ethernet configuration drift after shop-floor IT changes.",
            "MTConnect setup and parameter mapping for shop-floor monitoring.",
            "App integration on the OSP-P500 platform.",
            "USB media reliability — periodic cleaning on the boot path.",
        ],
        "parts_paragraph": "P500 parts are fully current through Okuma channels.",
        "recovery_paragraph": "P500 has the most modern backup workflow in the Okuma family — network-based parameter and program backup. We document the parameter set at the start of every visit.",
        "siblings": [
            ("OSP-P300",  "/repairs/okuma-cnc-machine-repair/osp-p300/"),
            ("OSP-P200",  "/repairs/okuma-cnc-machine-repair/osp-p200/"),
        ],
    },
    "osp-legacy": {
        "title":   "Okuma OSP Legacy Control Repair",
        "slug":    "okuma-osp-legacy",
        "subtitle":"OSP Legacy",
        "url":     "/repairs/okuma-cnc-machine-repair/osp-legacy/",
        "era":     "Pre-2003",
        "intro":   "OSP Legacy covers Okuma's pre-2003 controls — OSP 5000, OSP 7000, U10, U100. These machines are at the heavy-obsolescence stage; most boards are aftermarket-only, and the conversation often becomes a retrofit consultation rather than a reactive repair.",
        "machines_paragraph": "OSP Legacy controls shipped on older Okuma platforms — legacy MV-series verticals, MX-45, ES-L and ESV [LB/LU](/repairs/okuma-cnc-machine-repair/lb-lu-lathes/) builds, older [LT-15 and LT-25 twin-turret](/repairs/okuma-cnc-machine-repair/twin-spindle-twin-turret/), and legacy MacTurn predecessors to current MULTUS.",
        "failures": [
            "Bubble memory loss on the oldest OSP 5000 builds.",
            "CRT failure — original tubes mostly out of service. LCD retrofits available.",
            "Keypad and MDI board failures.",
            "Drive amplifier obsolescence — heading toward aftermarket-only.",
            "Floppy and PCMCIA media reliability.",
        ],
        "parts_paragraph": "OSP Legacy is heavily obsolescent. Most board-level repair runs through remanufacturing specialists. For some machines, the conversation moves to retrofit — replacing the OSP Legacy control with a current OSP-P300 or P500, or a third-party retrofit. We scope what's repairable in place versus retrofit-territory before quoting.",
        "recovery_paragraph": "Parameter backup on OSP Legacy is generation-specific. The process starts with documenting the existing parameter set on whatever media the control supports, then planning the work. Floppy and PCMCIA migration to modern media is often part of the same conversation.",
        "siblings": [
            ("OSP-P200",  "/repairs/okuma-cnc-machine-repair/osp-p200/"),
            ("OSP-P300",  "/repairs/okuma-cnc-machine-repair/osp-p300/"),
        ],
    },
}

# Fanuc — controls-only, no series spokes. The hub flips Browse-by-Series
# to "Brands that ship Fanuc controls".
_FANUC_CONTROL_SPOKES = {
    "series-0-legacy": {
        "title":   "Fanuc Series 0 / 0M / 0T Repair (Pre-i Legacy)",
        "slug":    "fanuc-series-0-legacy",
        "subtitle":"Fanuc Series 0 / 0M / 0T",
        "url":     "/repairs/fanuc-cnc-machine-repair/series-0-legacy/",
        "era":     "1980s through 1990s",
        "intro":   "Fanuc Series 0 (and the 0M mill and 0T lathe variants) was the workhorse Fanuc control through the 1980s and 1990s. In 2026 these are deep-legacy machines — bubble memory loss, CRT failure, and drive obsolescence are the routine work, and most boards run through remanufacturing specialists rather than OEM supply.",
        "machines_paragraph": "Series 0 shipped on a huge range of late-1980s through 1990s machines across multiple OEMs. Anything from that era with 'Fanuc' on the control panel is likely Series 0 or a close relative. Many older [Doosan Puma](/repairs/doosan-cnc-machine-repair/puma/) and other Korean and Taiwanese-built lathes from this era used Series 0.",
        "failures": [
            "Bubble memory loss — the single most common failure on Series 0.",
            "CRT failure — original tubes mostly out of service. LCD retrofits available.",
            "Keyboard and MDI board failures.",
            "Drive system obsolescence — older servo amps going scarce.",
            "Power supply faults from decades of thermal cycling.",
        ],
        "parts_paragraph": "Series 0 parts are heavily aftermarket-only at this point. Remanufactured boards through specialists are the standard path on board-level work. For some machines the conversation moves to retrofit — replacing the Series 0 with a Fanuc 0i or a third-party control.",
        "recovery_paragraph": "Bubble memory and parameter recovery on Series 0 is the most fragile recovery procedure in the Fanuc family. Capture the parameter set before any battery or board work; battery replacement on a powered-up control where possible; restore parameters if memory was lost. We scope each job individually because Series 0 specifics vary by OEM and vintage.",
        "siblings": [
            ("Series 6 / 10 / 11 / 12 / 15", "/repairs/fanuc-cnc-machine-repair/series-6-15-legacy/"),
            ("Series 16i / 18i / 21i",       "/repairs/fanuc-cnc-machine-repair/series-16i-18i-21i/"),
        ],
    },
    "series-6-15-legacy": {
        "title":   "Fanuc Series 6 / 10 / 11 / 12 / 15 Repair",
        "slug":    "fanuc-series-6-15-legacy",
        "subtitle":"Series 6 through 15",
        "url":     "/repairs/fanuc-cnc-machine-repair/series-6-15-legacy/",
        "era":     "1980s through 2000s",
        "intro":   "Fanuc Series 6, 10, 11, 12, and 15 are the higher-end siblings of Series 0 — typically on larger or more complex machines from the 1980s through the 2000s. Series 15 in particular still sees active service on larger machines from the late 1990s and early 2000s. Failure modes overlap with Series 0 but parts availability is sometimes better.",
        "machines_paragraph": "Series 6 through 12 shipped on higher-end machines from various OEMs through the 1990s. Series 15 was common on larger and more sophisticated machines into the 2000s — including some larger [Doosan](/repairs/doosan-cnc-machine-repair/puma/) and other Asian-OEM platforms.",
        "failures": [
            "Memory battery loss leading to parameter and program loss.",
            "CRT failure — LCD retrofits available.",
            "Drive amplifier obsolescence.",
            "Keyboard and MDI board failures.",
            "PCB-level faults requiring remanufacturing.",
        ],
        "parts_paragraph": "Series 6 through 12 are deep-legacy with most parts aftermarket-only. Series 15 still has better parts availability through Fanuc and remanufacturing specialists.",
        "recovery_paragraph": "Battery and parameter recovery follows the standard Fanuc workflow — capture parameters before any battery work, replace the battery on a powered control, restore parameters as needed. Series 15 has somewhat better recovery tooling than the earlier siblings.",
        "siblings": [
            ("Series 0 / 0M / 0T",        "/repairs/fanuc-cnc-machine-repair/series-0-legacy/"),
            ("Series 16i / 18i / 21i",    "/repairs/fanuc-cnc-machine-repair/series-16i-18i-21i/"),
        ],
    },
    "series-16i-18i-21i": {
        "title":   "Fanuc Series 16i / 18i / 21i Repair (Model A & B)",
        "slug":    "fanuc-series-16i-18i-21i",
        "subtitle":"Series 16i / 18i / 21i",
        "url":     "/repairs/fanuc-cnc-machine-repair/series-16i-18i-21i/",
        "era":     "Roughly 1995 through 2010",
        "intro":   "Fanuc Series 16i, 18i, and 21i (with Model A and Model B revisions) are the most common Fanuc controls on mid-life machines in 2026. The family shipped on a huge fleet of late-1990s through late-2000s machines across many OEMs. PCMCIA media obsolescence, FROM/SRAM battery loss, drive amplifier faults, and monitor failure are the routine service work.",
        "machines_paragraph": "Series 16i, 18i, and 21i shipped on a wide cross-section of late-1990s through 2000s machines — many [Doosan Puma](/repairs/doosan-cnc-machine-repair/puma/) builds from this era, plus countless other Asian-OEM platforms running Fanuc controls.",
        "failures": [
            "PCMCIA media obsolescence — physical drives mostly still work but media sourcing and reader reliability are the issue.",
            "FROM and SRAM battery loss — leading to parameter and program memory loss.",
            "Drive amplifier faults from heavy production work.",
            "Monitor failure — original CRTs mostly out of service.",
            "Operator-panel button failure on high-cycle keys.",
        ],
        "parts_paragraph": "Series 16i / 18i / 21i parts are still available through Fanuc channels for most board items, but the supply chain is thinning. Remanufactured boards through specialists are increasingly common. PCMCIA-to-CF or PCMCIA-to-USB media migration is a frequent companion job.",
        "recovery_paragraph": "Battery and parameter recovery on the 16i/18i/21i family is the standard Fanuc process — capture parameters before any battery work, replace the battery on a powered control where possible, restore parameters as needed. PCMCIA media migration is part of the same conversation we scope upfront.",
        "siblings": [
            ("Series 0i",                  "/repairs/fanuc-cnc-machine-repair/series-0i/"),
            ("Series 30i / 31i / 32i",     "/repairs/fanuc-cnc-machine-repair/series-30i-31i-32i/"),
        ],
    },
    "series-0i": {
        "title":   "Fanuc Series 0i Repair (Model A through F)",
        "slug":    "fanuc-series-0i",
        "subtitle":"Series 0i (A/B/C/D/F)",
        "url":     "/repairs/fanuc-cnc-machine-repair/series-0i/",
        "era":     "2003 through present (0i-F current)",
        "intro":   "Fanuc Series 0i is ubiquitous — Model A through current Model F. It shipped on a huge fleet of mid-2000s through present-day machines, including most entry and mid-range [Doosan Puma](/repairs/doosan-cnc-machine-repair/puma/), [Doosan Lynx](/repairs/doosan-cnc-machine-repair/lynx/), older [Haas](/repairs/haas-cnc-machine-repair/vf-series/) imports, and countless other platforms. Routine service is HDD/CF card work, battery replacement, drive amplifier faults, and panel button failures.",
        "machines_paragraph": "Series 0i ships on the broadest cross-section of any Fanuc control — most entry and mid-range [Doosan Puma](/repairs/doosan-cnc-machine-repair/puma/) and all [Doosan Lynx](/repairs/doosan-cnc-machine-repair/lynx/), older [Haas](/repairs/haas-cnc-machine-repair/vf-series/) builds, and a huge fleet of imported Asian-OEM machines. 0i-F is the current generation; 0i-D dominates the 2010-2018 fleet.",
        "failures": [
            "HDD or CF card failure — most common single issue. CF card replacement and SSD-style migration are routine.",
            "Battery loss — leading to parameter and program memory loss.",
            "Drive amplifier faults from heavy production cycles.",
            "Operator-panel button failure on high-cycle keys.",
            "Touchscreen drift on the newer 0i builds with touchscreen panels.",
        ],
        "parts_paragraph": "Series 0i parts are fully current and supported through Fanuc. 0i-A and B are heading toward late-life status; 0i-D and 0i-F are fully current.",
        "recovery_paragraph": "Battery and parameter recovery on 0i is well documented. Capture parameters and PMC ladder logic before any battery work, replace the battery on a powered control, restore parameters as needed. CF card migration to current media is part of the same workflow.",
        "siblings": [
            ("Series 16i / 18i / 21i",    "/repairs/fanuc-cnc-machine-repair/series-16i-18i-21i/"),
            ("Series 30i / 31i / 32i",    "/repairs/fanuc-cnc-machine-repair/series-30i-31i-32i/"),
        ],
    },
    "series-30i-31i-32i": {
        "title":   "Fanuc Series 30i / 31i / 32i / 35i Repair",
        "slug":    "fanuc-series-30i-31i-32i",
        "subtitle":"Series 30i / 31i / 32i / 35i",
        "url":     "/repairs/fanuc-cnc-machine-repair/series-30i-31i-32i/",
        "era":     "2008 through present",
        "intro":   "Fanuc Series 30i, 31i, 32i, and 35i are the current high-end Fanuc family — Model A through current Model B. They ship on higher-end machines that need more axes, more features, or faster processing than 0i provides. In 2026 they're recent enough that hardware failure is uncommon; most service work is integration, networking, MTConnect, and FOCAS-based shop-floor monitoring.",
        "machines_paragraph": "30i and family ship on higher-end machines — most current [Doosan Puma](/repairs/doosan-cnc-machine-repair/puma/) (Puma 2600SY, 3100, 4100, 5100, 700, 800), all [Puma MX and SMX](/repairs/doosan-cnc-machine-repair/puma-mx-smx/) multitasking, [DVF 5-axis](/repairs/doosan-cnc-machine-repair/5-axis-verticals/), [NHM/NHP/HC horizontals](/repairs/doosan-cnc-machine-repair/horizontals/), and the higher-end [DNM verticals](/repairs/doosan-cnc-machine-repair/dnm-verticals/).",
        "failures": [
            "Less hardware failure than earlier generations given relative age.",
            "Networking configuration drift after shop-floor IT changes.",
            "MTConnect and FOCAS setup for shop-floor monitoring.",
            "SSD upgrades on early 30i-A builds with the original HDD.",
            "Touchscreen calibration drift on heavily used panels.",
        ],
        "parts_paragraph": "30i family parts are fully current and supported through Fanuc.",
        "recovery_paragraph": "Backup workflow on 30i is modern — network and USB-based parameter and PMC backup. We document the parameter set at the start of every visit and verify the restore at sign-off.",
        "siblings": [
            ("Series 0i",                "/repairs/fanuc-cnc-machine-repair/series-0i/"),
            ("Series 16i / 18i / 21i",   "/repairs/fanuc-cnc-machine-repair/series-16i-18i-21i/"),
        ],
    },
    "power-mate-i": {
        "title":   "Fanuc Power Mate i Repair",
        "slug":    "fanuc-power-mate-i",
        "subtitle":"Power Mate i",
        "url":     "/repairs/fanuc-cnc-machine-repair/power-mate-i/",
        "era":     "2000 through present",
        "intro":   "Fanuc Power Mate i is the dedicated-axis or servo-positioner control — it handles single-axis positioning applications and dedicated rotary indexers. Service work is mostly drive amplifier, encoder, and parameter recovery rather than full-control issues.",
        "machines_paragraph": "Power Mate i shows up as a dedicated-axis control on rotary tables, indexers, bar feeders, and other auxiliary equipment integrated alongside primary CNC platforms. It often runs as a subordinate control under a primary Fanuc 0i, 30i, or similar host.",
        "failures": [
            "Drive amplifier faults — the most common single issue.",
            "Encoder issues — contamination or signal loss.",
            "Parameter loss from battery failure.",
            "Communication faults with the host CNC.",
        ],
        "parts_paragraph": "Power Mate i parts are supported through Fanuc on current generations. Older Power Mate i builds may have parts heading toward aftermarket.",
        "recovery_paragraph": "Parameter backup on Power Mate i follows the standard Fanuc workflow. The single-axis nature makes the parameter set smaller, but the discipline is the same — backup before any battery or board work, verify the restore.",
        "siblings": [
            ("Series 0i",              "/repairs/fanuc-cnc-machine-repair/series-0i/"),
            ("Series 30i / 31i / 32i", "/repairs/fanuc-cnc-machine-repair/series-30i-31i-32i/"),
        ],
    },
}

# Unified lookup. The dispatcher in render_machine_repair checks this
# dict to decide whether a brand uses the hub-and-spoke template
# (BRAND_HUB_DATA[slug] populated) or the legacy template (no entry).
BRAND_HUB_DATA = {
    "mazak": {
        "browse_series":  _MAZAK_HUB_BROWSE_SERIES,
        "browse_control": _MAZAK_HUB_BROWSE_CONTROL,
        "browse_service": [
            ("Mazak spindle repair",            "/spindle-grinding/mazak-spindle-repair/",
             "bearing-pack rebuilds, taper grinding, balancing, runout verification."),
            ("Mazak way covers",                "/way-covers/mazak-cnc-way-covers/",
             "replacement bellows, telescoping steel, and roll-up covers, built to spec."),
            ("ATC, drive, and alignment work",  "#faq",
             "covered in the FAQ below."),
        ],
        "faq": _MAZAK_HUB_FAQ,
        "series_spokes":  _MAZAK_SERIES_SPOKES,
        "control_spokes": _MAZAK_CONTROL_SPOKES,
        "hero_lede": "We service the Mazak platforms running on Midwest shop floors — Quick Turn lathes, Integrex multitasking, Variaxis 5-axis, VTC and VCN verticals, HCN horizontals, and legacy turning. Find your model below, or browse by series, control generation, or service type.",
        "what_brings": "Most Mazak repair calls fall into a few patterns: ATC faults on production verticals, drive system wear and ballscrew issues on long-bed VTCs, way alignment after a crash, spindle bearing failure on high-RPM VCN work, and pallet-changer issues on HCN horizontals. Control-side, the Matrix generation sees HDD failure as the single most common service item; legacy Mazatrol machines see memory battery and board obsolescence; current Smooth-generation machines come in for integration and configuration work rather than reactive repair. We diagnose what's actually broken before we quote.",
        "how_we_approach": "Mazak machines run Mazatrol, so diagnostics are platform-specific. Our approach starts with the control generation — legacy Mazatrol, Matrix, or Smooth — because the failure modes and the recovery paths are different across the three. From there we move to mechanical: spindle, ATC, drive, alignment. The control spokes below cover the platform-specific recovery procedures for each generation.",
        "browse_control_intro": "Mazak machines span three Mazatrol generations. Pick yours for common faults and parts notes.",
    },
    "haas": {
        "browse_series": [
            ("VF Series",                          "/repairs/haas-cnc-machine-repair/vf-series/",
             "Vertical mills. VF-1 through VF-12, plus YT extended-Y and SS super-speed variants."),
            ("ST Series",                          "/repairs/haas-cnc-machine-repair/st-series/",
             "Production lathes. ST-10 through ST-55, SSY Y-axis variants, DS-30 dual-spindle."),
            ("UMC Series",                         "/repairs/haas-cnc-machine-repair/umc-series/",
             "Universal 5-axis with trunnion table. UMC-350 through UMC-1600, plus SS builds."),
            ("EC Series",                          "/repairs/haas-cnc-machine-repair/ec-series/",
             "Horizontal machining. EC-300 through EC-3000, pallet-pool and 4-axis variants."),
            ("Mini Mill / Toolroom / DT / DM / VM","/repairs/haas-cnc-machine-repair/mini-mill-toolroom/",
             "Compact and toolroom — Mini Mill, TM toolroom, DT drill-tap, DM, VM mold machines."),
            ("Toolroom Lathes (TL / CL)",          "/repairs/haas-cnc-machine-repair/toolroom-lathes/",
             "TL-1 through TL-4 and CL-1 — toolroom-style turning."),
        ],
        "browse_control": [
            ("Haas Classic Control",  "/repairs/haas-cnc-machine-repair/haas-classic-control/",
             "Pre-NGC, through 2014. Keypad, monitor, MOCON board, drive faults, memory battery."),
            ("Haas Next Generation Control (NGC)", "/repairs/haas-cnc-machine-repair/haas-ngc/",
             "2014 to present. SSD upgrades, USB media, networking, MyHaas integration."),
        ],
        "browse_service": [
            ("Haas spindle repair",            "/spindle-grinding/haas-spindle-repair/",
             "bearing-pack rebuilds, taper grinding, balancing, runout verification."),
            ("Haas way covers",                "/way-covers/haas-cnc-way-covers/",
             "replacement bellows, telescoping steel, and roll-up covers, built to spec."),
            ("ATC, drive, and alignment work", "#faq",
             "covered in the FAQ below."),
        ],
        "faq": [
            ("What can you fix on a Haas CNC machine?",
             "Spindle, control, ATC, drive systems, and way alignment are the routine work. We diagnose before we quote — sometimes what looks like a spindle problem is something cheaper."),
            ("Which Haas series do you see most often?",
             "The VF series is by far the most common — VF-1 through VF-5 dominate the Midwest fleet. ST lathes are next, then Mini Mills and TM Toolroom mills. UMC 5-axis and EC horizontals are growing but still less common than VF."),
            ("Do you service older Haas machines with Classic Control?",
             "Yes. Classic Control machines from the early 2000s through 2014 are routine work. The common issues are keypad failures, monitor (CRT or early LCD) failure, MOCON board faults, drive system issues, and memory battery loss. Aftermarket replacement keypads and LCD retrofits are widely available."),
            ("Can you upgrade a Haas Classic Control to NGC?",
             "Haas-authorized Classic-to-NGC upgrades exist for some machine generations through Haas. They're not universally available across the entire Classic fleet. For machines where the upgrade isn't supported, replacement keypads, LCD retrofits, and SSD-style media migration cover most of the same goals."),
            ("How long does a typical Haas machine repair take?",
             "Lead time depends on what's wrong. Diagnostic is fast; parts and rebuild time vary by the job. Classic Control board work depends heavily on parts availability — Haas channels are still good but thinning. NGC service is usually faster because parts are fully current."),
            ("Do you service Haas machines outside Iowa?",
             "Yes. We service shops across Iowa, Illinois, Wisconsin, Minnesota, Nebraska, Missouri, and Texas. Field service is most economical in Iowa and adjacent states; longer-haul jobs typically run ship-in."),
        ],
        "series_spokes":  _HAAS_SERIES_SPOKES,
        "control_spokes": _HAAS_CONTROL_SPOKES,
        "hero_lede": "We service the Haas platforms running on Midwest shop floors — VF and ST production machines, UMC 5-axis, EC horizontals, Mini Mill and Toolroom families. Find your model below, or browse by series, control generation, or service type.",
        "what_brings": "Most Haas repair calls fall into a few patterns: ATC reliability on Mini Mills, spindle bearing wear on SS variants and high-RPM production work, way cover damage from chips or crash, MOCON board failures on Classic-vintage machines, and trunnion calibration on UMC 5-axis. NGC service is mostly SSD upgrades, USB media, and networking; Classic Control service is the harder side — keypad, monitor, MOCON, and battery work all add up.",
        "how_we_approach": "Haas service starts with control generation — Classic Control through 2014, NGC 2014-present — because the failure modes and parts availability differ between the two. From there we move to mechanical: spindle, ATC, drive, alignment. The control spokes below cover the recovery procedures for each generation.",
        "browse_control_intro": "Haas machines span two control generations. Pick yours for common faults and parts notes.",
    },
    "dmg-mori": {
        "browse_series": [
            ("NLX / ALX",                "/repairs/dmg-mori-cnc-machine-repair/nlx-turning/",
             "Universal turning. NLX 1500 through 6000, ALX 1500 through 2500, MC/SMC/Y/SY/MY variants."),
            ("CTX / CLX",                "/repairs/dmg-mori-cnc-machine-repair/ctx-clx-turning/",
             "Turning + TC turn-mill. CLX 350/450/550, CTX 310 through 850, plus TC variants."),
            ("NTX",                      "/repairs/dmg-mori-cnc-machine-repair/ntx/",
             "Integrated mill-turn. NTX 1000 through 4000 with SZ/SZM/S/S2 configurations."),
            ("DMU / DMC",                "/repairs/dmg-mori-cnc-machine-repair/dmu-dmc/",
             "5-axis universal and cube. DMU 50 through 340, monoBLOCK/duoBLOCK, DMC variants."),
            ("NHX / NH",                 "/repairs/dmg-mori-cnc-machine-repair/nhx-horizontals/",
             "Horizontals with pallet changers. NHX 4000 through 10000 plus legacy NH."),
            ("NVX / NV / NVD",           "/repairs/dmg-mori-cnc-machine-repair/nvx-verticals/",
             "Production verticals. NVX 4000 through 7000, NV 4000/5000, NVD DCG-construction."),
            ("CMX / CMX U",              "/repairs/dmg-mori-cnc-machine-repair/cmx/",
             "Entry production verticals. CMX 600V through 1300V, CMX 50U and 70U 5-axis."),
            ("DMP / Milltap",            "/repairs/dmg-mori-cnc-machine-repair/dmp-milltap/",
             "Compact production. DMP 35 through 70, dual-spindle DMP 500, Milltap 700."),
            ("SPRINT / MULTISPRINT",     "/repairs/dmg-mori-cnc-machine-repair/sprint-multisprint/",
             "Swiss-style and production turning. SPRINT 20/32/50/65, MULTISPRINT 25/36."),
        ],
        "browse_control": [
            ("Siemens 840D",   "/repairs/dmg-mori-cnc-machine-repair/siemens-840d/",
             "The most common DMG Mori control. PCU/NCU, drives, battery, MMC on older builds."),
            ("Heidenhain TNC", "/repairs/dmg-mori-cnc-machine-repair/heidenhain-tnc/",
             "Common on DMU/DMC 5-axis. iTNC 530 and TNC 640. Keypad, encoder, drive work."),
            ("CELOS",          "/repairs/dmg-mori-cnc-machine-repair/celos/",
             "The DMG Mori HMI on top of Siemens or Heidenhain. Networking, app integration, IPC."),
        ],
        "browse_service": [
            ("DMG Mori spindle repair",        "/spindle-grinding/dmg-mori-spindle-repair/",
             "bearing-pack rebuilds, taper grinding, balancing, runout verification."),
            ("DMG Mori way covers",            "/way-covers/dmg-mori-cnc-way-covers/",
             "replacement bellows, telescoping steel, and roll-up covers, built to spec."),
            ("ATC, drive, and alignment work", "#faq",
             "covered in the FAQ below."),
        ],
        "faq": [
            ("What can you fix on a DMG Mori CNC machine?",
             "Spindle, control, ATC, drive systems, and way alignment are the routine work across the lineup. DMU and DMC 5-axis trunnion work is brand-specific — we run the kinematic calibration as part of any trunnion-related service. We diagnose before we quote."),
            ("Which DMG Mori series do you see most often?",
             "NLX universal turning and DMU 5-axis are the most common platforms we see. CTX and CLX are growing. NTX integrated mill-turn is higher-value but lower volume. Entry CMX and DMP production come in for ATC and spindle work as they age."),
            ("Do you service DMG Mori machines on older Siemens 840D?",
             "Yes. Original 840D (non-solutionline) is at the late-life stage — board parts heading toward aftermarket — but boards are still serviceable through Siemens and remanufacturing specialists. 840D solutionline parts are fully current."),
            ("Can you service DMU machines with Heidenhain TNC?",
             "Yes. iTNC 530 and TNC 640 are both routine — keypad failure is the most common single service item, plus encoder drift on rotary axes, and the occasional MC board fault on older iTNC 530."),
            ("How long does a typical DMG Mori repair take?",
             "Lead time depends on what's wrong. Diagnostic is fast; parts and rebuild time vary. DMU trunnion work runs longer than a straight VMC repair because of the calibration time. 3 to 5 weeks on most jobs is realistic."),
            ("Do you service DMG Mori machines outside Iowa?",
             "Yes. We service shops across Iowa, Illinois, Wisconsin, Minnesota, Nebraska, Missouri, and Texas."),
        ],
        "series_spokes":  _DMG_MORI_SERIES_SPOKES,
        "control_spokes": _DMG_MORI_CONTROL_SPOKES,
        "hero_lede": "We service the DMG Mori platforms running on Midwest shop floors — NLX and CTX turning, NTX mill-turn, DMU and DMC 5-axis, NHX horizontals, NVX verticals, and the CMX, DMP, and SPRINT production lines. Find your model below, or browse by series, control generation, or service type.",
        "what_brings": "Most DMG Mori repair calls fall into a few patterns: turret indexing and sub-spindle alignment on NLX and CTX turning, B-axis milling spindle wear on NTX multitasking, trunnion calibration on DMU 5-axis, pallet changer issues on NHX, and ATC reliability on the production lines. Control-side, original Siemens 840D builds are seeing more board work as the platform ages; 840D solutionline and CELOS service is mostly integration and configuration.",
        "how_we_approach": "DMG Mori service starts with the control — Siemens 840D, Heidenhain TNC, or CELOS — because the diagnostic and recovery paths differ. From there we move to mechanical, and on 5-axis work we run the kinematic calibration as part of the rebuild rather than handing it back. The control spokes below cover the platform-specific recovery procedures.",
        "browse_control_intro": "DMG Mori machines run on Siemens 840D, Heidenhain TNC, or both, all wrapped in CELOS. Pick the control for common faults and parts notes.",
    },
    "doosan": {
        "browse_series": [
            ("Puma",                       "/repairs/doosan-cnc-machine-repair/puma/",
             "Horizontal turning. Puma 230 through 800, with M/MS/LM/Y/SY variants and TT/GT/TW builds."),
            ("Puma MX / SMX",              "/repairs/doosan-cnc-machine-repair/puma-mx-smx/",
             "Mill-turn multitasking. MX 1600 through 3100 and SMX 2100/2600/3100."),
            ("Puma V / VT / VTR",          "/repairs/doosan-cnc-machine-repair/puma-vertical-turning/",
             "Vertical turning. Puma V400 through V9300 chuckers and VT/VTR ram-type."),
            ("Lynx",                       "/repairs/doosan-cnc-machine-repair/lynx/",
             "Compact turning. Lynx 220 through 300, M/MS/LM/LSY and similar variants."),
            ("DNM",                        "/repairs/doosan-cnc-machine-repair/dnm-verticals/",
             "Vertical machining. DNM 200 through 750, plus the DNM 200/5AX 5-axis variant."),
            ("Horizontals (NHM / NHP / HC)","/repairs/doosan-cnc-machine-repair/horizontals/",
             "Production horizontals. NHM 4000 through 8000, NHP 4000 through 6300, HC 400/500."),
            ("DVF / FM 5-Axis Verticals",  "/repairs/doosan-cnc-machine-repair/5-axis-verticals/",
             "5-axis trunnion verticals. DVF 5000/6500/8000 and FM 200/5AX Linear."),
            ("Swiss-Type / DST",           "/repairs/doosan-cnc-machine-repair/swiss-turning/",
             "Swiss-style precision turning. SwiftTurn 32/38 and the DST series."),
        ],
        "browse_control": [
            ("Fanuc 0i (Doosan)",  "/repairs/fanuc-cnc-machine-repair/series-0i/",
             "Most entry and mid-range Doosan lathes and verticals. 0i-D and 0i-F are dominant."),
            ("Fanuc 30i (Doosan)", "/repairs/fanuc-cnc-machine-repair/series-30i-31i-32i/",
             "Higher-end Puma, Puma MX/SMX, DVF 5-axis, NHM horizontals, larger DNM verticals."),
        ],
        "browse_service": [
            ("Doosan spindle repair",         "/spindle-grinding/doosan-spindle-repair/",
             "bearing-pack rebuilds, taper grinding, balancing, runout verification."),
            ("Doosan way covers",             "/way-covers/doosan-cnc-way-covers/",
             "replacement bellows, telescoping steel, and roll-up covers, built to spec."),
            ("ATC, drive, and alignment work","#faq",
             "covered in the FAQ below."),
        ],
        "faq": [
            ("What can you fix on a Doosan CNC machine?",
             "Turret and sub-spindle work on Puma and Lynx lathes, B-axis spindle and ATC on Puma MX/SMX multitasking, ATC and ballscrew on DNM verticals, pallet changer on NHM horizontals, trunnion calibration on DVF 5-axis. We diagnose before we quote."),
            ("Which Doosan series do you see most often?",
             "The Puma horizontal turning workhorse is the most common Doosan platform on Midwest shop floors — particularly the 2100, 2500, and 2600 sizes. Lynx compact lathes are next, then DNM verticals. Puma MX/SMX multitasking and DVF 5-axis are higher-value but lower frequency."),
            ("Do you service older Doosan machines with Fanuc 0i-C or earlier?",
             "Yes. Doosan ships almost exclusively on Fanuc, so older Doosan machines with Fanuc 16i, 18i, 21i, or 0i-A/B/C controls are routine work. The common issues are PCMCIA media obsolescence, FROM/SRAM battery loss, drive amplifier faults, and monitor failure."),
            ("What's the difference between a Doosan branded machine and a DN Solutions branded one?",
             "DN Solutions is the current corporate name for the same lineup. Pre-rebrand machines say 'Doosan'; post-rebrand machines say 'DN Solutions.' The hardware is the same and the service work is the same."),
            ("How long does a typical Doosan machine repair take?",
             "Lead time depends on what's wrong. Diagnostic is fast; parts and rebuild time vary by the job. Fanuc-side work on older controls depends on Fanuc parts availability and PCMCIA media migration; mechanical work runs 3 to 5 weeks on most jobs."),
            ("Do you service Doosan machines outside Iowa?",
             "Yes. We service shops across Iowa, Illinois, Wisconsin, Minnesota, Nebraska, Missouri, and Texas."),
        ],
        "series_spokes":  _DOOSAN_SERIES_SPOKES,
        "control_spokes": {},  # Doosan controls cross-link to Fanuc canonical spokes
        "hero_lede": "We service the Doosan and DN Solutions platforms running on Midwest shop floors — Puma horizontal turning, Lynx compact lathes, DNM verticals, NHM horizontals, DVF 5-axis, and the multitasking Puma MX and SMX lines. Find your model below, or browse by series, control generation, or service type.",
        "what_brings": "Most Doosan repair calls fall into a few patterns: turret indexing on Puma and Lynx lathes, sub-spindle alignment on SY/SMC twin-spindle variants, B-axis milling spindle wear on Puma MX/SMX multitasking, pallet-changer faults on NHM horizontals, and trunnion calibration on DVF 5-axis. Control-side, Doosan ships almost exclusively on Fanuc — most of the work centers on Fanuc 0i for entry and mid-range builds and Fanuc 30i for higher-end multitasking and 5-axis.",
        "how_we_approach": "Doosan service starts with confirming the model and the Fanuc control generation. Fanuc 0i (Series 0i-A through 0i-F) covers entry and mid-range Puma, Lynx, and DNM. Fanuc 30i (30i-A and 30i-B) covers higher-end Puma, Puma MX/SMX, DVF, NHM, and the larger DNM 4000/5700/6700 builds. Once the control is identified, the mechanical work follows the series patterns.",
        "browse_control_intro": "Doosan ships almost exclusively on Fanuc. Pick the Fanuc generation your Doosan machine runs.",
    },
    "okuma": {
        "browse_series": [
            ("LB / LU Lathes",                "/repairs/okuma-cnc-machine-repair/lb-lu-lathes/",
             "Horizontal lathes. LB 200 through 5000 EX, LU 300 through 8000, live-tool variants."),
            ("Genos",                         "/repairs/okuma-cnc-machine-repair/genos/",
             "'Affordable Excellence' line — Genos L250 through L4000 lathes, M460/M560/M660 verticals."),
            ("MB / MA Verticals",             "/repairs/okuma-cnc-machine-repair/mb-ma-verticals/",
             "Vertical machining workhorses. MB-46V through MB-66V, MA-400 through MA-8000."),
            ("MULTUS",                        "/repairs/okuma-cnc-machine-repair/multus/",
             "B-axis multitasking. MULTUS B200 through B750, U3000 through U5000."),
            ("Twin-Spindle / Twin-Turret",    "/repairs/okuma-cnc-machine-repair/twin-spindle-twin-turret/",
             "2SP-2500H and 2SP-V40, LT 200-MY through LT 2000 EX, historic LT-15/25."),
            ("VTM Vertical Turning",          "/repairs/okuma-cnc-machine-repair/vtm/",
             "Large vertical turning. VTM-65, VTM-100, VTM-120, VTM-180."),
            ("MU 5-Axis / MCR Bridge",        "/repairs/okuma-cnc-machine-repair/v-bridge-mills/",
             "5-axis trunnion (MU-400V through MU-8000V) and bridge mills (MCR-A5C, MCR-BIII)."),
            ("LAW / LFS Heavy Lathes",        "/repairs/okuma-cnc-machine-repair/heavy-lathes/",
             "Heavy-duty turning. LAW 1000 through 3000 and LFS-590 flat-bed turning."),
        ],
        "browse_control": [
            ("OSP-P200",   "/repairs/okuma-cnc-machine-repair/osp-p200/",
             "Roughly 2003 through 2012. HDD, MMC board, keypad, monitor, fan/thermal."),
            ("OSP-P300",   "/repairs/okuma-cnc-machine-repair/osp-p300/",
             "Roughly 2012 through 2020. SSD upgrades, touchscreen drift, Ethernet/USB."),
            ("OSP-P500",   "/repairs/okuma-cnc-machine-repair/osp-p500/",
             "2020 to present. Integration, MTConnect, networking, app deployment."),
            ("OSP Legacy", "/repairs/okuma-cnc-machine-repair/osp-legacy/",
             "Pre-2003 (OSP 5000/7000, U10/U100). Heavy obsolescence — board-level + retrofit work."),
        ],
        "browse_service": [
            ("Okuma spindle repair",          "/spindle-grinding/okuma-spindle-repair/",
             "bearing-pack rebuilds, taper grinding, balancing, runout verification."),
            ("Okuma way covers",              "/way-covers/okuma-cnc-way-covers/",
             "replacement bellows, telescoping steel, and roll-up covers, built to spec."),
            ("ATC, drive, and alignment work","#faq",
             "covered in the FAQ below."),
        ],
        "faq": [
            ("What can you fix on an Okuma CNC machine?",
             "Turret and live-tool indexing on LB/LU lathes, ATC and ballscrew wear on MB/MA verticals, B-axis spindle on MULTUS multitasking, trunnion calibration on MU 5-axis, bridge geometry on MCR. We diagnose before we quote."),
            ("Which Okuma series do you see most often?",
             "LB and LU horizontal lathes are the most common Okuma platforms we see — particularly the LB 3000 EX II and LB 4000/5000 EX builds. MB and MA verticals are next, then MULTUS multitasking. The high-end MU 5-axis and MCR bridge mills are higher-value but lower frequency."),
            ("Do you service older Okuma machines with OSP Legacy or OSP-P200 controls?",
             "Yes. OSP Legacy machines (OSP 5000/7000, U10/U100, pre-2003) are at heavy-obsolescence — most board work runs through remanufacturing specialists, and for some machines the conversation moves to retrofit territory. OSP-P200 is late-life but still well serviced; HDD and MMC board work is the routine."),
            ("Can you upgrade an OSP-P200 to current OSP-P500?",
             "An OSP-P200 to OSP-P500 upgrade isn't a drop-in path. For machines where the control is the bottleneck and the mechanics are sound, a retrofit conversation is appropriate — either an OSP control swap through Okuma where available, or a third-party retrofit. We can scope that conversation as part of a quote."),
            ("How long does a typical Okuma machine repair take?",
             "Lead time depends on what's wrong. Diagnostic is fast; parts and rebuild time vary. OSP Legacy work is the wild-card because of parts situation; OSP-P200 and P300 are predictable; P500 is mostly configuration work."),
            ("Do you service Okuma machines outside Iowa?",
             "Yes. We service shops across Iowa, Illinois, Wisconsin, Minnesota, Nebraska, Missouri, and Texas."),
        ],
        "series_spokes":  _OKUMA_SERIES_SPOKES,
        "control_spokes": _OKUMA_CONTROL_SPOKES,
        "hero_lede": "We service the Okuma platforms running on Midwest shop floors — LB and LU horizontal lathes, MB and MA verticals, MULTUS multitasking, MU 5-axis, MCR bridge mills, and the heavy LAW lathe line. Find your model below, or browse by series, control generation, or service type.",
        "what_brings": "Most Okuma repair calls fall into a few patterns: turret indexing and live-tool faults on LB/LU lathes, ATC drum and spindle work on MB/MA verticals, B-axis milling spindle wear on MULTUS multitasking, trunnion calibration on MU 5-axis, and large-bore spindle work on LAW heavy lathes. Control-side, OSP-P200 sees the most reactive work right now; OSP-P300 is mid-life with SSD upgrades and touchscreen drift; OSP-P500 is mostly integration; OSP Legacy is retrofit territory.",
        "how_we_approach": "Okuma service starts with the OSP generation. OSP Legacy is its own conversation — repair vs. retrofit depending on the machine. P200 is late-life but predictable. P300 and P500 are mostly configuration and integration work. Once the control is identified, the mechanical work follows the series patterns. The control spokes below cover the recovery procedures for each generation.",
        "browse_control_intro": "Okuma machines span four OSP control generations. Pick yours for common faults and parts notes.",
    },
    "fanuc": {
        "browse_series": [
            ("Doosan / DN Solutions", "/repairs/doosan-cnc-machine-repair/",
             "Most Doosan lathes and verticals ship on Fanuc 0i or 30i."),
            ("Haas (older)",          "/repairs/haas-cnc-machine-repair/",
             "Some older Haas imports shipped with Fanuc controls before NGC."),
        ],
        "browse_series_header": "Brands that ship Fanuc controls",
        "browse_series_intro": "Fanuc is primarily a controls vendor — your machine is built by one of these OEMs and runs a Fanuc control. Pick the brand for series-specific notes, or pick a Fanuc generation below.",
        "browse_control": [
            ("Series 0 / 0M / 0T (Pre-i Legacy)", "/repairs/fanuc-cnc-machine-repair/series-0-legacy/",
             "1980s-1990s. Bubble memory, CRT failure, keyboard, MDI board, drive obsolescence."),
            ("Series 6 / 10 / 11 / 12 / 15",      "/repairs/fanuc-cnc-machine-repair/series-6-15-legacy/",
             "1980s-2000s. Similar pattern to Series 0; Series 15 still in active service on larger machines."),
            ("Series 16i / 18i / 21i",            "/repairs/fanuc-cnc-machine-repair/series-16i-18i-21i/",
             "1995-2010. PCMCIA media obsolescence, FROM/SRAM battery, drive amp, monitor."),
            ("Series 0i (A/B/C/D/F)",             "/repairs/fanuc-cnc-machine-repair/series-0i/",
             "2003-present. The ubiquitous Fanuc — HDD/CF card, battery, drive faults, panel buttons."),
            ("Series 30i / 31i / 32i / 35i",      "/repairs/fanuc-cnc-machine-repair/series-30i-31i-32i/",
             "2008-present. Less hardware failure; mostly networking, MTConnect, FOCAS integration."),
            ("Power Mate i",                      "/repairs/fanuc-cnc-machine-repair/power-mate-i/",
             "Dedicated-axis / servo positioner. Drive amp, encoder, parameter loss."),
        ],
        "browse_service": [
            ("Board-level repair",            "#faq",
             "Fanuc service is often board-level, not machine-level. Common on legacy generations."),
            ("PCMCIA media migration",        "#faq",
             "Migrating older 16i/18i/21i media to current paths — covered in the FAQ."),
            ("Parameter and PMC backup",      "#faq",
             "Recovery procedures and backup discipline — covered in the FAQ."),
        ],
        "faq": [
            ("Why is the Fanuc page structured differently?",
             "Fanuc is primarily a controls vendor — the machine your control sits in is built by Doosan, Haas, or another OEM. Our Fanuc hub is organized by control generation rather than machine series because that's the right diagnostic lens for Fanuc service work."),
            ("Which Fanuc generation do you see most often?",
             "Series 0i (specifically 0i-D and 0i-F) is by far the most common Fanuc generation we see on Midwest shop floors. Series 16i/18i/21i is the second-most-common — many late-1990s through 2000s machines still in production. Series 30i is growing as those builds age into routine service. Series 0 and Series 6-15 are deep legacy."),
            ("Do you do board-level Fanuc repair?",
             "Yes. Fanuc service is often board-level — drive amplifiers, MDI boards, MOCON-style motion-control boards. We work through remanufacturing specialists on boards that have gone out of OEM supply, and through Fanuc channels for current-generation parts."),
            ("Can you migrate a 16i/18i/21i from PCMCIA media?",
             "Yes. PCMCIA-to-CF or PCMCIA-to-USB media migration is a routine job on 16i/18i/21i machines where the physical reader is unreliable or the media is no longer sourcing reliably. We do the migration alongside any other service work on the control."),
            ("How long does Fanuc service take?",
             "Lead time depends on the generation. Current 0i-F and 30i parts are fully supported, so service is fast. 16i/18i/21i depends on Fanuc parts availability — most are still serviceable but the supply chain is thinning. Series 0 and Series 6-15 work runs through remanufacturing specialists and the timeline tracks their inventory."),
            ("Do you service Fanuc-controlled machines outside Iowa?",
             "Yes. We service shops across Iowa, Illinois, Wisconsin, Minnesota, Nebraska, Missouri, and Texas. For board-level Fanuc work, ship-in to our Waterloo facility is usually the right path."),
        ],
        "series_spokes":  {},  # Fanuc has no series; the hub flips this section
        "control_spokes": _FANUC_CONTROL_SPOKES,
        "hero_lede": "Fanuc is primarily a controls vendor — your machine is built by Doosan, Haas, or another OEM and runs a Fanuc control. We service the full Fanuc family from deep-legacy Series 0 through current 0i-F and 30i-B. Find your control below, or browse by service type.",
        "what_brings": "Most Fanuc service splits between three patterns. Deep-legacy Series 0, 6, 10, 11, 12, and 15 — board-level work through remanufacturing specialists, bubble memory recovery on the oldest builds. Mid-life Series 16i/18i/21i — PCMCIA media migration, FROM/SRAM battery, drive amplifier, and monitor work. Current Series 0i and 30i — HDD/CF card, battery, networking, MTConnect, and FOCAS integration. The diagnostic lens is the generation, not the machine.",
        "how_we_approach": "Fanuc service starts with confirming the generation. From there it's a fork: legacy generations (Series 0 through Series 15) go through board-level repair or remanufacturing specialists; mid-life 16i/18i/21i is parts availability and media migration; current 0i and 30i is mostly software, networking, and configuration. The control spokes below cover each generation in detail.",
        "browse_control_intro": "Fanuc spans six control generations from the early 1980s through current production. Pick yours for common faults and parts notes.",
    },
}


# Spindle and way-covers hub-and-spoke content for the 6 priority brands.
# Mirrors BRAND_HUB_DATA structure but service-specific.
from _brand_spindle_data import SPINDLE_HUB_DATA
from _brand_way_covers_data import WAY_COVERS_HUB_DATA


def _models_for_spoke(spoke_url):
    """Pull every model entry from machines.json whose spoke_url matches.
    Falls back to matching the corresponding repair spoke URL since
    machines.json only stores repair-section spoke URLs; the spindle /
    way-covers spokes share the same series structure."""
    p = os.path.join(REPO, "src", "data", "machines.json")
    with open(p) as f:
        data = json.load(f)
    # Map spindle/way-covers spoke URLs back to the canonical repair
    # spoke URL stored in machines.json so the model list resolves.
    repair_url = re.sub(
        r"^/spindle-grinding/([\w-]+)-spindle-repair/",
        r"/repairs/\1-cnc-machine-repair/",
        spoke_url,
    )
    repair_url = re.sub(
        r"^/way-covers/([\w-]+)-cnc-way-covers/",
        r"/repairs/\1-cnc-machine-repair/",
        repair_url,
    )
    return [m for m in data.get("machines", []) if m.get("spoke_url") == repair_url]


def render_series_spoke(spoke_data, brand_display_name, brand_hub_url, brand_slug, brand_so):
    """Generic series-spoke renderer used by every brand's hub-and-spoke
    architecture. spoke_data is one entry from BRAND_HUB_DATA[brand_slug]
    ['series_spokes']. brand_so is the brand's services_offered dict so we
    only emit cross-links to spindle and way-covers when those exist."""
    s = spoke_data
    models = _models_for_spoke(s["url"])
    model_lis = "".join(f'<li>{html.escape(m["model"])}</li>' for m in models)
    failure_bullets = "\n".join(f"- {html.escape(f)}" for f in s["failures"])
    sibling_cards = "".join(
        f'<li><a href="{u}"><span>{html.escape(n)}</span></a></li>'
        for n, u in s["siblings"]
    )
    # Add spindle / way-covers cross-links when the brand offers them
    extra_links = ""
    if brand_so.get("spindle"):
        extra_links += (
            f'<li><a href="/spindle-grinding/{brand_slug}-spindle-repair/">'
            f'<span>{html.escape(brand_display_name)} spindle repair</span></a></li>'
        )
    if brand_so.get("way_covers") and not spoke_data.get("skip_way_covers"):
        extra_links += (
            f'<li><a href="/way-covers/{brand_slug}-cnc-way-covers/">'
            f'<span>{html.escape(brand_display_name)} way covers</span></a></li>'
        )

    fm_lines = [
        '---',
        f'title: "{s["title"]}"',
        f'meta_description: "{html.escape(brand_display_name)} {s["subtitle"]} repair across the Midwest. Models, failure patterns, control notes."',
        f'h1: "{s["title"]}"',
        f'slug: "{s["slug"]}"',
        'page_type: "cnc_spindle"',
        'schema_data:',
        '  service:',
        '    "@type": Service',
        f'    serviceType: "{s["title"]}"',
        '    provider:',
        '      "@id": "#org"',
        '    areaServed:',
        '      - Iowa',
        '      - Illinois',
        '      - Minnesota',
        '      - Wisconsin',
        '      - Nebraska',
        '      - Missouri',
        '      - Texas',
        '  breadcrumb:',
        '    "@type": BreadcrumbList',
        '    itemListElement:',
        '      - { position: 1, name: Home, item: "https://midwestcncservices.com/" }',
        '      - { position: 2, name: "Repairs", item: "https://midwestcncservices.com/repairs/" }',
        f'      - {{ position: 3, name: "{brand_display_name} CNC Machine Repair", item: "https://midwestcncservices.com{brand_hub_url}" }}',
        f'      - {{ position: 4, name: "{s["subtitle"]}", item: "https://midwestcncservices.com{s["url"]}" }}',
        '---',
        '',
    ]

    body = (
        f'<section class="brand-hero">\n'
        f'  <div class="brand-hero-overlay" aria-hidden="true"></div>\n'
        f'  <div class="brand-hero-content">\n'
        f'    <p class="eyebrow">{html.escape(brand_display_name)} Series Repair</p>\n'
        f'    <h1>{html.escape(s["title"])}</h1>\n'
        f'    <p>{html.escape(s["intro"])}</p>\n'
        f'    <div class="cta-row">\n'
        f'      <a class="cta-button" href="/get-a-quote/">Get a Quote</a>\n'
        f'      <a class="cta-phone" href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a>\n'
        f'    </div>\n'
        f'  </div>\n'
        f'</section>\n\n'

        f'## Models in this series we service\n\n'
        f'<ul class="model-chips">{model_lis}</ul>\n\n'

        f'## Common failure patterns\n\n'
        f'{failure_bullets}\n\n'

        f'## Controls used on this series\n\n'
        f'{s["controls_paragraph"]}\n\n'

        f'## Lead time\n\n'
        f'Lead time depends on the model, the failure mode, and parts availability. Diagnostic is fast; full rebuilds run 3 to 5 weeks on most jobs. We scope each job individually rather than quoting a generic window.\n\n'

        f'[Get a Quote](/get-a-quote/) · [{PHONE_DISPLAY}](tel:{PHONE_TEL})\n\n'

        f'## Related\n\n'
        f'<ul class="related-grid">'
        f'<li><a href="{brand_hub_url}"><span>All {html.escape(brand_display_name)} repair</span></a></li>'
        f'{sibling_cards}'
        f'{extra_links}'
        f'</ul>\n'
    )
    return "\n".join(fm_lines) + body


def render_control_spoke(spoke_data, brand_display_name, brand_hub_url):
    """Generic control-generation spoke renderer."""
    s = spoke_data
    failure_bullets = "\n".join(f"- {html.escape(f)}" for f in s["failures"])
    sibling_cards = "".join(
        f'<li><a href="{u}"><span>{html.escape(n)}</span></a></li>'
        for n, u in s["siblings"]
    )

    fm_lines = [
        '---',
        f'title: "{s["title"]}"',
        f'meta_description: "{s["subtitle"]} control repair across the Midwest. {s["era"]}."',
        f'h1: "{s["title"]}"',
        f'slug: "{s["slug"]}"',
        'page_type: "cnc_spindle"',
        'schema_data:',
        '  service:',
        '    "@type": Service',
        f'    serviceType: "{s["title"]}"',
        '    provider:',
        '      "@id": "#org"',
        '    areaServed:',
        '      - Iowa',
        '      - Illinois',
        '      - Minnesota',
        '      - Wisconsin',
        '      - Nebraska',
        '      - Missouri',
        '      - Texas',
        '  breadcrumb:',
        '    "@type": BreadcrumbList',
        '    itemListElement:',
        '      - { position: 1, name: Home, item: "https://midwestcncservices.com/" }',
        '      - { position: 2, name: "Repairs", item: "https://midwestcncservices.com/repairs/" }',
        f'      - {{ position: 3, name: "{brand_display_name} CNC Machine Repair", item: "https://midwestcncservices.com{brand_hub_url}" }}',
        f'      - {{ position: 4, name: "{s["subtitle"]}", item: "https://midwestcncservices.com{s["url"]}" }}',
        '---',
        '',
    ]

    body = (
        f'<section class="brand-hero">\n'
        f'  <div class="brand-hero-overlay" aria-hidden="true"></div>\n'
        f'  <div class="brand-hero-content">\n'
        f'    <p class="eyebrow">{html.escape(brand_display_name)} Control Generation</p>\n'
        f'    <h1>{html.escape(s["title"])}</h1>\n'
        f'    <p>{html.escape(s["intro"])}</p>\n'
        f'    <div class="cta-row">\n'
        f'      <a class="cta-button" href="/get-a-quote/">Get a Quote</a>\n'
        f'      <a class="cta-phone" href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a>\n'
        f'    </div>\n'
        f'  </div>\n'
        f'</section>\n\n'

        f'## Machines this control shipped on\n\n'
        f'{s["machines_paragraph"]}\n\n'

        f'## Common failures and fixes\n\n'
        f'{failure_bullets}\n\n'

        f'## Parts availability\n\n'
        f'{s["parts_paragraph"]}\n\n'

        f'## Battery, memory, and parameter recovery\n\n'
        f'{s["recovery_paragraph"]}\n\n'

        f'[Get a Quote](/get-a-quote/) · [{PHONE_DISPLAY}](tel:{PHONE_TEL})\n\n'

        f'## Related\n\n'
        f'<ul class="related-grid">'
        f'<li><a href="{brand_hub_url}"><span>All {html.escape(brand_display_name)} repair</span></a></li>'
        f'{sibling_cards}'
        f'</ul>\n'
    )
    return "\n".join(fm_lines) + body


def _emit_brand_spokes(brand, brand_index):
    """Write all spoke markdown files for the given brand (series + control)
    into src/content/machine-repair/. Returns the count written."""
    hub_data = BRAND_HUB_DATA.get(brand["slug"])
    if not hub_data:
        return 0
    out_dir = os.path.join(REPO, "src", "content", "machine-repair")
    name = brand["brand_display_name"]
    hub_url = f"/repairs/{brand['slug']}-cnc-machine-repair/"
    so = brand.get("services_offered", {})
    n = 0
    for key, spoke in hub_data.get("series_spokes", {}).items():
        md = render_series_spoke(spoke, name, hub_url, brand["slug"], so)
        path = os.path.join(out_dir, f"{spoke['slug']}.md")
        with open(path, "w") as f:
            f.write(md)
        n += 1
    for key, spoke in hub_data.get("control_spokes", {}).items():
        md = render_control_spoke(spoke, name, hub_url)
        path = os.path.join(out_dir, f"{spoke['slug']}.md")
        with open(path, "w") as f:
            f.write(md)
        n += 1
    return n


def _emit_brand_spindle_spokes(brand, brand_index):
    """Write all SPINDLE spoke markdown files for the given brand
    (series + control) into src/content/spindle-brands/. Returns the
    count written. Spindle-specific content lives in SPINDLE_HUB_DATA
    in scripts/_brand_spindle_data.py."""
    hub_data = SPINDLE_HUB_DATA.get(brand["slug"])
    if not hub_data:
        return 0
    out_dir = os.path.join(REPO, "src", "content", "spindle-brands")
    name = brand["brand_display_name"]
    hub_url = f"/spindle-grinding/{brand['slug']}-spindle-repair/"
    so = brand.get("services_offered", {})
    n = 0
    for key, spoke in hub_data.get("series_spokes", {}).items():
        md = render_series_spoke(spoke, name, hub_url, brand["slug"], so)
        path = os.path.join(out_dir, f"{spoke['slug']}.md")
        with open(path, "w") as f:
            f.write(md)
        n += 1
    for key, spoke in hub_data.get("control_spokes", {}).items():
        md = render_control_spoke(spoke, name, hub_url)
        path = os.path.join(out_dir, f"{spoke['slug']}.md")
        with open(path, "w") as f:
            f.write(md)
        n += 1
    return n


def _emit_brand_way_covers_spokes(brand, brand_index):
    """Write all WAY-COVERS spoke markdown files for the given brand
    (series + control) into src/content/way-covers/. Returns the count
    written. Way-covers content lives in WAY_COVERS_HUB_DATA in
    scripts/_brand_way_covers_data.py."""
    hub_data = WAY_COVERS_HUB_DATA.get(brand["slug"])
    if not hub_data:
        return 0
    out_dir = os.path.join(REPO, "src", "content", "way-covers")
    name = brand["brand_display_name"]
    hub_url = f"/way-covers/{brand['slug']}-cnc-way-covers/"
    so = brand.get("services_offered", {})
    n = 0
    for key, spoke in hub_data.get("series_spokes", {}).items():
        md = render_series_spoke(spoke, name, hub_url, brand["slug"], so)
        path = os.path.join(out_dir, f"{spoke['slug']}.md")
        with open(path, "w") as f:
            f.write(md)
        n += 1
    for key, spoke in hub_data.get("control_spokes", {}).items():
        md = render_control_spoke(spoke, name, hub_url)
        path = os.path.join(out_dir, f"{spoke['slug']}.md")
        with open(path, "w") as f:
            f.write(md)
        n += 1
    return n


def render_brand_way_covers_hub(brand, g, brand_index):
    """Way-covers equivalent of render_brand_spindle_hub. Looks up
    way-covers content in WAY_COVERS_HUB_DATA. Same template as the
    spindle hub but with the way-covers hub URL, way-covers eyebrow / H1,
    and way-covers-specific content. Fanuc uses the flipped Browse-by-
    Series header ('Brands that ship Fanuc controls')."""
    name = brand["brand_display_name"]
    slug = brand["slug"]
    hub_data = WAY_COVERS_HUB_DATA.get(slug, {})

    h1_text = f"{name} CNC Way Cover Replacement"
    eyebrow_text = f"{name} Way Covers"
    canonical_path = f"/way-covers/{slug}-cnc-way-covers/"

    is_draft = bool(brand.get("way_covers_verification_pending"))
    verification_msg = None
    if is_draft:
        verification_msg = (
            "Awaiting Ken confirmation that Midwest CNC makes way covers / "
            "shielding for press brakes (Amada) and laser cutters (Trumpf) — "
            "these aren't conventional CNC mill way covers."
        )

    meta_desc = (
        f"Expert {name} way cover replacement across the Midwest. "
        f"Browse by series, by control generation, or by service. "
        f"Find your model with our machine lookup."
    )

    fm = front_matter(
        brand,
        title=f"{name} CNC Way Covers",
        h1=h1_text,
        meta_description=meta_desc,
        service_type=f"{name} CNC Way Cover Manufacturing",
        canonical_path=canonical_path,
        crumb_middle=("Way Covers", "/way-covers/"),
        crumb_leaf=f"{name} CNC Way Covers",
        draft=is_draft,
        verification_pending=verification_msg,
    )

    img_path, img_alt = hero_image_for(brand, "way_covers")
    hero_lede = hub_data.get("hero_lede",
        f"{name} way covers manufactured to spec across the Midwest. "
        f"Find your model with the lookup below, or browse by series, "
        f"control generation, or service type."
    )
    hero = build_brand_hero_html(
        eyebrow_text, h1_text, html.escape(hero_lede), img_path, img_alt,
    )
    hero += machine_lookup_html()

    series_lis = "".join(
        f'<li><a href="{u}"><strong>{html.escape(label)}</strong> &mdash; {html.escape(desc)}</a></li>'
        for label, u, desc in hub_data.get("browse_series", [])
    )
    control_lis = "".join(
        f'<li><a href="{u}"><strong>{html.escape(label)}</strong> &mdash; {html.escape(desc)}</a></li>'
        for label, u, desc in hub_data.get("browse_control", [])
    )
    service_lis = "".join(
        f'<li><a href="{u}"><strong>{html.escape(label)}</strong> &mdash; {html.escape(desc)}</a></li>'
        for label, u, desc in hub_data.get("browse_service", [])
    )

    faq_items = []
    for q, a in hub_data.get("faq", []):
        faq_items.append(
            f'<details class="faq-item">\n'
            f'  <summary>{html.escape(q)}</summary>\n'
            f'  <div class="faq-answer"><p>{html.escape(a)}</p></div>\n'
            f'</details>'
        )
    faq_schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in hub_data.get("faq", [])
        ],
    }
    faq_schema_script = (
        '\n<script type="application/ld+json">\n'
        + json.dumps(faq_schema, indent=2, ensure_ascii=False)
        + '\n</script>\n'
    )

    trust = trust_block(
        g, brand["page_type"], brand_index,
        "replacement way covers and the retrofit time",
    )
    cross_links = brand_cross_links_section(brand, {})
    related = related_block_way_covers(brand)

    series_header = hub_data.get("browse_series_header", "Browse by Series")
    series_intro  = hub_data.get("browse_series_intro",
        f"Pick the {name} platform you run for cover-style and dimensional notes specific to that series.")
    browse_series_section = ""
    if hub_data.get("browse_series"):
        browse_series_section = (
            f'<h2 id="browse-by-series">{html.escape(series_header)}</h2>\n'
            f'<p>{html.escape(series_intro)}</p>\n'
            f'<ul class="browse-list">{series_lis}</ul>\n'
        )
    control_intro = hub_data.get("browse_control_intro",
        f"{name} way cover sourcing patterns differ by machine era. Pick yours for parts-availability and fabrication notes.")
    browse_control_section = ""
    if hub_data.get("browse_control"):
        browse_control_section = (
            f'<h2 id="browse-by-control">Browse by Era</h2>\n'
            f'<p>{html.escape(control_intro)}</p>\n'
            f'<ul class="browse-list">{control_lis}</ul>\n'
        )
    browse_service_section = ""
    if hub_data.get("browse_service"):
        browse_service_section = (
            f'<h2 id="browse-by-service">Browse by Service</h2>\n'
            f'<ul class="browse-list">{service_lis}</ul>\n'
        )

    what_brings_para = hub_data.get("what_brings",
        f"Most {name} way cover orders fall into platform-specific patterns. We match the original cover or build to spec for the operating conditions.")
    what_brings = (
        f'<h2 id="what-brings-orders-in">What brings {name} way cover orders in</h2>\n'
        f'<p>{what_brings_para}</p>\n'
    )

    how_para = hub_data.get("how_we_approach",
        f"Our approach starts with confirming the platform, the cover style, and the dimensions. From there we route to OEM-spec or custom fabrication depending on parts availability and timing.")
    how_we_approach = (
        f'<h2 id="how-we-approach">How we approach {name} way cover orders</h2>\n'
        f'<p>{how_para}</p>\n'
    )

    lead_time = (
        f'<h2 id="lead-time-process">Lead Time &amp; Process</h2>\n'
        f"<p>2 to 4 weeks on most way cover orders, depending on dimensions, material, and the configuration coordination needed. Complex multi-axis cover sets can run slightly longer. Our three-step workflow keeps it transparent:</p>\n"
        f'<ol class="process-steps">\n'
        f'  <li><strong>Send measurements or the original cover.</strong> Call <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a> or use the quote form. Bring us dimensions, the original part, or way-system measurements.</li>\n'
        f'  <li><strong>Quote the build.</strong> We confirm style (bellows, telescoping steel, roll-up), material, and lead time. Routing between OEM-spec and custom fabrication happens here.</li>\n'
        f'  <li><strong>Fabricate &amp; ship.</strong> On approval we build to spec and ship anywhere in the continental US. Rush options are available.</li>\n'
        f'</ol>\n'
    )

    faq_section = (
        f'<h2 id="faq">Frequently Asked Questions</h2>\n'
        f'<div class="faq-list">\n'
        + "\n".join(faq_items) + "\n"
        + '</div>\n'
        + faq_schema_script
    )

    return (
        fm + hero
        + browse_series_section + browse_control_section + browse_service_section
        + what_brings + how_we_approach
        + lead_time + "\n" + trust + "\n" + faq_section + "\n"
        + cross_links + "\n" + related + "\n"
    )


def render_brand_spindle_hub(brand, g, brands_by_slug, brand_index):
    """Spindle equivalent of render_brand_hub. Looks up spindle content
    in SPINDLE_HUB_DATA. Same template as the repair hub but with the
    spindle hub URL, spindle eyebrow / H1, and spindle-specific content."""
    name = brand["brand_display_name"]
    slug = brand["slug"]
    hub_data = SPINDLE_HUB_DATA.get(slug, {})

    h1_text, eyebrow_text = make_h1_and_eyebrow(brand)
    if not h1_text:
        h1_text = f"{name} Spindle Repair & Grinding"
    eyebrow_text = f"{name} Spindle Service"
    canonical_path = brand["current_url"]

    meta_desc = (
        f"Expert {name} spindle repair across the Midwest. Browse by "
        f"series, by control generation, or by service. Find your model "
        f"with our machine lookup."
    )

    fm = front_matter(
        brand,
        title=f"{name} Spindle Repair",
        h1=h1_text,
        meta_description=meta_desc,
        service_type=f"{name} CNC Spindle Repair and Grinding",
        canonical_path=canonical_path,
        crumb_middle=("Spindle Grinding", "/spindle-grinding/"),
        crumb_leaf=f"{name} Spindle Repair",
    )

    img_path, img_alt = hero_image_for(brand, "spindle")
    hero_lede = hub_data.get("hero_lede",
        f"{name} spindle service across the Midwest. Find your model "
        f"with the lookup below, or browse by series, control generation, "
        f"or service type."
    )
    hero = build_brand_hero_html(
        eyebrow_text, h1_text, html.escape(hero_lede), img_path, img_alt,
    )
    hero += machine_lookup_html()

    # Browse-by-series list (Fanuc uses flipped header)
    series_lis = "".join(
        f'<li><a href="{u}"><strong>{html.escape(label)}</strong> &mdash; {html.escape(desc)}</a></li>'
        for label, u, desc in hub_data.get("browse_series", [])
    )
    control_lis = "".join(
        f'<li><a href="{u}"><strong>{html.escape(label)}</strong> &mdash; {html.escape(desc)}</a></li>'
        for label, u, desc in hub_data.get("browse_control", [])
    )
    service_lis = "".join(
        f'<li><a href="{u}"><strong>{html.escape(label)}</strong> &mdash; {html.escape(desc)}</a></li>'
        for label, u, desc in hub_data.get("browse_service", [])
    )

    # FAQ accordions
    faq_items = []
    for q, a in hub_data.get("faq", []):
        faq_items.append(
            f'<details class="faq-item">\n'
            f'  <summary>{html.escape(q)}</summary>\n'
            f'  <div class="faq-answer"><p>{html.escape(a)}</p></div>\n'
            f'</details>'
        )
    faq_schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in hub_data.get("faq", [])
        ],
    }
    faq_schema_script = (
        '\n<script type="application/ld+json">\n'
        + json.dumps(faq_schema, indent=2, ensure_ascii=False)
        + '\n</script>\n'
    )

    trust = trust_block(g, brand["page_type"], brand_index, "a new spindle")
    cross_links = brand_cross_links_section(brand, brands_by_slug)
    related = related_block_cnc(brand, brands_by_slug)

    series_header = hub_data.get("browse_series_header", "Browse by Series")
    series_intro  = hub_data.get("browse_series_intro",
        f"Pick the {name} platform you run for spindle failure patterns specific to that series.")
    browse_series_section = ""
    if hub_data.get("browse_series"):
        browse_series_section = (
            f'<h2 id="browse-by-series">{html.escape(series_header)}</h2>\n'
            f'<p>{html.escape(series_intro)}</p>\n'
            f'<ul class="browse-list">{series_lis}</ul>\n'
        )
    control_intro = hub_data.get("browse_control_intro",
        f"{name} spindles pair with multiple control generations. Pick yours for parameter notes.")
    browse_control_section = ""
    if hub_data.get("browse_control"):
        browse_control_section = (
            f'<h2 id="browse-by-control">Browse by Control Generation</h2>\n'
            f'<p>{html.escape(control_intro)}</p>\n'
            f'<ul class="browse-list">{control_lis}</ul>\n'
        )
    browse_service_section = ""
    if hub_data.get("browse_service"):
        browse_service_section = (
            f'<h2 id="browse-by-service">Browse by Service</h2>\n'
            f'<ul class="browse-list">{service_lis}</ul>\n'
        )

    what_brings_para = hub_data.get("what_brings",
        f"Most {name} spindle calls fall into platform-specific failure patterns. We diagnose each spindle before quoting.")
    what_brings = (
        f'<h2 id="what-brings-spindles-in">What brings {name} spindles in for service</h2>\n'
        f'<p>{what_brings_para}</p>\n'
    )

    how_para = hub_data.get("how_we_approach",
        f"Our approach starts with confirming the platform and the control generation. On the bench we tear down, inspect, source parts, rebuild, balance, and verify runout before sign-off.")
    how_we_approach = (
        f'<h2 id="how-we-approach">How we approach {name} spindle service</h2>\n'
        f'<p>{how_para}</p>\n'
    )

    lead_time = (
        f'<h2 id="lead-time-process">Lead Time &amp; Process</h2>\n'
        f"<p>Lead time on spindle work depends on the platform, the failure mode, and parts availability. Diagnostic is fast; full rebuilds run 3 to 5 weeks on most jobs. Our three-step workflow keeps it transparent:</p>\n"
        f'<ol class="process-steps">\n'
        f'  <li><strong>Contact us.</strong> Call <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a> or use the quote form. Tell us the machine, the spindle symptoms, and how urgent it is.</li>\n'
        f'  <li><strong>Review &amp; quote.</strong> We confirm the model and control generation, scope the spindle work, and send back a price and realistic lead time within one business day on most inquiries.</li>\n'
        f'  <li><strong>Rebuild, verify, ship.</strong> We rebuild on the bench, verify balance and runout at sign-off, run kinematic verification on multitasking and 5-axis platforms, and return the spindle ready to install.</li>\n'
        f'</ol>\n'
    )

    faq_section = (
        f'<h2 id="faq">Frequently Asked Questions</h2>\n'
        f'<div class="faq-list">\n'
        + "\n".join(faq_items) + "\n"
        + '</div>\n'
        + faq_schema_script
    )

    return (
        fm + hero
        + browse_series_section + browse_control_section + browse_service_section
        + what_brings + how_we_approach
        + lead_time + "\n" + trust + "\n" + faq_section + "\n"
        + cross_links + "\n" + related + "\n"
    )


def render_brand_hub(brand, g, brand_index):
    """Generic brand-hub renderer. Looks up the brand's content in
    BRAND_HUB_DATA. Keeps the brand-hero from the previous iteration,
    adds the MachineLookup widget, three Browse-by lenses (Series /
    Control / Service), expanded FAQ. Fanuc uses a flipped Browse-by-
    Series ('Brands that ship Fanuc controls') because Fanuc is a
    controls vendor."""
    name = brand["brand_display_name"]
    slug = brand["slug"]
    hub_data = BRAND_HUB_DATA.get(slug, {})

    h1_text = f"{name} CNC Machine Repair & Service"
    eyebrow_text = "CNC Machine Repair"
    canonical_path = f"/repairs/{slug}-cnc-machine-repair/"

    meta_desc = (
        f"Expert {name} CNC machine repair across the Midwest. "
        f"Browse by series, by control generation, or by service. "
        f"Find your model with our machine lookup."
    )

    fm = front_matter(
        brand,
        title=f"{name} CNC Machine Repair",
        h1=h1_text,
        meta_description=meta_desc,
        service_type=f"{name} CNC Machine Repair and Service",
        canonical_path=canonical_path,
        crumb_middle=("Repairs", "/repairs/"),
        crumb_leaf=f"{name} CNC Machine Repair",
    )

    img_path, img_alt = hero_image_for(brand, "machine_repair")
    bg_img_html = (
        f'<img class="brand-hero-bg" src="{img_path}" alt="{html.escape(img_alt)}" loading="eager">\n'
        if img_path else ""
    )
    hero_lede = hub_data.get("hero_lede",
        f"We service {name} CNC platforms across the Midwest. Find your "
        f"model with the lookup below, or browse by series, control "
        f"generation, or service type."
    )

    # Browse-by-series list (Fanuc flips this to "Brands that ship Fanuc controls")
    series_lis = "".join(
        f'<li><a href="{u}"><strong>{html.escape(label)}</strong> — {html.escape(desc)}</a></li>'
        for label, u, desc in hub_data.get("browse_series", [])
    )
    control_lis = "".join(
        f'<li><a href="{u}"><strong>{html.escape(label)}</strong> — {html.escape(desc)}</a></li>'
        for label, u, desc in hub_data.get("browse_control", [])
    )
    service_lis = "".join(
        f'<li><a href="{u}"><strong>{html.escape(label)}</strong> — {html.escape(desc)}</a></li>'
        for label, u, desc in hub_data.get("browse_service", [])
    )

    # FAQ accordions
    faq_items = []
    for q, a in hub_data.get("faq", []):
        faq_items.append(
            f'<details class="faq-item">\n'
            f'  <summary>{html.escape(q)}</summary>\n'
            f'  <div class="faq-answer"><p>{html.escape(a)}</p></div>\n'
            f'</details>'
        )
    faq_schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in hub_data.get("faq", [])
        ],
    }
    faq_schema_script = (
        '\n<script type="application/ld+json">\n'
        + json.dumps(faq_schema, indent=2, ensure_ascii=False)
        + '\n</script>\n'
    )

    trust = trust_block(g, brand["page_type"], brand_index, "a replacement machine")
    cross_links = brand_cross_links_section(brand, {})
    related = related_block_machine_repair(brand)

    hero = (
        f'<section class="brand-hero">\n'
        f'{bg_img_html}'
        f'  <div class="brand-hero-overlay" aria-hidden="true"></div>\n'
        f'  <div class="brand-hero-content">\n'
        f'    <p class="eyebrow">{eyebrow_text}</p>\n'
        f'    <h1>{html.escape(h1_text)}</h1>\n'
        f'    <p>{html.escape(hero_lede)}</p>\n'
        f'    <div class="cta-row">\n'
        f'      <a class="cta-button" href="/get-a-quote/">Get a Quote</a>\n'
        f'      <a class="cta-phone" href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a>\n'
        f'    </div>\n'
        f'  </div>\n'
        f'</section>\n\n'
        f'{machine_lookup_html()}\n'
    )

    # Series section — Fanuc flips this header (no series; it's controls-only)
    series_header = hub_data.get("browse_series_header", "Browse by Series")
    series_intro  = hub_data.get("browse_series_intro",
        f"Pick the {name} platform you run for failure patterns specific to that series.")
    browse_series_section = ""
    if hub_data.get("browse_series"):
        browse_series_section = (
            f'<h2 id="browse-by-series">{html.escape(series_header)}</h2>\n'
            f'<p>{html.escape(series_intro)}</p>\n'
            f'<ul class="browse-list">{series_lis}</ul>\n'
        )
    control_intro = hub_data.get("browse_control_intro",
        f"{name} machines span multiple control generations. Pick yours for common faults and parts notes.")
    browse_control_section = ""
    if hub_data.get("browse_control"):
        browse_control_section = (
            f'<h2 id="browse-by-control">Browse by Control Generation</h2>\n'
            f'<p>{html.escape(control_intro)}</p>\n'
            f'<ul class="browse-list">{control_lis}</ul>\n'
        )
    browse_service_section = ""
    if hub_data.get("browse_service"):
        browse_service_section = (
            f'<h2 id="browse-by-service">Browse by Service</h2>\n'
            f'<ul class="browse-list">{service_lis}</ul>\n'
        )

    what_brings_para = hub_data.get("what_brings",
        f"Most {name} repair calls fall into a few platform-specific patterns. We diagnose what's actually broken before we quote — sometimes what looks like a spindle problem is something cheaper to fix.")
    what_brings = (
        f'<h2 id="what-brings-machines-in-for-repair">What brings {name} machines in for repair</h2>\n'
        f'<p>{what_brings_para}</p>\n'
    )

    how_para = hub_data.get("how_we_approach",
        f"Our approach starts with confirming the model and control generation, then scoping the mechanical work. The control spokes below cover the platform-specific recovery procedures for each generation.")
    how_we_approach = (
        f'<h2 id="how-we-approach-repair-work">How we approach {name} repair work</h2>\n'
        f'<p>{how_para}</p>\n'
    )

    lead_time = (
        f'<h2 id="lead-time-process">Lead Time &amp; Process</h2>\n'
        f"<p>Lead time on machine repair depends on what's wrong — diagnostic is fast, but parts and rebuild time vary by the job. Our three-step workflow keeps it transparent:</p>\n"
        f'<ol class="process-steps">\n'
        f'  <li><strong>Contact us.</strong> Call <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a> or use the quote form. Tell us the machine, the symptoms, and how urgent it is.</li>\n'
        f'  <li><strong>Review &amp; quote.</strong> We confirm the model and control generation, scope the work, and send back a price and realistic lead time within one business day on most inquiries.</li>\n'
        f'  <li><strong>Approve &amp; rebuild.</strong> We complete the repair, verify it back to spec, and return the machine ready to run.</li>\n'
        f'</ol>\n'
    )

    faq_section = (
        f'<h2 id="faq">Frequently Asked Questions</h2>\n'
        f'<div class="faq-list">\n'
        + "\n".join(faq_items) + "\n"
        + '</div>\n'
        + faq_schema_script
    )

    return (
        fm + hero
        + browse_series_section + browse_control_section + browse_service_section
        + what_brings + how_we_approach
        + lead_time + "\n" + trust + "\n" + faq_section + "\n"
        + cross_links + "\n" + related + "\n"
    )


# ---------- Machine repair page (TASK 2) ----------

def _format_models_inline(models):
    if not models:
        return ""
    if len(models) == 1:
        return models[0]
    if len(models) == 2:
        return f"{models[0]} and {models[1]}"
    return ", ".join(models[:-1]) + f", and {models[-1]}"


def render_machine_repair(brand, g, brand_index):
    """Brand × machine-repair page. Lives at /repairs/{slug}-cnc-machine-repair/.
    Process-focused — no fabricated brand specifics beyond Ken's existing
    data. Target 250–350 visible body words.

    HUB-AND-SPOKE DISPATCH: any brand with an entry in BRAND_HUB_DATA
    (Mazak, Haas, DMG Mori, Doosan, Okuma, Fanuc per the prompt spec)
    gets the new hub-and-spoke template. The remaining 12 brands still
    use the standard template below."""
    if brand["slug"] in BRAND_HUB_DATA:
        return render_brand_hub(brand, g, brand_index)
    name = brand["brand_display_name"]
    slug = brand["slug"]
    ki = brand["ken_input"]
    models = ki["models"]
    control_system = brand.get("control_system", "varies by model")

    # H1 / eyebrow / canonical
    if len(name) > 11:
        h1_text = f"{name} CNC Repair"
    else:
        h1_text = f"{name} CNC Machine Repair & Service"
    eyebrow_text = f"CNC Machine Repair"
    canonical_path = f"/repairs/{slug}-cnc-machine-repair/"

    meta_desc = (
        f"Expert {name} CNC machine repair across the Midwest. "
        f"Spindle, control, ATC, drive, and alignment work. "
        f"Experienced field technicians."
    )

    fm = front_matter(
        brand,
        title=f"{name} CNC Machine Repair",
        h1=h1_text,
        meta_description=meta_desc,
        service_type=f"{name} CNC Machine Repair and Service",
        canonical_path=canonical_path,
        crumb_middle=("Repairs", "/repairs/"),
        crumb_leaf=f"{name} CNC Machine Repair",
    )

    img_path, img_alt = hero_image_for(brand, "machine_repair")
    model_inline = _format_models_inline(models)

    # New image-background hero — same visual language as the homepage
    # video hero. The image becomes a full-bleed background; text sits
    # centred over a dark gradient overlay.
    hero_lede = (
        f"When a {name} machine isn't producing the way it used to, we come in. "
        f"We work across the {name} lineup"
        f"{ ' — ' + model_inline if model_inline else '' } — "
        f"spindle, control, ATC, drive, and alignment work. "
        f"Lead time depends on what's wrong: diagnostics move fast, "
        f"parts and rebuild time vary by the job."
    )
    bg_img_html = (
        f'<img class="brand-hero-bg" src="{img_path}" alt="{html.escape(img_alt)}" loading="eager">\n'
        if img_path else ""
    )
    hero = (
        f'<section class="brand-hero">\n'
        f'{bg_img_html}'
        f'  <div class="brand-hero-overlay" aria-hidden="true"></div>\n'
        f'  <div class="brand-hero-content">\n'
        f'    <p class="eyebrow">{html.escape(eyebrow_text)}</p>\n'
        f'    <h1>{html.escape(h1_text)}</h1>\n'
        f'    <p>{html.escape(hero_lede)}</p>\n'
        f'    <div class="cta-row">\n'
        f'      <a class="cta-button" href="#quote">Get a Quote</a>\n'
        f'      <a class="cta-phone" href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a>\n'
        f'    </div>\n'
        f'  </div>\n'
        f'</section>\n\n'
    )

    # Models — pill chips instead of a bullet list. Easier to scan.
    if models:
        model_lis = "".join(f'<li>{html.escape(m)}</li>' for m in models)
        models_section = (
            f'<h2 id="models-we-service">{html.escape(name)} Models We Service</h2>\n'
            f'<p>Our {html.escape(name)} repair work covers the full lineup:</p>\n'
            f'<ul class="model-chips">{model_lis}</ul>\n'
        )
    else:
        models_section = ""

    # What Brings Machines In For Repair — process-uniform list, rotated
    # per brand so different pages don't open with the same item.
    issue_items = [
        "spindle issues",
        "control problems",
        "ATC faults",
        "drive system wear",
        "way alignment",
    ]
    rot = (sum(ord(c) for c in slug)) % len(issue_items)
    permuted = issue_items[rot:] + issue_items[:rot]
    items_text = ", ".join(permuted[:-1]) + f", or {permuted[-1]}"
    issues_section = (
        f"\n## What Brings {name} Machines In For Repair\n\n"
        f"Most {name} repair calls come in for {items_text}. "
        f"We diagnose what's actually broken before we quote — sometimes "
        f"what looks like a spindle problem is something cheaper to fix.\n"
    )

    # How We Approach — lean on Ken's control_system field. Honest fallback
    # for brands without a documented control.
    if control_system == "varies by model":
        approach = (
            f"{name} control systems vary by model, so we start with "
            f"diagnostics that match the platform in front of us rather than "
            f"assuming what we'll find."
        )
    else:
        approach = (
            f"{name} machines run {control_system}, so diagnostics need to "
            f"come from someone who knows the platform — that's us."
        )
    how = (
        f"\n## How We Approach {name} Repair Work\n\n"
        f"{approach}\n"
    )

    # Lead Time & Process — numbered process steps (HTML ol) so the
    # workflow gets the accented numbered-circle treatment from the
    # global .process-steps style.
    lead_section = (
        f'\n<h2 id="lead-time-process">Lead Time &amp; Process</h2>\n'
        f"<p>Lead time on machine repair depends on what's wrong — diagnostic "
        f"is fast, but parts and rebuild time vary by the job. Our three-step "
        f"workflow keeps it transparent:</p>\n"
        f'<ol class="process-steps">\n'
        f'  <li><strong>Contact us.</strong> Call <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a> or use the quote form. Tell us the machine, the symptoms, and how urgent it is.</li>\n'
        f'  <li><strong>Review &amp; quote.</strong> We confirm the model, scope the work, and send back a price and realistic lead time within one business day on most inquiries.</li>\n'
        f'  <li><strong>Approve &amp; rebuild.</strong> We complete the repair, verify it back to spec, and return the machine ready to run.</li>\n'
        f'</ol>\n'
    )

    trust = trust_block(g, brand["page_type"], brand_index, "a replacement machine")
    related = related_block_machine_repair(brand)
    cross_links = brand_cross_links_section(brand, {})
    faq_html, faq_schema = brand_faq_section(brand, ki, "machine_repair")
    # Blog teaser placeholder removed — was rendering as ghost text.

    return (
        fm + hero + models_section + issues_section + how
        + lead_section + "\n" + trust + "\n" + faq_html + "\n"
        + cross_links + "\n" + related + "\n"
    )


# ---------- Way covers page (TASK 3) ----------

def render_way_covers(brand, g, brand_index):
    """Brand × way-covers page. Lives at /way-covers/{slug}-cnc-way-covers/.

    HUB-AND-SPOKE DISPATCH: brands with WAY_COVERS_HUB_DATA entries
    (Mazak, Haas, DMG Mori, Doosan, Okuma, Fanuc) get the new hub-and-
    spoke template; other 14 brands keep the existing template.

    Manufacturing service — process-uniform across brands, with Ken's model
    list as the brand-specific anchor. For Amada/Trumpf this renders as a
    draft pending Ken's verification (SAFEGUARD).
    Target 200–280 visible body words."""
    if brand["slug"] in WAY_COVERS_HUB_DATA:
        return render_brand_way_covers_hub(brand, g, brand_index)
    name = brand["brand_display_name"]
    slug = brand["slug"]
    ki = brand["ken_input"]
    models = ki["models"]
    is_draft = bool(brand.get("way_covers_verification_pending"))

    h1_text = f"{name} CNC Way Cover Replacement"
    eyebrow_text = f"{name} CNC Way Covers"
    canonical_path = f"/way-covers/{slug}-cnc-way-covers/"

    meta_desc = (
        f"Replacement {name} CNC way covers manufactured to spec. Bellows, "
        f"telescoping steel, and roll-up styles. 2–4 week lead time on "
        f"most orders."
    )

    verification_msg = None
    if is_draft:
        verification_msg = (
            "Awaiting Ken confirmation that Midwest CNC makes way covers / "
            "shielding for press brakes (Amada) and laser cutters (Trumpf) — "
            "these aren't conventional CNC mill way covers."
        )

    fm = front_matter(
        brand,
        title=f"{name} CNC Way Covers",
        h1=h1_text,
        meta_description=meta_desc,
        service_type=f"{name} CNC Way Cover Manufacturing",
        canonical_path=canonical_path,
        crumb_middle=("Way Covers", "/way-covers/"),
        crumb_leaf=f"{name} CNC Way Covers",
        draft=is_draft,
        verification_pending=verification_msg,
    )

    img_path, img_alt = hero_image_for(brand, "way_covers")
    model_inline = _format_models_inline(models)

    lede_text = (
        f"We manufacture replacement way covers for {html.escape(name)} machines"
        f"{ ' across the ' + html.escape(model_inline) if model_inline else '' }. "
        f"Most jobs ship in 2&ndash;4 weeks depending on dimensions and "
        f"material. Bellows, telescoping steel, and roll-up styles available &mdash; "
        f"we match the original or build to spec."
    )
    hero = build_brand_hero_html(
        eyebrow_text or f"{name} CNC Way Covers",
        h1_text,
        lede_text,
        img_path, img_alt,
    )
    hero += machine_lookup_html()
    hero += browse_series_section_for_service(slug, name, "way_covers")

    if models:
        model_bullets = "\n".join(f"- {m}" for m in models)
        models_section = (
            f"\n## Way Covers We Manufacture for {name}\n\n"
            f"We cover the {name} lineup including:\n\n"
            f"{model_bullets}\n\n"
            f"[Get a Quote](#quote)\n"
        )
    else:
        models_section = (
            f"\n## Way Covers We Manufacture for {name}\n\n"
            f"We build replacement covers and shielding sized to your "
            f"machine — bring us the dimensions or the original part and "
            f"we'll match it.\n\n"
            f"[Get a Quote](#quote)\n"
        )

    what_we_build = (
        "\n## What We Build\n\n"
        "Way covers in three styles depending on the machine's design and "
        "operating conditions:\n\n"
        "- Bellows-style for protected ways with limited debris\n"
        "- Telescoping steel for heavier chip and coolant environments\n"
        "- Roll-up for retrofits and specific clearance constraints\n\n"
        "We measure to spec from your original or your machine, fabricate, "
        "and ship anywhere in the continental US.\n"
    )

    lead_section = (
        "\n## Lead Time\n\n"
        "2–4 weeks for most way cover orders, depending on dimensions and "
        "material. Rush options available — call to discuss.\n"
    )

    trust = trust_block(
        g, brand["page_type"], brand_index,
        "replacement way covers and the retrofit time",
    )
    related = related_block_way_covers(brand)
    cross_links = brand_cross_links_section(brand, {})
    faq_html, faq_schema = brand_faq_section(brand, ki, "way_covers")
    # blog_block() removed — was rendering as dashed-border placeholder

    return (
        fm + hero + models_section + what_we_build
        + lead_section + "\n" + trust + "\n" + faq_html + "\n"
        + cross_links + "\n" + related + "\n"
    )


# ---------- Driver ----------

def _word_count(md):
    """Visible body word count (approximate). Strips YAML front matter,
    headings, list markers, link wrappers, and italic placeholders."""
    body = re.sub(r"^---.*?^---\s*", "", md, flags=re.S | re.M)
    body = re.sub(r"`[^`]*`", "", body)
    body = re.sub(r"#+\s*\S.*", "", body)
    body = re.sub(r"\*[^*]+\*", "", body)
    body = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", body)
    body = re.sub(r"^\s*[-*]\s+", "", body, flags=re.M)
    return len(re.findall(r"\b[\w'-]+\b", body))


def main():
    data = json.load(open(DATA))
    g = data["global_context"]
    brands = data["brands"]
    brands_by_slug = {b["slug"]: b for b in brands}

    for d in (OUTDIR_SPINDLE, OUTDIR_REPAIR, OUTDIR_COVERS):
        os.makedirs(d, exist_ok=True)

    # Alphabetical brand_index drives customer-quote rotation. A single
    # index per brand keeps the rotation consistent across all of that
    # brand's pages (spindle/repair/way-covers).
    sorted_slugs = sorted(b["slug"] for b in brands)
    index_for = {s: i for i, s in enumerate(sorted_slugs)}

    written = []  # (service_kind, slug, path, words, draft)

    for b in brands:
        pt = b["page_type"]
        bi = index_for[b["slug"]]
        so = b.get("services_offered", {})

        # --- Main brand page (spindle for cnc_spindle, repair page for the others) ---
        if pt == "cnc_spindle":
            md = render_cnc_spindle(b, g, brands_by_slug, bi)
        elif pt == "press_brake_service":
            md = render_amada(b, g, brands_by_slug, bi)
        elif pt == "laser_punch_service":
            md = render_trumpf(b, g, brands_by_slug, bi)
        else:
            raise SystemExit(f"Unknown page_type: {pt}")
        path = os.path.join(OUTDIR_SPINDLE, f"{b['slug']}.md")
        with open(path, "w") as f:
            f.write(md)
        written.append(("main",         b["slug"], path, _word_count(md), False))

        # --- Spindle hub-and-spoke spokes: emit for any brand with
        # SPINDLE_HUB_DATA entry (Mazak, Haas, DMG Mori, Doosan, Okuma, Fanuc).
        if b["slug"] in SPINDLE_HUB_DATA:
            n_spindle_spokes = _emit_brand_spindle_spokes(b, bi)
            written.append((f"{b['slug']}_spindle_spokes", b["slug"], OUTDIR_SPINDLE,
                            n_spindle_spokes * 500, False))

        # --- Machine-repair page (cnc_spindle brands only) ---
        if so.get("machine_repair"):
            md = render_machine_repair(b, g, bi)
            path = os.path.join(OUTDIR_REPAIR, f"{b['slug']}.md")
            with open(path, "w") as f:
                f.write(md)
            written.append(("machine_repair", b["slug"], path, _word_count(md), False))

            # --- Hub-and-spoke spokes: emit for any brand with hub data.
            # Includes Mazak (pilot), Haas, DMG Mori, Doosan, Okuma, Fanuc.
            if b["slug"] in BRAND_HUB_DATA:
                n_spokes = _emit_brand_spokes(b, bi)
                written.append((f"{b['slug']}_spokes", b["slug"], OUTDIR_REPAIR,
                                n_spokes * 500, False))

        # --- Way-covers page (all 20 brands; Amada/Trumpf flagged draft) ---
        if so.get("way_covers"):
            md = render_way_covers(b, g, bi)
            path = os.path.join(OUTDIR_COVERS, f"{b['slug']}.md")
            with open(path, "w") as f:
                f.write(md)
            written.append(("way_covers", b["slug"], path,
                             _word_count(md),
                             bool(b.get("way_covers_verification_pending"))))

            # --- Way-covers hub-and-spoke spokes: emit for any brand
            # with WAY_COVERS_HUB_DATA entry.
            if b["slug"] in WAY_COVERS_HUB_DATA:
                n_wc_spokes = _emit_brand_way_covers_spokes(b, bi)
                written.append((f"{b['slug']}_way_covers_spokes", b["slug"], OUTDIR_COVERS,
                                n_wc_spokes * 500, False))

    n_redirects = write_redirects(brands, os.path.join(REPO, "public", "_redirects"))

    # Summary
    by_kind = {}
    for kind, slug, path, words, draft in written:
        by_kind.setdefault(kind, []).append((slug, words, draft))

    print(f"\nWrote {len(written)} markdown files across 3 content directories.")
    print(f"Wrote {n_redirects} redirects to public/_redirects.\n")

    for kind in ("main", "machine_repair", "way_covers"):
        if kind not in by_kind:
            continue
        rows = by_kind[kind]
        avg = sum(w for _, w, _ in rows) // len(rows)
        n_draft = sum(1 for _, _, d in rows if d)
        print(f"  {kind:<15} {len(rows):>3} pages  avg ~{avg:>4} words  drafts: {n_draft}")


if __name__ == "__main__":
    main()

---
title: "Mori Seiki Spindle Repair | Midwest CNC Services"
meta_description: "Expert Mori Seiki spindle repair across the Midwest. 3–5 weeks on most rebuilds. Experienced field technicians."
h1: "Mori Seiki Spindle Repair & Rebuilds"
slug: "mori-seiki"
page_type: "cnc_spindle"
schema_data:
  service:
    "@type": Service
    serviceType: "Mori Seiki CNC Spindle Repair and Grinding"
    provider:
      "@id": "#org"
    areaServed:
      - Iowa
      - Illinois
      - Minnesota
      - Wisconsin
      - Nebraska
      - Missouri
      - Texas
  local_business:
    "@type": LocalBusiness
    "@id": "#org"
    name: "Midwest CNC Services"
    telephone: "+13196104341"
    # address, geo, openingHours filled in by template at build time
  breadcrumb:
    "@type": BreadcrumbList
    itemListElement:
      - { position: 1, name: Home, item: "https://midwestcncservices.com/" }
      - { position: 2, name: "Spindle Grinding", item: "https://midwestcncservices.com/spindle-grinding/" }
      - { position: 3, name: "Mori Seiki Spindle Repair", item: "https://midwestcncservices.com/spindle-grinding/mori-seiki-spindle-repair/" }
---
<section class="brand-hero">
<img class="brand-hero-bg" src="/assets/images/services/repairs-mori-seiki-cnc-machine-repair-image.png" alt="Mori Seiki machine service work at Midwest CNC Services" loading="eager">
  <div class="brand-hero-overlay" aria-hidden="true"></div>
  <div class="brand-hero-content">
    <p class="eyebrow">Mori Seiki Spindle Repair &amp; Grinding</p>
    <h1>Mori Seiki Spindle Repair &amp; Rebuilds</h1>
    <p>What we see most on Mori Seiki spindles: older belt-drive setups tend to come in with pulley wear and tired bearings. Newer direct-drive units usually show heat damage or preload loss. We rebuild, regrind, and rebalance across the Mori Seiki platform &mdash; SL series, NL series, older MV mills, and NH horizontals &mdash; with most jobs running 3–5 weeks and field troubleshooting where it can save a teardown.</p>
    <div class="cta-row">
      <a class="cta-button" href="#quote">Get a Quote</a>
      <a class="cta-phone" href="tel:+13196104341">319-610-4341</a>
    </div>
  </div>
</section>

<div class="machine-lookup" id="machine-lookup">
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
    return (s || '').toLowerCase().replace(/[\s\-]/g, '');
  }
  function escapeHTML(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[c];
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
        '<div class="machine-lookup-empty">' +
          'We service older and obscure machines too. ' +
          '<a href="/get-a-quote/">Get a quote</a> or call ' +
          '<a href="tel:+13196104341">319-610-4341</a>.' +
        '</div>';
    } else {
      results.innerHTML = matches.map(function (m) {
        // Context-aware URL routing: machines.json stores the repair-section
        // spoke URL; when the user is on a /spindle-grinding/ or /way-covers/
        // page we rewrite the URL to the corresponding service-line spoke so
        // the user lands on the right content without a context switch.
        var href = m.spoke_url;
        if (/^\/spindle-grinding\//.test(window.location.pathname)) {
          href = href.replace(/^\/repairs\/([\w-]+)-cnc-machine-repair\//,
                              '/spindle-grinding/$1-spindle-repair/');
        } else if (/^\/way-covers\//.test(window.location.pathname)) {
          href = href.replace(/^\/repairs\/([\w-]+)-cnc-machine-repair\//,
                              '/way-covers/$1-cnc-way-covers/');
        }
        return (
          '<a class="machine-lookup-result" href="' + escapeHTML(href) + '" role="option">' +
            '<span class="machine-lookup-result-brand">'  + escapeHTML(m.brand)  + '</span>' +
            '<span class="machine-lookup-result-model">'  + escapeHTML(m.model)  + '</span>' +
            '<span class="machine-lookup-result-series">' + escapeHTML(m.series) + '</span>' +
            '<span class="machine-lookup-result-arrow" aria-hidden="true">&rarr;</span>' +
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

## Mori Seiki Models We Support

Our Mori Seiki work covers the full lineup. Whether the job is a precision bearing pack replacement, a full rebuild, or a regrind to restore tolerance, we handle:

- SL series
- NL series
- older MV mills
- NH horizontals

[Get a Quote](#quote)

## How We Approach Mori Seiki Spindle Work

A lot of the older standalone Mori machines are still extremely solid mechanically and worth rebuilding.

## A Recent Mori Seiki Job

A recent example of the kind of work that comes through here: one customer was ready to scrap an older Mori horizontal because of chatter. After rebuild and alignment work, it went right back into production.

## Lead Time & Process

3–5 weeks depending on spindle generation. Our three-step workflow keeps it transparent:

**Step 1 — Contact Us.** Call 319-610-4341 or use the quote form below. [Get a Quote](#quote)

**Step 2 — Grab Model #.** We'll fire back price, lead time, and shipping ETA after reviewing your details. [Get a Quote](#quote)

**Step 3 — Approve & Rebuild.** We rebuild the spindle, verify balance and runout, and return it ready to run.

*Quote form rendered here at build time.*


## Why Shops Trust Us

Experienced field technicians with hands-on time across the major CNC OEM platforms, in-house precision spindle balancing capability, laser alignment services, and established relationships with aftermarket bearing and spindle component suppliers.

> "Honestly, we thought the machine was done for." It saves shops from replacement lead times and the capital expense of a new spindle.

<h2 id="faq">Frequently Asked Questions</h2>
<div class="faq-list">
<details class="faq-item">
  <summary>Where can I get Mori Seiki spindle repair near me?</summary>
  <div class="faq-answer"><p>Midwest CNC Services rebuilds Mori Seiki spindles from our Waterloo, Iowa shop and ships finished work to any continental US destination. Direct service covers Iowa, Illinois, Wisconsin, Minnesota, Nebraska, Missouri, and Texas. Call 319-610-4341 to scope the job.</p></div>
</details>
<details class="faq-item">
  <summary>How much does a Mori Seiki spindle rebuild cost?</summary>
  <div class="faq-answer"><p>Mori Seiki spindle rebuild cost depends on the failure mode — bearing-pack replacement, taper damage, preload loss, and crash recovery all scope differently. We quote after reviewing the symptoms, model, and photos where available. Most quotes go out within one business day with a lead time and parts breakdown.</p></div>
</details>
<details class="faq-item">
  <summary>What&#x27;s the typical lead time on a Mori Seiki spindle rebuild?</summary>
  <div class="faq-answer"><p>3–5 weeks depending on spindle generation. Each job is scoped during the quote — bearing-pack damage, parts availability, and crash-related work all shift the window.</p></div>
</details>
<details class="faq-item">
  <summary>What&#x27;s the most common Mori Seiki spindle failure you see?</summary>
  <div class="faq-answer"><p>Older belt-drive setups tend to come in with pulley wear and tired bearings. Newer direct-drive units usually show heat damage or preload loss.</p></div>
</details>
<details class="faq-item">
  <summary>What should I know about Mori Seiki spindle rebuilds specifically?</summary>
  <div class="faq-answer"><p>A lot of the older standalone Mori machines are still extremely solid mechanically and worth rebuilding.</p></div>
</details>
<details class="faq-item">
  <summary>Do you grind Mori Seiki spindles back to factory tolerance?</summary>
  <div class="faq-answer"><p>Yes — precision spindle balancing and grinding to runout is part of every rebuild we do, with photo verification at sign-off.</p></div>
</details>
</div>

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Where can I get Mori Seiki spindle repair near me?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Midwest CNC Services rebuilds Mori Seiki spindles from our Waterloo, Iowa shop and ships finished work to any continental US destination. Direct service covers Iowa, Illinois, Wisconsin, Minnesota, Nebraska, Missouri, and Texas. Call 319-610-4341 to scope the job."
      }
    },
    {
      "@type": "Question",
      "name": "How much does a Mori Seiki spindle rebuild cost?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Mori Seiki spindle rebuild cost depends on the failure mode — bearing-pack replacement, taper damage, preload loss, and crash recovery all scope differently. We quote after reviewing the symptoms, model, and photos where available. Most quotes go out within one business day with a lead time and parts breakdown."
      }
    },
    {
      "@type": "Question",
      "name": "What's the typical lead time on a Mori Seiki spindle rebuild?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "3–5 weeks depending on spindle generation. Each job is scoped during the quote — bearing-pack damage, parts availability, and crash-related work all shift the window."
      }
    },
    {
      "@type": "Question",
      "name": "What's the most common Mori Seiki spindle failure you see?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Older belt-drive setups tend to come in with pulley wear and tired bearings. Newer direct-drive units usually show heat damage or preload loss."
      }
    },
    {
      "@type": "Question",
      "name": "What should I know about Mori Seiki spindle rebuilds specifically?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "A lot of the older standalone Mori machines are still extremely solid mechanically and worth rebuilding."
      }
    },
    {
      "@type": "Question",
      "name": "Do you grind Mori Seiki spindles back to factory tolerance?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Yes — precision spindle balancing and grinding to runout is part of every rebuild we do, with photo verification at sign-off."
      }
    }
  ]
}
</script>

<h2 id="regional-presence">Where Mori Seiki Work Concentrates</h2>
<p>Mori Seiki platforms have strong regional concentration in our service area:</p>
<ul><li><a href="/service-area/iowa/">Iowa</a> — particularly <a href="/service-area/cedar-rapids-iowa/">Cedar Rapids</a></li><li><a href="/service-area/illinois/">Illinois</a> — particularly <a href="/service-area/rockford-illinois/">Rockford</a></li><li><a href="/service-area/minnesota/">Minnesota</a> — particularly <a href="/service-area/minneapolis-minnesota/">Minneapolis</a></li></ul>

## Related Mori Seiki Services

- [Mori Seiki CNC machine repair](/repairs/mori-seiki-cnc-machine-repair/)
- [Mori Seiki CNC way covers](/way-covers/mori-seiki-cnc-way-covers/)
- See also spindle grinding on related platforms:
  - [DMG Mori spindle grinding](/spindle-grinding/dmg-mori-spindle-repair/)
  - [Mazak spindle grinding](/spindle-grinding/mazak-spindle-repair/)
  - [Okuma spindle grinding](/spindle-grinding/okuma-spindle-repair/)

We serve shops across Iowa, Illinois, Minnesota, Wisconsin, Nebraska, Missouri, and Texas.


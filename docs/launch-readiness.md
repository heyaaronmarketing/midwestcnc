# Launch Readiness Audit

Audited **298 HTML files** under `public/` plus the `assets/` tree. Run this any time before deploy to catch regressions.

## Summary

- Total HTML files in `public/`: **298**
- Sitemap URLs:                  **294**
  (3 expected exclusions: 404 page + draft way-cover pages)
- Internal links scanned:         **19997**
- Broken internal links:          **0**
- Ban-list findings:              **0** unauthorized, **3** Aaron-authorized exceptions
- Schema issues:                  **0**
- Pages missing breadcrumb:       **0** (homepage and 404 are expected here)
- Images missing `alt`:           **0**
- Images with empty `alt`:        **0** (decorative — generally acceptable)
- Pages without viewport meta:    **0**
- Distinct `<header>` markups:    **2** (want 1 if nav is template-consistent)
- Total asset size:               **114.3 MB** across 146 files

## Verdict

**Blockers:**

- navigation drift (2 distinct headers)

## a) Link audit

- Total `<a href>` scanned: 19997
- Resolved to file:        17211
- Resolved via redirect:   0
- External (skipped):      299
- Non-http skipped:        2487
- **Broken:**              **0**

## d) Claim-audit ban-list scan

**Aaron-authorized exceptions** (documented in `docs/claim-audit.md`):
- `same-day` in `public/service-area/index.html` — authorized
- `same-day` in `public/service-area/iowa/index.html` — authorized
- `warranty` in `public/terms-of-service/index.html` — authorized

## e) Schema validation

- Pages with BreadcrumbList: 296 / 296 (excluding homepage and 404)
- No structural schema issues found.

## f) Image alt-text audit

Every `<img>` has a populated `alt` attribute. 🎉

## g) Viewport meta-tag

Every page has `<meta name="viewport" content="width=device-width, initial-scale=1">`. 🎉

## h) Cross-page nav consistency

**2 distinct `<header>` markups detected.** Want 1 — if more, the template has drifted somewhere:
- `11d5ddc2c7e5` — 263 pages
  - `public/repairs/amada-press-brake-service/index.html`
  - `public/repairs/amera-seiki-cnc-machine-repair/index.html`
  - `public/repairs/brother-cnc-machine-repair/index.html`
  - *…and 260 more*
- `f2994f3b9491` — 35 pages
  - `public/404.html`
  - `public/about/index.html`
  - `public/get-a-quote/index.html`
  - *…and 32 more*

## i) Asset directory size

- Total: **114.3 MB** across 146 files

Breakdown by subdirectory:

| Subdirectory | Bytes | Pretty |
|---|---:|---:|
| `images/cities` | 47,106,262 | 44.9 MB |
| `images/services` | 27,542,983 | 26.3 MB |
| `images/blocks` | 24,614,343 | 23.5 MB |
| `images/general` | 10,740,603 | 10.2 MB |
| `images/states` | 9,868,033 | 9.4 MB |
| `images/logos` | 21,716 | 21.2 KB |

## b/c) Sitemap composition

- Total `<loc>` entries: 294
- HTML files in `public/`: 298
- Difference: 4 (404 page + drafts — expected)

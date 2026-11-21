# Phase 1 — Cross-Link Audit

Scanned every `<a href>` in every HTML file under `public/` and resolved each link against the filesystem and `public/_redirects`.

## Totals

- **Total `<a href>` links scanned:** 22046
- **Resolved to a real file:** 18722
- **Resolved via `_redirects` (301):** 0
- **External links (skipped from broken-check):** 647
- **Other non-http (tel:/mailto:/anchor/etc.):** 2677

## Broken internal links

None. 🎉

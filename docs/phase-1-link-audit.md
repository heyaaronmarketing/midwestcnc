# Phase 1 — Cross-Link Audit

Scanned every `<a href>` in every HTML file under `public/` and resolved each link against the filesystem and `public/_redirects`.

## Totals

- **Total `<a href>` links scanned:** 20749
- **Resolved to a real file:** 17577
- **Resolved via `_redirects` (301):** 0
- **External links (skipped from broken-check):** 609
- **Other non-http (tel:/mailto:/anchor/etc.):** 2563

## Broken internal links

None. 🎉

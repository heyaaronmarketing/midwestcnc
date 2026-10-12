# Phase 1 — Cross-Link Audit

Scanned every `<a href>` in every HTML file under `public/` and resolved each link against the filesystem and `public/_redirects`.

## Totals

- **Total `<a href>` links scanned:** 19997
- **Resolved to a real file:** 17211
- **Resolved via `_redirects` (301):** 0
- **External links (skipped from broken-check):** 299
- **Other non-http (tel:/mailto:/anchor/etc.):** 2487

## Broken internal links

None. 🎉

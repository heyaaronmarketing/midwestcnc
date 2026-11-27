# Phase 1 — Cross-Link Audit

Scanned every `<a href>` in every HTML file under `public/` and resolved each link against the filesystem and `public/_redirects`.

## Totals

- **Total `<a href>` links scanned:** 22662
- **Resolved to a real file:** 19266
- **Resolved via `_redirects` (301):** 0
- **External links (skipped from broken-check):** 665
- **Other non-http (tel:/mailto:/anchor/etc.):** 2731

## Broken internal links

None. 🎉

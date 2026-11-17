# Performance and indexing review — 17 November 2026

The disabled advertising integration downloaded the AdSense SDK on every page. Verification-only pages now use Google's `google-adsense-account` meta tag. The SDK remains available when both advertising approval and rendering are enabled. Publisher ID, ads.txt, slot settings and layout are unchanged. Generated HTML is included because this repository publishes the static export.

`npm run check` passes, including the new crawlability check. AdSense browser checks pass across 30 views (five routes, three phone widths, both themes), with zero SDK requests, visible advertisements or overflow. The approval/render combinations and disabled verification are checked separately.

## Search Console findings

The supplied export contains 173 discovered/not-indexed URLs. Every listed URL currently returns HTTP 200 with its own canonical URL and indexable HTML directives. The generated sitemap contains 174 indexable routes. All are reachable through ordinary HTML links within two clicks of the homepage; no missing internal targets were found. Current robots.txt allows crawling and advertises the canonical sitemap. `live-url-audit.json` records the URL checks.

The overall export reports 10 canonical alternatives, four 404s, two redirects, 12 crawled/not-indexed pages, 173 discovered/not-indexed pages and zero server errors. Alternatives and redirects are not inherently faults. The attachments do not identify the URLs for the four 404s or the 12 crawled/not-indexed pages, so no speculative redirects or page removals were added. The shared Search Console drilldown required Google sign-in in the available browser. URL examples or an authenticated Search Console session are needed to finish those two groups.

`1970-01-01` in the supplied table is treated as an unknown/placeholder crawl date. No claim about an actual 1970 crawl is made. Google controls indexing; passing technical checks does not force inclusion. After publishing, inspect representative year, subject and book URLs in Search Console using Test live URL, then request indexing for the principal hubs. Confirm sitemap processing there. IndexNow does not submit pages to Google.

## Measurement limits

Lighthouse uses local gzip delivery with mobile throttling. These are lab measurements, not field Core Web Vitals or a measurement of the future deployed build. The unmodified local baseline already scored 95–99 for performance; the earlier production run scored 91–95. These environments are not directly comparable. An initial modified run overlapped with static checks and was discarded from the final comparison because of CPU contention; the isolated final run is recorded separately. Verify the deployed build with the production workflow after merge.

## Final isolated results

30 layout/axe views passed with no browser errors; menu, search, theme persistence, studied state, no-JavaScript preset links and reduced motion checks passed. Mobile Lighthouse results:

| Route | Performance | Accessibility | Best practices | SEO | LCP |
|---|---:|---:|---:|---:|---:|
| / | 97 | 100 | 100 | 100 | 2.26s |
| /bvsc/year-1/roadmap/ | 97 | 100 | 100 | 100 | 1.97s |
| /bvsc/tanuvas-notes/ | 98 | 100 | 100 | 100 | 1.96s |
| /objective/ | 98 | 100 | 100 | 100 | 2.33s |
| /books/dhruv-desai/ | 99 | 100 | 100 | 100 | 2.12s |

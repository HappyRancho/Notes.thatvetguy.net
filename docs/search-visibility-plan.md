# Search visibility audit and action plan

Audit: 20 October 2026. Property: https://notes.thatvetguy.net/. Repository baseline: `fcfc7101e6eaecdfea57a6f01dbdd5b8074153e4`.

## Conclusion

The public HTTP audit found no basic crawl/indexing blocker on the 16 sitemap pages. The website is accessible, but eligibility to be indexed does not establish actual indexing or rankings. Google Search Console access is required to establish Google's last crawl, selected canonical and exclusion reason. No claim of a penalty, sandbox, domain age or specific backlink deficit is supported by this audit.

Exploratory searches for `site:notes.thatvetguy.net`, the exact domain, the brand and BVSc/veterinary notes did not return the notes subdomain in the results shown to this audit. They returned established notes sites and the main ThatVetGuy website. This is weak visibility evidence, not an exhaustive Google index/rank report; search results vary by engine, location and date.

## Verified public baseline

Raw results: [baseline.json](qa/search/baseline.json). Reproduce with `python3 scripts/search-health.py --label baseline` from a network-enabled runner.

| Check | Baseline result | Interpretation |
| --- | --- | --- |
| All 16 sitemap URLs | HTTP 200; self-canonical to the custom domain; index allowed; one H1 | No obvious HTTP, canonical or noindex block |
| robots.txt, sitemap.xml, llms.txt, llms-full.txt, search-index.json | HTTP 200 | Discovery endpoints exist and can be fetched |
| Googlebot, Bingbot, OAI-SearchBot user-agent probes | HTTP 200, no challenge observed | UA-specific basic probes pass; these are not authenticated real bots |
| Search page | HTTP 200, noindex/follow, excluded from sitemap | Intentional and appropriate; not a site-wide noindex |
| Invented missing URL | HTTP 404 with noindex | No homepage fallback/soft-404 problem in this test |
| HTTP home and /index.html | Resolve to HTTPS canonical homepage | Normalization already works |
| pages.dev alias | HTTP 200; canonical points to custom domain | Working alias, not downtime. Optional 301 consolidation remains a hosting task |
| Live build marker | cf3503dfdb94, matching baseline repo build | Prior published build is actually live |
| Catalogue | 499 linked notes + 21 Telegram collection items = 520 resources | Resource count is not the count of independent indexed pages |
| Indexable architecture | 16 pages; four year hubs and four year note readers; standalone subjects retired | Subject queries share year-level URLs; fragment IDs are not separate indexable subject pages |

## Changes implemented

1. Added distinct, factual search titles/descriptions for BVSc, Objective, Handbooks and Drug Index, and subject-specific descriptions for each year's note reader. Removed the duplicated brand title on About. No unsupported claim of a real ICAR PYQ collection was added.
2. Restored short subject explanations and study pointers already present in the source data to the four note readers. Original explanatory text is visible HTML, not schema-only text. All existing resource URLs and the year-based architecture remain intact.
3. Preserved the subject anchor when redirecting retired year/subject URLs to the year's note reader, rather than sending every subject to its top.
4. Replaced the single library-review date as page lastmod with persisted per-page content fingerprints. Sitemap and page JSON-LD now agree about actual page changes; unchanged rebuilds preserve their dates. Source-review dates remain separate, so editing metadata does not imply rechecking hundreds of files.
5. Added HTML discovery links for Markdown mirrors and HTTP canonical headers from each mirror to its HTML equivalent. Updated AI-readable introductions to describe Telegram access, book recommendations and source ownership accurately. Added the visible Rx Notes identity as a WebSite alternateName.
6. Added build-failing SEO checks for unique metadata, sitemap/JSON-LD date agreement, self-canonicals, Markdown discovery and crawlable internal paths to every indexable page. Added a repeatable public HTTP audit workflow and stored its baseline evidence.

No theme redesign, new subject routes, invented downloads, meta-keywords, hidden keyword text, fabricated FAQs/reviews, or ranking promises were introduced.

## Publication status — deployment mismatch confirmed

The improvements and generated pages are committed to `main` in `ab3c97d850b3348fe1c5177d5c660ee4c1eff99b`. Review QA passed: 12 homepage views, 40 additional page views, no reported browser/axe failures, and Lighthouse scores on five pages of 97–99 Performance and 100 Accessibility / Best Practices / SEO. These are review-build measurements, not new production scores. Handbooks LCP was 2.41 seconds in that run, so the earlier under-2-second target was not met there.

After publication, the production job checked nine live routes repeatedly and correctly failed: every route still served build `cf3503dfdb94`, while `main` expects `f22744229921`. Both the custom domain and pages.dev alias served that same old build. See [deployment-mismatch.json](qa/search/deployment-mismatch.json). No cache purge was attempted because Cloudflare API token/zone bindings were unavailable. No new Cloudflare Pages check appeared on the publication commit during this verification window; that observation alone does not establish the cause.

**Hosting action required:** In Cloudflare → Workers & Pages → `notes-thatvetguy-net`, inspect the latest production deployment and Git integration. Confirm the repository is `HappyRancho/Notes.thatvetguy.net`, the production branch is `main`, and production deployments are enabled; inspect build-watch exclusions, skipped builds and any build error. Deploy the current `main` commit, then verify `/build-info.json` reports `f22744229921` and the page HTML has the same `site-build` marker. If the Pages alias updates but the custom domain does not, investigate custom-domain routing/cache next. A cache purge by itself cannot publish a commit that was never deployed.

Until that mismatch is resolved, the fixes are **committed and validated, but not verified live**. This deployment issue is separate from the baseline crawl findings: the older live pages remain publicly accessible and indexable.

## What is probably limiting visibility

- **Indexing/discovery is still unconfirmed.** Search Console must distinguish unknown URLs, discovered-not-indexed, crawled-not-indexed and indexed-but-low-ranking. Each needs a different response.
- **Much of the academic value is off-site.** Linking to a PDF does not make its full contents text on your HTML page. Several competitors link to the same underlying notes. Clearer navigation is useful, but original explanations and editorial selection give search engines and AI systems a reason to cite this site specifically.
- **Subject targeting was consolidated.** Nineteen subject sections now share four note-reader URLs. That follows the requested architecture, but reduces dedicated search landing pages for terms such as veterinary pharmacology notes. Keep year routes stable and strengthen their subject sections before deciding whether dedicated, substantial subject guides are worth adding later.
- **The main website offers a discovery opportunity.** Its publicly fetched home page and Chirag profile did not expose a notes-library link in the readable content. A contextual link from those existing pages would help students and crawlers reach the library. This audit does not measure all backlinks or prove no link exists elsewhere.
- **Recent restructuring requires recrawling.** The repository records multiple URL/content changes. Search engines may need to discover and reassess them. The audit has not established the domain's age, first index date or a guaranteed waiting period.

## Prioritized action plan

| Priority / timing | Action | Owner / evidence of success |
| --- | --- | --- |
| P0 — first | Resolve the production/repository mismatch described above. Publish current main through the existing Cloudflare Pages project. | Cloudflare owner. Both hosts serve the expected build marker; the exact-build verification passes. |
| P0 — now | Verify a Google Search Console Domain property for thatvetguy.net, or URL-prefix property for https://notes.thatvetguy.net/. Submit https://notes.thatvetguy.net/sitemap.xml. Inspect Home, /bvsc/, one year hub and one year note reader; run Live Test. Request indexing once after fixes. | Property owner. Record indexed status, last crawl, Google-selected canonical, successful sitemap processing and indexed page count. Do not repeatedly submit the same URLs. |
| P0 — now | Check Search Console Manual Actions, Security Issues and Page indexing reports. In Cloudflare Security Events, inspect verified Googlebot/Bingbot/OpenAI search requests for blocks/challenges. Keep robots and important assets accessible. | Property owner. Authenticated crawl evidence and the actual exclusion reasons; UA probes alone cannot establish this. |
| P1 — this week | Add a natural “Free BVSc notes and veterinary study resources” link from the main website and author profile, plus relevant blog articles. Verify Bing Webmaster Tools and submit the same canonical sitemap. | Main-site owner. Followable HTML links, successful sitemap processing and first crawler visits/impressions. Main website was not modified in this task. |
| P1 — this week | Keep the current URLs stable. Optionally configure the production pages.dev alias to 301 to the custom domain, retaining paths and query strings; leave branch previews available. Current canonicals already favor the custom domain. | Cloudflare owner. Test home, a nested page and a query string. Follow Cloudflare's documented alias/custom-domain procedure; no access to these dashboard settings was available. |
| P1 — next 2–4 weeks | Expand useful original guidance inside existing year/subject sections: scope, what each resource covers, book edition/selection advice and common study questions. Start with Anatomy, Physiology, Pharmacology, Pathology and Medicine. Credit source authors and get veterinary editorial review. | Editor. Information students can use before opening a file, with accurate author/review attribution. No arbitrary word-count target or copied competitor prose. |
| P2 — weekly | Measure Search Console with country India, device mobile, and query groups: BVSc notes, veterinary notes, year terms and individual subjects. Review 28-day impressions, clicks, indexed URLs and CTR by page; compare comparable periods. | Owner/editor. Separate “not indexed” from “indexed but not relevant/competitive”; use the data to choose the next content improvements. |
| P2 — ongoing | Earn real links through veterinary college libraries, student groups, teaching staff and original contributors. Publish original resources that deserve reference links. | Owner/community. Relevant referring pages and student usage; avoid purchased bulk links and copied directory submissions. |

Suggested query/page mapping: Home and /bvsc/ for broad BVSc/veterinary notes; each /bvsc/year-N/notes/ for that year's subjects; /objective/ for veterinary objective notes and question banks; /clinical/handbooks/ for veterinary handbooks; /clinical/drug-index/ for veterinary drug references. Do not claim hosted book downloads or available PYQs where the collection does not supply them.

## AI / LLM discovery

llms.txt, llms-full.txt, the JSON resource index, Markdown mirrors, static HTML and JSON-LD already existed. They are useful retrieval formats, but they do not guarantee Google rankings or AI citations. Google states that no special AI text file or schema is needed for AI Overviews/AI Mode: normal crawlability, indexing, helpful text and consistent structured data still apply. Public PDFs and Telegram access rules remain controlled by their owners; private Telegram posts cannot be made publicly crawlable by this site's metadata.

## Limits and validation

Local build and checks pass: 18 generated HTML pages (16 indexable), all 520 catalogue entries preserved, strict external-link policy, no orphan sitemap pages, unique metadata, matching schema/canonicals, and both existing contrast suites. A repeated unchanged build preserves content dates and discovery output. Home HTML/CSS/JS remains approximately 35 KB gzip; this is a payload check, not a fresh Lighthouse score.

Search Console/Bing account data, verified bot logs, backlink metrics, Cloudflare dashboard rules and real-user Core Web Vitals were unavailable. No production indexing submission or dashboard change is claimed. Browser/production deployment results are recorded by the repository's QA workflows; use those run artifacts for exact fresh scores.

## Primary guidance

- Google: [AI features and your website](https://developers.google.com/search/docs/appearance/ai-features)
- Google: [Request recrawling](https://developers.google.com/search/docs/crawling-indexing/ask-google-to-recrawl)
- Google: [Sitemap dates](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)
- Google: [Canonical signals](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls)
- Google: [Helpful content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content)
- Google: [Limits of site: searches](https://developers.google.com/search/docs/monitor-debug/search-operators/all-search-site)
- Cloudflare: [Redirecting the Pages alias](https://developers.cloudflare.com/pages/how-to/redirect-to-custom-domain/)

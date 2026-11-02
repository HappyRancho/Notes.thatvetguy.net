# Search visibility audit — 2 November 2026

Site: https://notes.thatvetguy.net/

## What the evidence says

- Owner-supplied Google Search Console screenshots confirm the homepage is indexed. Googlebot smartphone last crawled it on 1 November 2026; fetch and indexing were allowed. Google selected the same canonical as the site and discovered the sitemap. This is evidence for the homepage, not all URLs.
- Public `site:` and exact-domain searches returned no results in this research session. These searches are incomplete diagnostics and do not override Search Console's indexed status. No claim about a measured Google rank follows from them.
- The 2 November production audit checked 185 endpoints, including 172 sitemap pages, without crawl errors. Sitemap pages returned 200, expected canonical URLs, indexable directives and one H1. HTTP and `/index.html` resolve to the canonical homepage; a nonexistent URL returns 404.
- Requests carrying Googlebot, Bingbot and OAI-SearchBot user-agent strings received 200 HTML. These are accessibility probes, not authenticated crawler visits or proof that an engine indexed the page.
- Search Console performance, query impressions, clicks, country/device rankings, manual actions, links and field Core Web Vitals are not connected here. Traffic growth and the exact cause of low ranking cannot be measured from the public crawl alone.

## Findings and implementation

| Finding | Change | Verification |
| --- | --- | --- |
| Per-page Markdown canonical headers exceed Cloudflare Pages' documented 100-rule limit | Replace the individual rules with root and wildcard rules; retain explicit exclusion headers for six non-indexed mirrors | Static rule budget and live canonical headers, including a late-path book mirror |
| Search and legacy notes Markdown versions lacked their HTML pages' `noindex` policy | Add `X-Robots-Tag: noindex, follow` to excluded mirrors; allow fetching | Static and live checks |
| Production `pages.dev` alias serves an indexable duplicate | Restrict both Pages alias forms with host-specific `noindex, follow`, retaining production canonical URLs | Live alias and canonical-domain checks; a permanent domain redirect remains a possible hosting refinement |
| Clinical handbook snippet still promised Telegram after Drive migration | Correct its meta description to available Drive access | Generated metadata assertion |
| Subject titles/descriptions implied TANUVAS and books even when unavailable | Describe the actual resources present; keep subject and BVSc search intent clear | Source-driven metadata and normal unique-description checks |
| No unified route for original TANUVAS course-code discovery | Add `/bvsc/tanuvas-notes/` with all 42 reviewed entries, source context, current-syllabus links and no invented fourth-year collection | Exact source ID parity; deep links target real subject entries |
| Syllabus tools buried in individual subject routes | Add `/bvsc/syllabus/` with 19 checklists, theory/practical counts, four course-outline PDFs, curriculum source and year-grouping explanation | Checklist links and source-data validation |
| Weak discovery of these study tasks from entry pages | Add compact Home, BVSc index and More menu links; index both directories in site search | Reachability, mobile layout and keyboard/accessibility checks |
| Cover images not advertised in the sitemap | Add existing book-cover image URLs to canonical book entries | Local file and namespace validation |
| No search-engine change notification | Add IndexNow, with a live key/sitemap check, initial canonical URL submission and changed/added/deleted URLs only afterward | Offline change selection tests and logged live acceptance status |
| Search HTTP audit logged problems without failing | Make observed crawl-policy regressions fail verification, retry transport errors once, inspect alias and Markdown headers | Production audit exit status and diagnostics |
| Team attribution needed to remain accurate | Retain anonymous team authorship, explain editorial approach and distinguish linked source authors | About content and structured author checks |

## AI and LLM visibility

The primary content remains server-rendered HTML, with canonical URLs, headings, real internal links, source credits and source-backed course information. Existing Markdown mirrors, `llms.txt` and `llms-full.txt` remain available and generated from the same page content. They are convenience formats, not a ranking factor or proof that a model will cite the site. Google explicitly says it does not use `llms.txt` for rankings. OAI-SearchBot is already allowed independently of training crawlers; no extra training permissions were added for this change.

Structured data describes what is on the page. No fake qualifications, reviews, ratings, official university affiliation or medical authority were added. No keyword-stuffed doorway pages, hidden SEO text, invented experience, paid backlinks or mass-generated subject articles were introduced.

## Owner actions and measurement

1. Keep the existing Search Console property and sitemap. After publication, inspect the two new directory URLs and request indexing once. Repeated requests do not accelerate ranking.
2. Check Search Console's Pages report for important subject URLs, and review Manual actions and Security issues. The homepage screenshot alone cannot establish the status of the other pages.
3. Import the verified property into Bing Webmaster Tools and submit `https://notes.thatvetguy.net/sitemap.xml`. IndexNow does not replace the reporting benefits of an account and is not a Google submission mechanism.
4. Record a baseline from Search Console Performance: last 28 days, India and all countries, mobile and desktop separately, clicks, impressions, CTR and average position. Track branded queries separately from non-branded queries. Compare like-for-like periods after recrawling; do not interpret a short-term fluctuation as causation.
5. Useful query groups correspond to actual pages: veterinary notes / BVSc study material (Home and BVSc index); TANUVAS notes (course directory); BVSc syllabus / MSVE 2016 checklist (syllabus directory); subject notes (subject pages); named books and question banks (book pages). No search-volume estimates were available.
6. For genuine authority, invite willing students and teaching staff to review a specific checklist or guide and report corrections. Seek voluntary links from relevant college resource pages and legitimate veterinary communities when the resource helps their readers. Do not buy links or manufacture Reddit/Quora endorsements. No outreach messages were sent during this task.
7. Prioritise original, accurately reviewed material: annotated specimen identification guides, worked question explanations and course-to-topic mappings with contributor permission and clear review attribution. Add these only when actual content and reviewers are available; this work does not invent an expert author.
8. In Bing Webmaster Tools, use Search Performance and the available AI Performance reporting to measure visibility. Search Console's available AI reports can complement normal web-search metrics. AI citations and traffic cannot be guaranteed by metadata.

## Sources checked

- Google: https://developers.google.com/search/docs/fundamentals/ai-optimization-guide
- Google AI eligibility: https://developers.google.com/search/docs/appearance/ai-features
- Sitemap submission and truthful lastmod: https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap
- Limits of site searches: https://developers.google.com/search/docs/monitor-debug/search-operators/all-search-site
- Cloudflare header rules, 100-rule limit and alias exclusions: https://developers.cloudflare.com/pages/configuration/headers/
- Cloudflare redirect capabilities: https://developers.cloudflare.com/pages/configuration/redirects/
- IndexNow protocol: https://www.indexnow.org/documentation
- OpenAI crawler purposes: https://developers.openai.com/api/docs/bots
- Bing AI Performance: https://blogs.bing.com/webmaster/2026/2/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview/

Indexing, top positions, AI inclusion and visitor growth remain decisions of search engines and users; no technical audit can promise them.

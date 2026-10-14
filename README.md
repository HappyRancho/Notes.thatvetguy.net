# Notes.ThatVetGuy

A free veterinary academic and study-resource platform, primarily for BVSc & AH students. The homepage, category content, year lists and external source links are static HTML. JavaScript enhances search, year tabs and the mobile navigation.

## Edit and build

Edit `data/resources.json` and `data/subjects.json` for content and credited material. `data/content-contract.json` locks the requested homepage content and earlier year grouping; update it only when the product requirements deliberately change. Edit `scripts/build.py` for page composition; edit `assets/site.css` and `assets/site.js` for presentation and behaviour.

```sh
python3 scripts/build.py
python3 scripts/check.py
node --check assets/site.js
python3 -m http.server 8000
```

Deploy the repository root. Generated pages are committed so a production build service is unnecessary. Root-relative URLs assume hosting at `notes.thatvetguy.net`.

## Search and AI discovery

- Useful content and normal links exist without JavaScript, including all professional years.
- Each page has a canonical URL, unique title/description and consistent `WebSite`, `Organization`, `WebPage`/`CollectionPage`, `ItemList` and breadcrumb JSON-LD where applicable. Markup describes visible content; it does not assert medical authorship or review.
- `robots.txt` permits public crawling, explicitly including OAI-SearchBot. `sitemap.xml` lists indexable pages; internal search results use `noindex,follow`.
- `llms.txt` provides a concise optional directory for compatible readers. It is not a ranking mechanism or a substitute for accessible content. Google states that it does not use llms.txt for rankings.
- Content and metadata share the same generator. Do not add hidden keyword blocks, fake reviews, fabricated authority or special content for bots.
- Source links are attributed. Current listings point to external resources; planned books are labelled as unavailable downloads. This site does not host third-party textbooks.

Indexing, inclusion and citations in AI answers are not guaranteed. After deploying, check that the actual hosting/CDN allows crawlers and returns these pages successfully. Verify the domain in Google Search Console and Bing Webmaster Tools and submit the sitemap using the owner's accounts.

References: [Google's AI search guidance](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide), [OpenAI crawler documentation](https://developers.openai.com/api/docs/bots), [VCI MSVE 2016, section 20](https://www.vci.dahd.gov.in/sites/default/files/IVPR/MSVE-Gazette-2016.pdf#page=103).

## Design and accessibility

One midnight-blue, warm-ivory and muted-apricot palette; compact search; equal objective links; a revision-note treatment for Backbenchers. No external fonts, animation libraries, tracking, login or runtime framework. Search catalogue loads only on interaction. Motion respects reduced-motion preferences; content never depends on reveal animations. Native modal navigation supports Escape, outside click, focus containment, link dismissal and scroll lock.

## Verification

The structural audit covers links/anchors, schema JSON, visible catalogue content, indexable URLs, robots access and representative WCAG AA text pairs. JavaScript syntax is checked separately. Browser visual and interaction checks must run in a browser-capable environment; the current managed sandbox blocked Chromium socket operations.

Content preservation and reviewed source decisions are documented in [docs/source-audit.md](docs/source-audit.md). Every subject now keeps separate Notes and Books choices instead of repeating the same two generic directories.

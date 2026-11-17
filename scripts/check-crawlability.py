"""Check canonical sitemap routes and their crawl paths through static HTML."""
from collections import deque
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
BASE = 'https://notes.thatvetguy.net'

class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.links, self.canonicals, self.robots = set(), [], []
        self.feed(path.read_text())
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'a':
            url = urlsplit(a.get('href', ''))
            if not url.netloc or url.netloc == urlsplit(BASE).netloc:
                if url.path.startswith('/'):
                    self.links.add(unquote(url.path))
        if tag == 'link' and a.get('rel') == 'canonical':
            self.canonicals.append(a.get('href'))
        if tag == 'meta' and a.get('name') == 'robots':
            self.robots.append(a.get('content', '').lower())

urls = [e.text for e in ET.parse(ROOT/'sitemap.xml').findall('.//{*}url/{*}loc')]
assert len(urls) == len(set(urls)), 'Duplicate sitemap URLs'
pages = {}
for url in urls:
    assert url.startswith(BASE+'/') and url.endswith('/'), url
    route = urlsplit(url).path
    file = ROOT/route.lstrip('/')/'index.html'
    assert file.is_file(), (route, 'Missing sitemap page')
    page = pages[route] = Page(file)
    assert page.canonicals == [url], (route, 'Canonical mismatch')
    assert page.robots and all('noindex' not in r and 'nofollow' not in r for r in page.robots), (route, 'Not indexable')
    for target in page.links:
        assert (ROOT/target.lstrip('/')).exists(), (route, 'Broken internal link', target)
# Follow ordinary anchors only, without search, JavaScript, or Markdown mirrors.
seen, queue = {'/': 0}, deque(['/'])
while queue:
    route = queue.popleft()
    for target in pages[route].links:
        if target in pages and target not in seen:
            seen[target] = seen[route]+1
            queue.append(target)
assert set(pages) <= set(seen), ('Orphan indexable pages', set(pages)-set(seen))
print(f'CRAWLABILITY: {len(pages)} canonical sitemap pages; no orphans or broken internal links; maximum depth {max(seen.values())}.')

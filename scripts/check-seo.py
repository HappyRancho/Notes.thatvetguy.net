#!/usr/bin/env python3
"""Regression checks for crawl targets, equivalent representations and freshness."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from collections import deque
import datetime,json,re,xml.etree.ElementTree as ET
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
BASE='https://notes.thatvetguy.net'
class Document(HTMLParser):
    def __init__(self,raw):
        super().__init__();self.links=[];self.meta={};self.canonical=[];self.alternates=[];self.title='';self.in_title=False;self.h1=0;self.schemas=[];self.in_schema=False;self.buffer='';self.feed(raw)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='a':self.links.append(a.get('href',''))
        if tag=='h1':self.h1+=1
        if tag=='title':self.in_title=True
        if tag=='meta':self.meta[a.get('name') or a.get('property')]=a.get('content')
        if tag=='link' and a.get('rel')=='canonical':self.canonical.append(a['href'])
        if tag=='link' and a.get('rel')=='alternate' and a.get('type')=='text/markdown':self.alternates.append(a['href'])
        if tag=='script' and a.get('type')=='application/ld+json':self.in_schema=True;self.buffer=''
    def handle_data(self,text):
        if self.in_title:self.title+=text
        if self.in_schema:self.buffer+=text
    def handle_endtag(self,tag):
        if tag=='title':self.in_title=False
        if tag=='script' and self.in_schema:self.schemas+=json.loads(self.buffer)['@graph'];self.in_schema=False

def check():
    nodes=ET.parse(ROOT/'sitemap.xml').getroot();ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
    entries={n.find('s:loc',ns).text:n.find('s:lastmod',ns).text for n in nodes}
    history=json.loads((ROOT/'data/page-history.json').read_text());documents={};titles=set();descriptions=set()
    checked_images=set()
    for url,date in entries.items():
        path=urlsplit(url).path;p=ROOT/path.strip('/')/'index.html';d=Document(p.read_text());documents[path]=d
        assert d.canonical==[url],(path,'canonical')
        assert 'noindex' not in d.meta.get('robots',''),(path,'robots')
        assert d.h1==1,(path,'one H1')
        assert d.title not in titles,(path,'duplicate title');titles.add(d.title)
        description=d.meta.get('description');assert description and description not in descriptions,(path,'duplicate/missing description');descriptions.add(description)
        preview=d.meta.get('og:image','');assert preview.startswith(BASE+'/assets/social/'),(path,'social image origin')
        assert d.meta.get('twitter:image')==preview and d.meta.get('og:image:secure_url')==preview,(path,'social image mismatch')
        assert d.meta.get('og:image:width')=='1200' and d.meta.get('og:image:height')=='630',(path,'social dimensions')
        assert d.meta.get('og:image:alt') and d.meta.get('twitter:image:alt'),(path,'social image alt text')
        if not path.startswith('/books/'):assert '/assets/social/rx-' in preview and preview.endswith('.jpg'),(path,'legacy section card')
        if preview not in checked_images:
            with Image.open(ROOT/urlsplit(preview).path.lstrip('/')) as picture:
                assert picture.size==(1200,630),(path,'preview dimensions')
                assert d.meta.get('og:image:type')==Image.MIME[picture.format],(path,'preview MIME type')
            checked_images.add(preview)
        assert d.alternates==[url+'index.md'],(path,'markdown discovery')
        assert (ROOT/path.strip('/')/'index.md').exists(),(path,'mirror')
        assert date==history[path]['modified'] and date<=datetime.date.today().isoformat(),(path,'lastmod')
        page=next(x for x in d.schemas if x.get('@id')==url+'#webpage');assert page['dateModified']==date
        assert page['description']==description,(path,'schema/meta description mismatch')
        headers=(ROOT/'_headers').read_text()
        rule='/index.md\n  Link: <'+BASE+'/>; rel="canonical"' if path=='/' else '/*/index.md\n  Link: <'+BASE+'/:splat/>; rel="canonical"'
        assert rule in headers,(path,'mirror canonical rule')
    seen={'/'};queue=deque(['/'])
    while queue:
        for href in documents[queue.popleft()].links:
            u=urlsplit(href)
            if u.scheme or u.netloc:continue
            path=u.path
            if path in documents and path not in seen:seen.add(path);queue.append(path)
    assert seen==set(documents),('orphan sitemap pages',set(documents)-seen)
    search=Document((ROOT/'search/index.html').read_text());assert 'noindex' in search.meta['robots'] and BASE+'/search/' not in entries
    header_text=(ROOT/'_headers').read_text()
    header_rules=[line for line in header_text.splitlines() if line and not line.startswith(('#',' ','\t'))]
    assert len(header_rules)<=100,('Cloudflare supports at most 100 header rules',len(header_rules))
    assert all(len(line)<=2000 for line in header_text.splitlines()),'Cloudflare header line limit'
    assert 'https://notes-thatvetguy-net.pages.dev/*\n  X-Robots-Tag: noindex, follow' in header_text
    for path in ['/search/','/404/']+[f'/bvsc/year-{y}/notes/' for y in range(1,5)]:
        assert path+'index.md\n  X-Robots-Tag: noindex, follow' in header_text,(path,'Excluded mirror must remain excluded')
    for node in nodes:
        for picture in node.findall('{http://www.google.com/schemas/sitemap-image/1.1}image'):
            source=picture.find('{http://www.google.com/schemas/sitemap-image/1.1}loc').text
            assert source.startswith(BASE+'/assets/books/') and (ROOT/urlsplit(source).path.lstrip('/')).is_file(),('Missing sitemap cover',source)
    for path in ['/bvsc/tanuvas-notes/','/bvsc/syllabus/']:
        assert path in documents and path in documents['/'].links and path in documents['/bvsc/'].links,(path,'Directory discovery')
    tanuvas=(ROOT/'bvsc/tanuvas-notes/index.html').read_text()
    source=json.loads((ROOT/'data/tanuvas-source.json').read_text())
    assert set(re.findall(r'data-tanuvas-course="([^"]+)"',tanuvas))=={r['id'] for r in source['notes']},'TANUVAS directory must mirror reviewed source entries'
    syllabus=(ROOT/'bvsc/syllabus/index.html').read_text()
    for subject in json.loads((ROOT/'data/subject-syllabi.json').read_text())['subjects']:
        assert '/bvsc/year-'+str(subject['year'])+'/'+subject['slug']+'/syllabus/' in syllabus
    assert 'Telegram' not in documents['/clinical/handbooks/'].meta['description'],'Outdated access description'
    from importlib.util import spec_from_file_location,module_from_spec
    spec=spec_from_file_location('indexnow',ROOT/'scripts/notify-indexnow.py');notify=module_from_spec(spec);spec.loader.exec_module(notify)
    current={BASE+'/',BASE+'/new/'};old={BASE+'/',BASE+'/gone/'}
    assert notify.changed(current,old,{'/':{'sha256':'a'}},{'/':{'sha256':'a'}})==[BASE+'/gone/',BASE+'/new/']
    assert notify.changed({BASE+'/'},{BASE+'/'},{'/':{'sha256':'b'}},{'/':{'sha256':'a'}})==[BASE+'/']
    assert notify.changed(current,old,{}, {},True)==sorted(current)

    for s in json.loads((ROOT/'data/subject-map.json').read_text())['years'].values():
        for subject in s:
            # Source URLs are never rewritten by this audit.
            assert subject in json.loads((ROOT/'data/subjects.json').read_text())
    print(f'PASS SEO: {len(entries)} reachable sitemap pages, unique metadata, canonical mirrors, matching schema and content dates.')

if __name__=='__main__':check()

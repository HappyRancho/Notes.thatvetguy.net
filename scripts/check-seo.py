#!/usr/bin/env python3
"""Regression checks for crawl targets, equivalent representations and freshness."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from collections import deque
import datetime,json,re,xml.etree.ElementTree as ET
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
    for url,date in entries.items():
        path=urlsplit(url).path;p=ROOT/path.strip('/')/'index.html';d=Document(p.read_text());documents[path]=d
        assert d.canonical==[url],(path,'canonical')
        assert 'noindex' not in d.meta.get('robots',''),(path,'robots')
        assert d.h1==1,(path,'one H1')
        assert d.title not in titles,(path,'duplicate title');titles.add(d.title)
        description=d.meta.get('description');assert description and description not in descriptions,(path,'duplicate/missing description');descriptions.add(description)
        assert d.alternates==[url+'index.md'],(path,'markdown discovery')
        assert (ROOT/path.strip('/')/'index.md').exists(),(path,'mirror')
        assert date==history[path]['modified'] and date<=datetime.date.today().isoformat(),(path,'lastmod')
        page=next(x for x in d.schemas if x.get('@id')==url+'#webpage');assert page['dateModified']==date
        assert page['description']==description,(path,'schema/meta description mismatch')
        assert f'{path}index.md\n  Link: <{url}>; rel="canonical"' in (ROOT/'_headers').read_text(),(path,'mirror canonical header')
    seen={'/'};queue=deque(['/'])
    while queue:
        for href in documents[queue.popleft()].links:
            u=urlsplit(href)
            if u.scheme or u.netloc:continue
            path=u.path
            if path in documents and path not in seen:seen.add(path);queue.append(path)
    assert seen==set(documents),('orphan sitemap pages',set(documents)-seen)
    search=Document((ROOT/'search/index.html').read_text());assert 'noindex' in search.meta['robots'] and BASE+'/search/' not in entries
    for s in json.loads((ROOT/'data/subject-map.json').read_text())['years'].values():
        for subject in s:
            # Source URLs are never rewritten by this audit.
            assert subject in json.loads((ROOT/'data/subjects.json').read_text())
    print(f'PASS SEO: {len(entries)} reachable sitemap pages, unique metadata, canonical mirrors, matching schema and content dates.')

if __name__=='__main__':check()

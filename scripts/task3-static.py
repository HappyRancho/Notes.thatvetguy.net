#!/usr/bin/env python3
"""Independent checks for provenance, counts, pagination, links and machine retrieval."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from collections import Counter
import json,re,gzip,xml.etree.ElementTree as ET,importlib.util
from library_views import keep_complete_resource
ROOT=Path(__file__).resolve().parent.parent
class Page(HTMLParser):
    def __init__(self,path):super().__init__();self.path=path;self.ids=set();self.urls=[];self.headings=[];self.rows=[];self.capture=False;self.schema=[];self.buffer='';self.themes=[]
    def handle_starttag(self,t,attrs):
        a=dict(attrs)
        if a.get('id'):
            assert a['id'] not in self.ids,(self.path,'duplicate id',a['id']);self.ids.add(a['id'])
        if re.fullmatch('h[1-6]',t):self.headings.append(int(t[1]))
        if a.get('data-resource-id'):self.rows.append(a['data-resource-id'])
        if t=='a':
            assert a.get('href') not in ['',None,'#'],(self.path,'empty link')
            if a['href'].startswith(('https:','http:')):assert a.get('target')=='_blank' and {'noopener','noreferrer'}<=set(a.get('rel','').split())
            else:assert 'target' not in a
        if t=='meta' and a.get('name')=='theme-color':self.themes.append(a.get('media'))
        for k in ['src','href']:
            if k in a:self.urls.append(a[k])
        if t=='script' and a.get('type')=='application/ld+json':self.capture=True;self.buffer=''
    def handle_endtag(self,t):
        if t=='script' and self.capture:self.schema=json.loads(self.buffer)['@graph'];self.capture=False
    def handle_data(self,s):
        if self.capture:self.buffer+=s
pages={}
for p in ROOT.rglob('index.html'):
    if any(x in p.parts for x in ['node_modules','docs','.git','dist']):continue
    raw=p.read_text();page=Page(p);page.feed(raw);pages[p]=page
    assert page.headings.count(1)==1 and page.headings[0]==1,(p,'heading order')
    previous=0
    for h in page.headings:assert h<=previous+1,(p,'heading skip',h);previous=h
    assert page.themes==['(prefers-color-scheme: light)','(prefers-color-scheme: dark)']
    assert not re.search(r'\b(supplied|indexed|matching files|Drive library|original revision guidance)\b',raw,re.I),(p,'developer copy')
    assert '<h2>Explore.' not in raw and 'Unsorted' not in raw
    assert p.with_suffix('.md').exists(),(p,'markdown')
    types={g['@type'] for g in page.schema};assert {'Organization','Person','WebSite'}<=types
    assert ('FAQPage' in types)==(p.parent.name in ['about','request-resource'])
    if p!=ROOT/'index.html':assert 'BreadcrumbList' in types
for p,page in pages.items():
    for url in page.urls:
        u=urlsplit(url)
        if u.scheme or u.netloc:continue
        dest=ROOT/u.path.lstrip('/') if u.path.startswith('/') else p.parent/u.path
        if not u.path:dest=p
        elif u.path.endswith('/'):dest=dest/'index.html'
        assert dest.exists(),(p,'missing destination',url)
        if u.fragment and dest in pages:assert unquote(u.fragment) in pages[dest].ids,(p,'missing anchor',url)
data=json.loads((ROOT/'data/resources.json').read_text());records=data['files'];raw=json.loads((ROOT/'data/drive_manifest.json').read_text());report=json.loads((ROOT/'data/duplicates-report.json').read_text());search=json.loads((ROOT/'search-index.json').read_text())
rawids={f['id'] for f in raw};accounted=[]
for r in records:accounted+=r['photoIds'] or [v['id'] for v in r['variants']];accounted+=r['duplicateIds']
assert set(accounted)==rawids and len(accounted)==len(rawids),'lost or multiply-owned original file'
visible_records=[r for r in records if keep_complete_resource(r)]
assert {r['id'] for r in search}=={r['id'] for r in visible_records},'search mismatch'
assert not any(re.match(r'^(IMG[-_]|PXL_|DSC[_-]|Screenshot)',r['title'],re.I) for r in search),'camera file title'
counts=Counter(rid for p in pages.values() for rid in p.rows)
for r in records:
    if not keep_complete_resource(r):
        assert counts[r['id']]==0,(r['id'],'hidden topic material still listed',counts[r['id']])
        continue
    assert counts[r['id']]==1,(r['id'],'canonical row count',counts[r['id']])
    assert r['id'] in pages[ROOT/r['page'].strip('/')/'index.html'].rows
    assert r['kind'] in ['notes','books','practical','objective','presentation','images','other']
    for v in r['variants']:assert bool(v['download'])==bool(not r['photoIds'] and isinstance(v['size'],int) and v['size']<25_000_000 and not v['mime'].startswith('application/vnd.google-apps.'))
for y in data['years']:
    assert y['count']==sum(s['count'] for s in y['subjects'])+len(y['extras'])
    for s in y['subjects']:assert s['count']==sum(s['groups'].values())==len(s['resourceIds'])
assert not any('icar-pyq' in r['collections'] for r in records),'Unverified ICAR PYQ'
assert len([r for r in records if r['title']=='Toxicology Objectives'])==1
assert next(r for r in records if r['title'].lower()=='micro mcq')['kind']=='objective'
assert not any('drug-index' in r['collections'] for r in records if r['id'] in ['1B7aVgkhm3eEoEVK1PrquHqa2WuWXQPeE','1ttttsajUvalFa9eL2CX6_3pbnBLnqqH2'])
home=(ROOT/'index.html').read_text();assert all(x not in home for x in ['faq-list','Recently Added','quick-tiles'])
assert home.count('role="tablist"')==3 and 'BVSc &amp; AH Resources' in home
assert 'content="noindex,follow"' in (ROOT/'search/index.html').read_text()
xml=ET.parse(ROOT/'sitemap.xml');ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
assert len(xml.findall('s:url',ns))==sum('content="noindex,follow"' not in p.read_text() for p in pages)
assert all(el.find('s:lastmod',ns) is not None for el in xml.findall('s:url',ns))
assert all((ROOT/x).exists() for x in ['llms.txt','llms-full.txt','robots.txt','search-index.json'])
runtime=sum(len(gzip.compress((ROOT/'assets'/p).read_bytes())) for p in ['theme.js','logic.js','site.js','motion.js','homepage.js']);assert runtime<60_000
payload=runtime+len(gzip.compress(home.encode()))+sum(len(gzip.compress((ROOT/'assets'/p).read_bytes())) for p in ['site.css','homepage.css','rx-pages.css']);assert payload<150_000
spec=importlib.util.spec_from_file_location('policy',ROOT/'scripts/check-link-policy.py');policy=importlib.util.module_from_spec(spec);spec.loader.exec_module(policy);policy.check_policy()
out=ROOT/'docs/qa/task3';out.mkdir(parents=True,exist_ok=True)
(out/'counts.json').write_text(json.dumps({'years':data['years'],'cleanup':report,'homeGzipBytes':payload,'jsGzipBytes':runtime},indent=2)+'\n')
print(f'PASS {len(pages)} pages; {len(rawids)} originals accounted for; {len(visible_records)} public rows in search. Home HTML/CSS/JS {payload} bytes gzip; JS {runtime}.')

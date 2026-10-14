#!/usr/bin/env python3
"""Check static HTML, crawl paths, structured data and contrast before publishing."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
from urllib.robotparser import RobotFileParser
import json
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent.parent
class Page(HTMLParser):
    def __init__(self,path):
        super().__init__();self.path=path;self.ids=set();self.urls=[];self.h1=0;self.jsons=[];self.capture=False;self.buffer='';self.canonical=None
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:
            assert a['id'] not in self.ids,(self.path,'Duplicate id',a['id'])
            self.ids.add(a['id'])
        if tag=='h1':self.h1+=1
        if tag=='a':
            assert a.get('href') not in ('','#',None),(self.path,'Empty link')
        for key in ['href','src']:
            if key in a:self.urls.append(a[key])
        if tag=='script' and a.get('type')=='application/ld+json':self.capture=True;self.buffer=''
        if tag=='link' and a.get('rel')=='canonical':self.canonical=a['href']
    def handle_data(self,text):
        if self.capture:self.buffer+=text
    def handle_endtag(self,tag):
        if tag=='script' and self.capture:
            self.jsons.append(json.loads(self.buffer));self.capture=False

pages={}
for path in ROOT.rglob('index.html'):
    if any(part in path.parts for part in ['shared','scratch','library-files']):continue
    parser=Page(path.relative_to(ROOT));parser.feed(path.read_text());pages[path]=parser
    assert parser.h1==1,(path,'Expected one H1')
    assert parser.jsons and parser.jsons[0]['@context']=='https://schema.org'
    assert parser.canonical and parser.canonical.startswith('https://notes.thatvetguy.net/')
for path,page in pages.items():
    for url in page.urls:
        u=urlsplit(url)
        if u.scheme or u.netloc:continue
        dest=(ROOT/u.path.lstrip('/')) if u.path.startswith('/') else path.parent/u.path
        if not u.path:dest=path
        elif u.path.endswith('/'):dest=dest/'index.html'
        assert dest.exists(),(path,'Missing local destination',url)
        if u.fragment and dest in pages:assert unquote(u.fragment) in pages[dest].ids,(path,'Missing anchor',url)
    for graph in page.jsons[0]['@graph']:
        if graph['@type']=='ItemList':
            for item in graph['itemListElement']:
                assert item['name'] in path.read_text() or item['name'].replace('&','&amp;') in path.read_text(),(path,'Schema name not in page',item['name'])
data=json.loads((ROOT/'data/resources.json').read_text())
home=(ROOT/'index.html').read_text()
for names in data['years'].values():
    for name in names:assert name in home,'Subjects missing from static HTML'
assert not any('Farm Practices' in name for name in data['years']['4'])
assert 'Recently Added' not in home
css=(ROOT/'assets/site.css').read_text()
assert css.count('{')==css.count('}') and 'prefers-reduced-motion' in css
rp=RobotFileParser();rp.parse((ROOT/'robots.txt').read_text().splitlines())
for agent in ['OAI-SearchBot','Googlebot','Bingbot']:
    for url in ['https://notes.thatvetguy.net/','https://notes.thatvetguy.net/bvsc/']:assert rp.can_fetch(agent,url)
sitemap=ET.parse(ROOT/'sitemap.xml');ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
assert len(sitemap.findall('s:url',ns))==7

def luminance(h):
    c=[int(h[i:i+2],16)/255 for i in (1,3,5)]
    c=[x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in c]
    return sum(a*b for a,b in zip(c,[.2126,.7152,.0722]))
pairs=[('body','#233d32','#f7f7f0'),('secondary','#5c685e','#f7f7f0'),('link','#244d3d','#f7f7f0'),('placeholder','#69756b','#fffefa'),('subject number','#68765f','#fffefa'),('inactive tab','#233d32','#e8edde'),('selected tab','#fffefa','#244d3d'),('note text','#344022','#e8edba'),('note metadata','#54603c','#e8edba'),('AI copy','#5c685e','#eaf0e5'),('Telegram','#086b99','#f7f7f0'),('footer','#c8d4c3','#233f33'),('result type','#365340','#edf2e9')]
ratios=[]
for label,fg,bg in pairs:
    lo,hi=sorted([luminance(fg),luminance(bg)]);ratio=(hi+.05)/(lo+.05)
    assert ratio>=4.5,(label,ratio);ratios.append(ratio)
print(f'PASS: {len(pages)} pages; local destinations and anchors; one H1 per page; JSON-LD; sitemap; crawler access; all subjects in static HTML; {len(pairs)} contrast pairs (minimum {min(ratios):.2f}:1).')

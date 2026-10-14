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
        super().__init__();self.path=path;self.ids=set();self.urls=[];self.h1=0;self.jsons=[];self.capture=False;self.buffer='';self.canonical=None;self.text=[];self.sections=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:
            assert a['id'] not in self.ids,(self.path,'Duplicate id',a['id'])
            self.ids.add(a['id'])
        if tag=='h1':self.h1+=1
        if tag=='section' and 'id' in a:self.sections.append(a['id'])
        if tag=='a':
            assert a.get('href') not in ('','#',None),(self.path,'Empty link')
        for key in ['href','src']:
            if key in a:self.urls.append(a[key])
        if tag=='script' and a.get('type')=='application/ld+json':self.capture=True;self.buffer=''
        if tag=='link' and a.get('rel')=='canonical':self.canonical=a['href']
    def handle_data(self,text):
        if not self.capture:self.text.append(text)
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
contract=json.loads((ROOT/'data/content-contract.json').read_text())
assert data['years']==contract['years'],'Professional-year subjects drifted from the preserved content'
assert data['objectiveBooks']==contract['objectiveBooks'],'Objective book names were changed'
homepage=pages[ROOT/'index.html']
visible=' '.join(' '.join(homepage.text).split())
for phrase in contract['requiredText']+contract['searchExamples']:
    assert phrase in visible,('Required homepage content missing',phrase)
assert [s for s in homepage.sections if s in contract['requiredSections']]==contract['requiredSections'],'Homepage section flow changed'
for url in contract['telegram'].values():assert url in homepage.urls,'Telegram channel missing or changed'
subjects=json.loads((ROOT/'data/subjects.json').read_text())
assert set(subjects)=={subject for names in data['years'].values() for subject in names}
for subject,material in subjects.items():
    assert material['notes'],('Missing notes source',subject)
    assert 'sourceChecked' in material
    for bucket in ['notes','books']:
        for item in material[bucket]:
            assert item['url'].startswith('https://'),('Unusable source URL',subject)
assert 'download-best-veterinary-e-learning-app_83.html' not in (ROOT/'objective/index.html').read_text(),'Objective questions still lead to the general app/materials page'
for names in data['years'].values():
    for name in names:assert name in home,'Subjects missing from static HTML'
assert not any('Farm Practices' in name for name in data['years']['4'])
assert 'Recently Added' not in home
css=(ROOT/'assets/site.css').read_text()
assert css.count('{')==css.count('}') and 'prefers-reduced-motion' in css
asides=json.loads((ROOT/'data/section-asides.json').read_text())
assert set(asides)=={'backbench','tools'} and len(asides)==2
for aside in asides.values():assert visible.count(aside)==1,('Section aside repeated or missing',aside)
assert 'forced-colors:active' in css
assert (ROOT/'data/content-contract.json').read_bytes(), 'Missing content contract'
rp=RobotFileParser();rp.parse((ROOT/'robots.txt').read_text().splitlines())
for agent in ['OAI-SearchBot','Googlebot','Bingbot']:
    for url in ['https://notes.thatvetguy.net/','https://notes.thatvetguy.net/bvsc/']:assert rp.can_fetch(agent,url)
sitemap=ET.parse(ROOT/'sitemap.xml');ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
assert len(sitemap.findall('s:url',ns))==7

def luminance(h):
    c=[int(h[i:i+2],16)/255 for i in (1,3,5)]
    c=[x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in c]
    return sum(a*b for a,b in zip(c,[.2126,.7152,.0722]))
pairs=[('body','#183c36','#fffaf2'),('secondary','#59706b','#fffaf2'),('link','#a93c2b','#fffaf2'),('placeholder','#59706b','#ffffff'),('subject number','#59706b','#ffffff'),('inactive tab','#183c36','#edf3ed'),('selected tab','#ffffff','#183c36'),('note text','#213d32','#dbf07d'),('note metadata','#405e35','#dbf07d'),('AI copy','#59706b','#fff0ea'),('Telegram','#086b99','#fffaf2'),('footer','#dce9dd','#183c36'),('result type','#36574c','#edf3ed'),('coral button','#102c26','#ef6a50'),('coral button hover','#102c26','#f27b63'),('aside','#49635e','#fffaf2'),('AI aside','#49635e','#fff0ea'),('AI label','#a93c2b','#fff0ea')]
ratios=[]
for label,fg,bg in pairs:
    lo,hi=sorted([luminance(fg),luminance(bg)]);ratio=(hi+.05)/(lo+.05)
    assert ratio>=4.5,(label,ratio);ratios.append(ratio)
print(f'PASS: {len(pages)} pages; preserved homepage copy/flow, year subjects and book names; credited Notes/Books sources; local links and anchors; JSON-LD; sitemap; crawler access; {len(pairs)} contrast pairs (minimum {min(ratios):.2f}:1).')

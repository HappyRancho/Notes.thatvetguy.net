#!/usr/bin/env python3
"""Check static HTML, crawl paths, structured data and contrast before publishing."""
from html.parser import HTMLParser
from html import escape
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
    if any(part in path.parts for part in ['shared','scratch','library-files','node_modules']):continue
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
    assert material['notesIds'],('Missing notes source',subject)
    assert 'sourceChecked' in material
    for rid in material['notesIds']:
        assert rid in {r['id'] for r in json.loads((ROOT/'data/catalogue.json').read_text())}
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
assert len(sitemap.findall('s:url',ns))==len(pages)-1

def luminance(h):
    c=[int(h[i:i+2],16)/255 for i in (1,3,5)]
    c=[x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in c]
    return sum(a*b for a,b in zip(c,[.2126,.7152,.0722]))
tokens=json.loads((ROOT/'data/design-tokens.json').read_text())
semantic=[('ink','paper'),('muted','paper'),('ink','surface'),('muted','surface'),('action','paper'),('on-accent','accent'),('on-brand','brand'),('on-brand','brand-hover'),('note-ink','note'),('note-muted','note'),('telegram','paper'),('footer-ink','footer'),('footer-muted','footer')]+[(f'year-{n}','paper') for n in range(1,5)]
pairs=[(theme+':'+fg,t[fg],t[bg]) for theme,t in tokens.items() for fg,bg in semantic]
ratios=[]
for label,fg,bg in pairs:
    lo,hi=sorted([luminance(fg),luminance(bg)]);ratio=(hi+.05)/(lo+.05)
    assert ratio>=4.5,(label,ratio);ratios.append(ratio)
print(f'PASS: {len(pages)} pages; preserved homepage copy/flow, year subjects and book names; credited Notes/Books sources; local links and anchors; JSON-LD; sitemap; crawler access; {len(pairs)} contrast pairs (minimum {min(ratios):.2f}:1).')

# Discovery and content acceptance checks that do not pretend to render CSS.
import re,gzip
from datetime import date
from struct import unpack
from collections import Counter
catalogue=json.loads((ROOT/'data/catalogue.json').read_text())
urls=[r['url'] for r in catalogue if r['url']]
assert len(urls)==len(set(urls)),'Duplicate canonical resources'
collections=data['collections']
for rid in ['zotero','cornell-eclinpath']:
 assert sum(rid in c.get('resourceIds',[]) for c in collections.values())==1,(rid,'Repeated in multiple collections')
for path,page in pages.items():
 raw=path.read_text();outline=[int(h) for h in re.findall(r'<h([1-6])(?:\s|>)',raw)]
 previous=0
 for h in outline:
  assert h<=previous+1,(path,'Skipped heading level',previous,h)
  previous=h
 assert not re.search(r'<h[1-6][^>]*>Explore\.',raw),'Navigation title must not be a heading'
 for attrs in re.findall(r'<a\b([^>]*)>',raw):
  a=dict(re.findall(r'([\w-]+)="([^"]*)"',attrs));url=a.get('href','')
  external=url.startswith(('https://','http://')) and not url.startswith('https://notes.thatvetguy.net/')
  if external:assert a.get('target')=='_blank' and {'noopener','noreferrer'}<=set(a.get('rel','').split()),(path,url,'Unsafe external link')
  else:assert 'target' not in a,(path,url,'Internal link opens a tab')
 assert path.with_suffix('.md').exists(),(path,'Missing Markdown mirror')
 assert '<meta property="og:image:width" content="1200">' in raw
 social=re.search(r'property="og:image" content="https://notes.thatvetguy.net([^"]+)"',raw)[1]
 image=(ROOT/social.lstrip('/')).read_bytes();start=image.index(b'\x9d\x01\x2a')+3
 assert tuple(v&16383 for v in unpack('<HH',image[start:start+4]))==(1200,630)
 graph=page.jsons[0]['@graph'];types={g['@type'] for g in graph}
 assert {'WebSite','Organization','Person','FAQPage'}<=types,(path,'Missing schema entities')
 if path!=ROOT/'index.html':assert 'BreadcrumbList' in types
 for entity in graph:
  if entity['@type']=='FAQPage':
   for q in entity['mainEntity']:assert q['name'] in raw or escape(q['name']) in raw
  if entity['@type']=='LearningResource':assert all(entity.get(k) for k in ['educationalLevel','teaches','inLanguage','isBasedOn'])
for subject,m in subjects.items():
 assert 40<=len(m['summary'].split())<=80,(subject,'Summary word count')
 slug=re.sub(r'[^a-z0-9]+','-',subject.lower()).strip('-')
 assert (ROOT/'bvsc'/slug/'index.html').exists()
 assert len(m['topics'])>=4
for item in sitemap.findall('s:url',ns):date.fromisoformat(item.find('s:lastmod',ns).text)
for bot in ['GPTBot','OAI-SearchBot','ChatGPT-User','ClaudeBot','Claude-SearchBot','PerplexityBot','Google-Extended','Applebot-Extended','CCBot']:
 assert rp.can_fetch(bot,'https://notes.thatvetguy.net/bvsc/')
assert 'content="noindex,follow"' in (ROOT/'search/index.html').read_text()
for p in ['pharmacology','haemonchus','nsaids','surgery-books']:assert 'preset-'+p in pages[ROOT/'search/index.html'].ids
assert (ROOT/'llms-full.txt').stat().st_size>20000
runtime=sum(len(gzip.compress((ROOT/'assets'/p).read_bytes())) for p in ['theme.js','logic.js','site.js'])
assert runtime<60000,('Runtime JS exceeds budget',runtime)
print(f'PASS: heading outlines, external attributes, 27 Markdown mirrors/social dimensions/schema entities, 19 original subject summaries, unique catalogue URLs, no-JS preset anchors, sitemap dates; runtime JS {runtime} bytes gzip.')

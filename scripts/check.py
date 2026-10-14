#!/usr/bin/env python3
"""Static structure, data integrity, source policy, retrieval and contrast checks."""
from html.parser import HTMLParser
from html import escape
from pathlib import Path
from urllib.parse import urlsplit,unquote
import json,re,gzip,xml.etree.ElementTree as ET,importlib.util
from collections import Counter
ROOT=Path(__file__).resolve().parent.parent
class Page(HTMLParser):
 def __init__(self,path):super().__init__();self.path=path;self.ids=set();self.urls=[];self.h1=0;self.outline=[];self.capture=False;self.buffer='';self.jsons=[];self.canonical=None;self.cards=[];self.text=[];self.sections=[]
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if a.get('id'):
   assert a['id'] not in self.ids,(self.path,'Duplicate ID',a['id']);self.ids.add(a['id'])
  if t=='h1':self.h1+=1
  if re.fullmatch('h[1-6]',t):self.outline.append(int(t[1]))
  if t=='section' and 'id'in a:self.sections.append(a['id'])
  if t=='a':
   assert a.get('href') not in ['',None,'#'],(self.path,'Empty link')
   if a['href'].startswith(('https://','http://')):
    assert a.get('target')=='_blank' and {'noopener','noreferrer'}<=set(a.get('rel','').split()),(self.path,'Unsafe external link')
   else:assert 'target' not in a,(self.path,'Internal target')
  if t=='article' and a.get('data-resource-id'):self.cards.append(a['data-resource-id'])
  for k in ['href','src']:
   if k in a:self.urls.append(a[k])
  if t=='link' and a.get('rel')=='canonical':self.canonical=a['href']
  if t=='script' and a.get('type')=='application/ld+json':self.capture=True;self.buffer=''
 def handle_endtag(self,t):
  if t=='script' and self.capture:self.jsons.append(json.loads(self.buffer));self.capture=False
 def handle_data(self,t):
  if self.capture:self.buffer+=t
  else:self.text.append(t)
pages={}
for p in ROOT.rglob('index.html'):
 if any(a in p.parts for a in ['node_modules','docs','dist','.git']):continue
 parser=Page(p);parser.feed(p.read_text());pages[p]=parser
 assert parser.h1==1,(p,'Expected one H1')
 previous=0
 for h in parser.outline:assert h<=previous+1,(p,'Heading level skip');previous=h
 assert parser.canonical and parser.canonical.startswith('https://notes.thatvetguy.net/')
 assert parser.jsons and parser.jsons[0]['@context']=='https://schema.org'
 assert p.with_suffix('.md').exists(),(p,'Missing Markdown mirror')
 assert not re.search(r'<h2[^>]*>Explore\.',p.read_text())
for p,pg in pages.items():
 for url in pg.urls:
  u=urlsplit(url)
  if u.scheme or u.netloc:continue
  dest=(ROOT/u.path.lstrip('/')) if u.path.startswith('/') else p.parent/u.path
  if not u.path:dest=p
  elif u.path.endswith('/'):dest=dest/'index.html'
  assert dest.exists(),(p,'Missing destination',url)
  if u.fragment and dest in pages:assert unquote(u.fragment) in pages[dest].ids,(p,'Missing anchor',url)
 graph=pg.jsons[0]['@graph'];types={g['@type'] for g in graph}
 assert {'Organization','Person','WebSite','FAQPage'}<=types,(p,'Missing discovery schema')
 if p!=ROOT/'index.html':assert 'BreadcrumbList'in types
 for g in graph:
  if g['@type']=='ItemList':
   for item in g['itemListElement']:assert item['name'] in p.read_text() or escape(item['name']) in p.read_text(),(p,'Invisible schema name',item['name'])
  if g['@type']=='LearningResource':assert all(g.get(k) for k in ['educationalLevel','teaches','inLanguage','encodingFormat'])
data=json.loads((ROOT/'data/resources.json').read_text());records=data['files'];manifest=json.loads((ROOT/'data/drive_manifest.json').read_text());index=json.loads((ROOT/'search-index.json').read_text())
assert len({r['id'] for r in records})==len(records)
assert {f['id'] for f in manifest}=={r['id'] for r in records},'A manifest file was dropped'
assert {r['id'] for r in index if r['type']!='Subject'}=={r['id'] for r in records},'Search does not cover every file'
counts=Counter(rid for pg in pages.values() for rid in pg.cards)
for r in records:
 assert counts[r['id']]==1,(r['id'],'File must appear on exactly one canonical subject page',counts[r['id']])
 assert r['id'] in pages[ROOT/r['page'].strip('/')/'index.html'].cards
 assert bool(r['download'])==(isinstance(r['size'],int) and r['size']<25_000_000 and not r['mime'].startswith('application/vnd.google-apps.'))
 assert all(k in r for k in ['title','subject','year','type','source','url','description','lastVerified'])
contract=json.loads((ROOT/'data/content-contract.json').read_text());site=json.loads((ROOT/'data/site-content.json').read_text());home=pages[ROOT/'index.html'];visible=' '.join(' '.join(home.text).split())
assert site['years']==contract['years']
for text in contract['requiredText']+contract['searchExamples']:assert text in visible,('Missing homepage copy',text)
assert [s for s in home.sections if s in contract['requiredSections']]==contract['requiredSections']
assert not any('Farm Practices'in name for name in site['years']['4'])
assert 'Recently Added'not in visible
subjects=json.loads((ROOT/'data/subjects.json').read_text())
for name,m in subjects.items():assert 40<=len(m['summary'].split())<=80 and len(m['topics'])>=4
for preset in ['pharmacology','haemonchus','nsaids','surgery-books']:assert 'preset-'+preset in pages[ROOT/'search/index.html'].ids
assert 'content="noindex,follow"'in (ROOT/'search/index.html').read_text()
xml=ET.parse(ROOT/'sitemap.xml');ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
assert len(xml.findall('s:url',ns))==sum('content="noindex,follow"'not in p.read_text()for p in pages)
assert all(el.find('s:lastmod',ns)is not None for el in xml.findall('s:url',ns))
css=(ROOT/'assets/site.css').read_text();assert css.count('{')==css.count('}') and 'prefers-reduced-motion'in css and 'forced-colors:active'in css
micro=json.loads((ROOT/'data/microcopy.json').read_text())
for key in ['search','bvsc','objective','backbench','tools','clinical','jobs','request','footer','404','empty']:assert micro[key]
def lum(h):
 cs=[int(h[i:i+2],16)/255 for i in [1,3,5]];cs=[c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4 for c in cs];return sum(c*w for c,w in zip(cs,[.2126,.7152,.0722]))
tokens=json.loads((ROOT/'data/design-tokens.json').read_text());pairs=[('ink','paper'),('muted','paper'),('ink','surface'),('muted','surface'),('action','paper'),('on-brand','brand'),('on-accent','accent'),('footer-ink','footer'),('footer-muted','footer'),('note-ink','note'),('note-muted','note'),('ink','objective-panel'),('muted','objective-panel'),('ink','clinical-panel'),('muted','clinical-panel'),('tools-ink','tools-panel'),('tools-muted','tools-panel'),('tools-ink','tools-tile'),('tools-muted','tools-tile'),('tools-spark','tools-panel'),('jobs-button-ink','jobs-button'),('ink','jobs-panel'),('muted','jobs-panel')]
ratios=[]
for theme,t in tokens.items():
 for fg,bg in pairs:
  lo,hi=sorted([lum(t[fg]),lum(t[bg])]);ratio=(hi+.05)/(lo+.05);assert ratio>=4.5,(theme,fg,bg,ratio);ratios.append(ratio)
runtime=sum(len(gzip.compress((ROOT/'assets'/p).read_bytes()))for p in ['theme.js','logic.js','site.js']);assert runtime<60000
spec=importlib.util.spec_from_file_location('policy',ROOT/'scripts/check-link-policy.py');policy=importlib.util.module_from_spec(spec);spec.loader.exec_module(policy);policy.check_policy()
print(f'PASS: {len(pages)} routes; {len(records)} real files each on exactly one subject page and in search; valid headings/anchors/metadata/mirrors; {len(ratios)} AA pairs (min {min(ratios):.2f}:1); JS {runtime} bytes gzip.')

"""Assert published Tools routes, real app sources and progressive guide content."""
from pathlib import Path
import json,sys
from html.parser import HTMLParser
from study_tools import DATA,GUIDES,route
ROOT=Path(__file__).resolve().parent.parent
class Page(HTMLParser):
 def __init__(self):super().__init__();self.apps=[];self.hrefs=[];self.h1=0
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t=='a':self.hrefs.append(a.get('href',''))
  if t=='h1':self.h1+=1
  if t=='img' and '/tools/apps/' in a.get('src',''):self.apps.append(a)
for g in GUIDES:
 p=ROOT/route(g).strip('/')/'index.html';raw=p.read_text();page=Page();page.feed(raw)
 assert page.h1==1 and 'rx-tools.css?' in raw and 'study-tools.js?' in raw
 assert (p.with_suffix('.md')).exists() and 'LearningResource' in raw
 assert 'MSD Manual Professional' not in raw and 'com.msd.professional' not in raw
 assert route(g) in (ROOT/'llms.txt').read_text()
 assert route(g) in (ROOT/'sitemap.xml').read_text()
 if g['id']=='vet-apps':
  assert len(page.apps)==len(DATA['apps'])==10
  for a in DATA['apps']:
   assert (ROOT/a['icon'].lstrip('/')).is_file()
   assert (a['store'] in page.hrefs)==a['free'],'Paid app must not have Play download CTA'
  assert raw.count('on Google Play</span>')==4
  assert 'Biosphera' not in raw and 'app-how' not in raw
  assert 'Telegram link coming soon' in raw
 if g['id']=='online-resources':
  assert raw.count('data-tool-item')==len(DATA['resources'])
  assert all(r['url'] in page.hrefs for r in DATA['resources'])
 if g['id']=='veterinary-careers':
  assert raw.count('class="career-card"')==len(DATA['careers'])==13
  assert all(s['url'] in page.hrefs for s in DATA['careerSources'])
  assert 'id="armed-forces"' in raw and 'id="how-to-decide"' in raw
  assert 'Your plan' not in raw and 'next-30-days' in raw
  from career_guidance import DATA as GUIDANCE
  assert all(c['url'] in page.hrefs for c in GUIDANCE['community'])
  assert all('id="'+c['id']+'"' in raw for c in DATA['careers'])
manifest=json.loads((ROOT/'data/app-icon-sources.json').read_text())
assert {a['package'] for a in DATA['apps']}=={a['package'] for a in manifest['apps']}
assert all(a['imageSource'].startswith('https://play-lh.googleusercontent.com/') for a in manifest['apps'])
search=json.loads((ROOT/'search-index.json').read_text())
assert all(any(r['url']==route(g) for r in search) for g in GUIDES)
import runpy
runpy.run_path(str(ROOT/'scripts/check-link-policy.py'),run_name='__main__')
print('PASS Tools: three sourced guides, 4 free Play links, 6 paid anatomy entries, 12 websites, 13 career paths; all icons attributed.')

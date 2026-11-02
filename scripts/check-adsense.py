"""Verification-only release contract: no slots, requests, labels or layout changes."""
from pathlib import Path
from html.parser import HTMLParser
from copy import deepcopy
import json,re
import adsense
ROOT=Path(__file__).resolve().parent.parent
c=adsense.CONFIG
assert c['publisherId']=='ca-pub-3524774459480835'
assert not c['approved'] and not c['renderEnabled']
assert all(not p['enabled'] and p['slotId'] is None for p in c['placements'].values())
assert (ROOT/'ads.txt').read_text()==adsense.ads_txt()
class Page(HTMLParser):
 def __init__(self):super().__init__();self.head=False;self.scripts=[];self.units=[]
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t=='head':self.head=True
  if t=='script' and 'adsbygoogle.js' in a.get('src',''):self.scripts.append((self.head,a))
  if 'adsbygoogle' in a.get('class','').split() or 'data-rx-ad' in a:self.units.append(a)
 def handle_endtag(self,t):
  if t=='head':self.head=False
count=0
for p in ROOT.rglob('*.html'):
 if any(x in p.parts for x in ['node_modules','.git','docs','attachments','dist']):continue
 s=p.read_text();d=Page();d.feed(s)
 assert len(d.scripts)==1,(p,'loader duplicated or missing')
 head,a=d.scripts[0]
 assert head and 'async' in a and a.get('crossorigin')=='anonymous'
 assert a['src']=='https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client='+c['publisherId']
 assert not d.units and '/assets/adsense.js?' not in s and '/assets/adsense.css?' not in s,(p,'Ads rendered before approval')
 assert s.count('<!-- rx-ad-placement:')<=1
 count+=1
for key,p in c['placements'].items():
 for path,section in p['pages'].items():
  s=(ROOT/path.strip('/')/'index.html').read_text()
  assert s.count('<!-- rx-ad-placement:'+key+' -->')==1
  assert s.index('id="'+section+'"')<s.index('<!-- rx-ad-placement:')
assert 'rx-ad-placement' not in (ROOT/'books/dhruv-desai/index.html').read_text()
home=(ROOT/'index.html').read_text();assert home.index('id="notes"')<home.index('rx-ad-placement:home-after-bvsc')<home.index('id="objective"')
for approval,enable,autoff in [(False,False,False),(True,False,True),(False,True,True),(True,True,False),(True,True,True)]:
 test=deepcopy(c);test.update(approved=approval,renderEnabled=enable,autoAdsOffConfirmed=autoff)
 for key in test['placements']:
  test['placements'][key]['enabled']=True
  assert adsense.component(key,test)=='','Missing slot must always fail closed'
print(f'PASS AdSense: exact loader once in {count} HTML heads; no ad units, runtime, placeholders or invented slots; ads.txt and section boundaries verified.')

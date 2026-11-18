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
assert all(not p['enabled'] and re.fullmatch(r'\d{10}',p['slotId'] or '') for p in c['placements'].values())
assert (ROOT/'ads.txt').read_text()==adsense.ads_txt()
class Page(HTMLParser):
 def __init__(self):super().__init__();self.head=False;self.scripts=[];self.units=[];self.verification=[]
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t=='head':self.head=True
  if t=='meta' and a.get('name')=='google-adsense-account':self.verification.append((self.head,a.get('content')))
  if t=='script' and 'adsbygoogle.js' in a.get('src',''):self.scripts.append((self.head,a))
  if 'adsbygoogle' in a.get('class','').split() or 'data-rx-ad' in a:self.units.append(a)
 def handle_endtag(self,t):
  if t=='head':self.head=False
count=0
for p in ROOT.rglob('*.html'):
 if any(x in p.parts for x in ['node_modules','.git','docs','attachments','dist']):continue
 s=p.read_text();d=Page();d.feed(s)
 assert d.verification==[(True,c['publisherId'])],(p,'publisher verification missing or duplicated')
 assert not d.scripts,(p,'Ad runtime downloaded before approval')
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
  assert bool(adsense.component(key,test))==(approval and enable and autoff),'Approval gates must control the configured slot'
  for invalid in [None,'','123','not-a-slot']:
   missing=deepcopy(test);missing['placements'][key]['slotId']=invalid
   assert adsense.component(key,missing)=='','Missing or invalid slot must always fail closed'
print(f'PASS AdSense: publisher meta tag once in {count} HTML heads; configured slot remains inactive; no ad units, SDK requests or placeholders; ads.txt and section boundaries verified.')

# Verification remains available while the runtime follows rendering approval.
for approved in (False,True):
 for enabled in (False,True):
  config={**c,'approved':approved,'renderEnabled':enabled}
  markup=adsense.verification(config)
  assert 'google-adsense-account' in markup
  assert ('adsbygoogle.js' in markup)==(approved and enabled)
assert adsense.verification({**c,'verificationEnabled':False})==''

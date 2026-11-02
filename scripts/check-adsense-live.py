"""Inspect public verification and ads.txt; this cannot read AdSense account approval."""
import json,sys,time,urllib.request,urllib.error
from html.parser import HTMLParser
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parent.parent
CLIENT='ca-pub-3524774459480835';SELLER='google.com, pub-3524774459480835, DIRECT, f08c47fec0942fa0'
class Tags(HTMLParser):
 def __init__(self):super().__init__();self.head=False;self.loaders=[];self.units=[]
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t=='head':self.head=True
  if t=='script' and 'adsbygoogle.js' in a.get('src',''):self.loaders.append({'head':self.head,**a})
  if t=='ins' and 'adsbygoogle' in a.get('class','').split():self.units.append(a)
 def handle_endtag(self,t):
  if t=='head':self.head=False
urls=['https://thatvetguy.net/','https://thatvetguy.net/ads.txt','https://www.thatvetguy.net/ads.txt','https://thatvetguy.net/robots.txt','https://notes.thatvetguy.net/ads.txt','https://notes.thatvetguy.net/','https://notes.thatvetguy.net/objective/','https://notes.thatvetguy.net/bvsc/year-1/roadmap/','https://notes.thatvetguy.net/books/dhruv-desai/']
def fetch(url):
 for attempt in range(3):
  try:
   req=urllib.request.Request(url,headers={'User-Agent':'Mediapartners-Google'})
   with urllib.request.urlopen(req,timeout=25) as r:
    text=r.read().decode('utf-8','replace');result={'url':url,'status':r.status,'finalUrl':r.url,'contentType':r.headers.get('Content-Type','')}
    if url.endswith('.txt'):result['text']=text[:6000];result['sellerPresent']=SELLER in text.splitlines()
    else:
     p=Tags();p.feed(text);result.update(loaders=p.loaders,adUnits=len(p.units),manualAdRuntime='/assets/adsense.js?' in text)
    return result
  except urllib.error.HTTPError as e:
   if e.code<500 or attempt==2:return {'url':url,'status':e.code,'error':str(e)}
  except Exception as e:
   if attempt==2:return {'url':url,'error':str(e)}
  time.sleep(attempt+1)
report={'pages':list(ThreadPoolExecutor(4).map(fetch,urls)),'accountApproval':'Not accessible; confirm in AdSense Sites','autoAds':'Account-controlled; must remain OFF','errors':[],'parentActions':[]}
if '--audit-only' not in sys.argv:
 for p in report['pages']:
  failures=report['errors'] if p['url'].startswith('https://notes.') else report['parentActions']
  if p['url'].endswith('robots.txt'):continue
  if p.get('status')!=200:failures.append(p['url']+' not HTTP 200');continue
  if p['url'].endswith('ads.txt'):
   if not p.get('sellerPresent') or 'text/plain' not in p.get('contentType',''):failures.append(p['url']+' missing plain-text seller entry')
  else:
   ls=p.get('loaders',[])
   if len(ls)!=1 or CLIENT not in ls[0].get('src','') or not ls[0]['head']:failures.append(p['url']+' publisher loader mismatch')
   if p['url'].startswith('https://notes.') and (p['adUnits'] or p['manualAdRuntime']):failures.append(p['url']+' unexpectedly rendering ads')
p=ROOT/'docs/qa/adsense';p.mkdir(parents=True,exist_ok=True);(p/'live.json').write_text(json.dumps(report,indent=2)+'\n');print('ADSENSE_LIVE '+json.dumps(report))
if report['errors'] or ('--require-parent' in sys.argv and report['parentActions']):raise SystemExit(1)

#!/usr/bin/env python3
"""HTTP audit; report redirects, HTTP errors and unverified network failures separately."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError
from concurrent.futures import ThreadPoolExecutor
import json, argparse
ROOT=Path(__file__).resolve().parent.parent
class Links(HTMLParser):
 def __init__(self):super().__init__();self.urls=set()
 def handle_starttag(self,t,a):
  a=dict(a)
  if t=='a' and a.get('href','').startswith(('http://','https://')):self.urls.add(a['href'].split('#')[0])
class Redirects(HTTPRedirectHandler):
 def __init__(self):self.chain=[]
 def redirect_request(self,req,fp,code,msg,headers,newurl):
  self.chain.append({'status':code,'to':newurl});return super().redirect_request(req,fp,code,msg,headers,newurl)
def check(url):
 redirects=Redirects();opener=build_opener(redirects)
 try:
  with opener.open(Request(url,headers={'User-Agent':'NotesThatVetGuy-LinkAudit/1.0','Range':'bytes=0-512'}),timeout=12) as r:
   return {'url':url,'status':r.status,'finalUrl':r.url,'redirects':redirects.chain,'result':'redirect' if redirects.chain else 'ok'}
 except HTTPError as e:return {'url':url,'status':e.code,'result':'http-error','redirects':redirects.chain}
 except Exception as e:return {'url':url,'status':None,'result':'unverified','reason':str(e),'redirects':redirects.chain}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--output',default='docs/qa/links.json');ap.add_argument('--limit',type=int,default=0);args=ap.parse_args();p=Links()
 for file in ROOT.rglob('index.html'):
  if not any(part in file.parts for part in ['shared','scratch','library-files','node_modules']):p.feed(file.read_text())
 with ThreadPoolExecutor(max_workers=8) as pool:results=list(pool.map(check,sorted(p.urls)[:args.limit] if args.limit else sorted(p.urls)))
 for result in results:print('QA_LINK '+json.dumps(result))
 target=ROOT/args.output;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(results,indent=2)+'\n')
 counts={kind:sum(r['result']==kind for r in results) for kind in ['ok','redirect','http-error','unverified']};print(counts)
 raise SystemExit(1 if any(r['result']!='ok' for r in results) else 0)

"""Verify primary-storage PDF identities without publishing PDF contents."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlencode
from html.parser import HTMLParser
import json,requests,fitz
ROOT=Path(__file__).resolve().parent.parent
class Form(HTMLParser):
 def __init__(self,raw):super().__init__();self.action=None;self.values={};self.feed(raw)
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t=='form' and a.get('action','').startswith('https://drive.usercontent.google.com/'):self.action=a['action']
  if t=='input' and a.get('type')=='hidden' and a.get('name'):self.values[a['name']]=a.get('value','')
def fetch_pdf(file,path):
 session=requests.Session();url='https://drive.google.com/uc?'+urlencode({'export':'download','id':file['id']})
 for _ in range(2):
  with session.get(url,stream=True,timeout=(15,45)) as r:
   r.raise_for_status();chunks=r.iter_content(65536);first=next(chunks,b'')
   if first.lstrip().startswith(b'%PDF'):
    n=len(first)
    with path.open('wb') as f:
     f.write(first)
     for chunk in chunks:
      n+=len(chunk)
      if n>260_000_000:raise ValueError('PDF exceeds audit size limit')
      f.write(chunk)
    return n
   html=first+next(chunks,b'');form=Form(html.decode('utf-8','replace'))
   if form.action:url=form.action+'?'+urlencode(form.values)
   else:raise ValueError('Public PDF download unavailable (HTML response)')
 raise ValueError('PDF confirmation did not return a file')

def inspect(file):
 path=Path('/tmp')/('primary-'+file['id']+'.pdf')
 result={'id':file['id'],'name':file['name'],'url':file['url']}
 try:
  result['bytes']=fetch_pdf(file,path)
  with fitz.open(path) as pdf:
   result['pages']=len(pdf)
   result['openingText']='\n'.join(pdf[i].get_text()[:2200] for i in range(min(3,len(pdf))))
   result['metadata']=pdf.metadata
 except Exception as error:result['error']=str(error)[:200]
 finally:path.unlink(missing_ok=True)
 print(file['name']+': '+str(result.get('pages',result.get('error'))),flush=True)
 return result
files=json.loads((ROOT/'data/primary-drive-inventory.json').read_text())['files']
with ThreadPoolExecutor(max_workers=5) as pool:results=list(pool.map(inspect,files))
(ROOT/'data/primary-drive-verification.json').write_text(json.dumps({'reviewed':'2026-11-01','files':results},ensure_ascii=False,indent=2)+'\n')

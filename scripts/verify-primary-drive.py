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
inventory=json.loads((ROOT/'data/primary-drive-inventory.json').read_text())['files']
links=ROOT/'data/primary-drive-links.json'
if links.exists():inventory+=list(json.loads(links.read_text())['books'].values())
files={f['id']:f for f in inventory}
previous=ROOT/'data/primary-drive-verification.json'
results=json.loads(previous.read_text())['files'] if previous.exists() else []
verified={f['id'] for f in results if not f.get('error')}
pending=[f for fid,f in files.items() if fid not in verified]
with ThreadPoolExecutor(max_workers=5) as pool:new=list(pool.map(inspect,pending))
results={f['id']:f for f in results+new}
previous.write_text(json.dumps({'reviewed':'2026-11-01','files':list(results.values())},ensure_ascii=False,indent=2)+'\n')
assert not any(f.get('error') for f in new),'New primary PDF unavailable'
print('Verified primary PDFs:',len(results),'New:',len(new))

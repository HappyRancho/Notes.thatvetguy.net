"""Inspect public source PDFs first; retain candidate provenance for visual review."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse,parse_qs,urlencode
from html.parser import HTMLParser
import json,io,re,time,hashlib,base64
import requests,fitz
from PIL import Image,ImageDraw,ImageFont
from book_catalogue import books
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'assets/books/audit';OUT.mkdir(parents=True,exist_ok=True)
BOOKS=books()
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
def image_candidate(book,url,kind):
 r=requests.get(url,timeout=20);r.raise_for_status()
 with Image.open(io.BytesIO(r.content)) as im:
  im=im.convert('RGB');im.load()
  if im.width<90 or im.height<125 or im.convert('L').entropy()<1.7:raise ValueError('Not a usable cover')
  im.thumbnail((600,850));name=book['id']+'-'+kind+'.webp';dest=OUT/name;im.save(dest,'WEBP',quality=85)
  return {'path':'/assets/books/audit/'+name,'width':im.width,'height':im.height,'kind':kind,'source':url}
def audit(book):
 result={'title':book['title'],'author':book.get('author'),'existing':book.get('cover'),'pages':[],'errors':[],'online':[]}
 if book['files']:
  file=book['files'][0];temp=Path('/tmp')/('cover-audit-'+file['id']+'.pdf')
  try:
   fetch_pdf(file,temp)
   with fitz.open(temp) as doc:
    for n in range(min(4,len(doc))):
     page=doc[n];pix=page.get_pixmap(matrix=fitz.Matrix(1.1,1.1),alpha=False);im=Image.open(io.BytesIO(pix.tobytes('png'))).convert('RGB');im.thumbnail((600,850));name=book['id']+'-p'+str(n+1)+'.webp';dest=OUT/name;im.save(dest,'WEBP',quality=85)
     result['pages'].append({'path':'/assets/books/audit/'+name,'width':im.width,'height':im.height,'kind':'file-cover','page':n+1,'source':file['url'],'fileId':file['id'],'text':page.get_text()[:1200]})
  except Exception as ex:result['errors'].append(str(ex)[:200])
  finally:temp.unlink(missing_ok=True)
 if not result['pages'] and book['files']:
  try:result['online'].append(image_candidate(book,'https://drive.google.com/thumbnail?'+urlencode({'id':book['files'][0]['id'],'sz':'w800'}),'file-preview'))
  except Exception as ex:result['errors'].append('Thumbnail: '+str(ex)[:180])
 if not book.get('cover') and book.get('telegram') and '/c/' not in book['telegram']:
  try:
   from enrich_books_loader import module
   Telegram=module.Telegram
   url=book['telegram'].split('?')[0]+'?embed=1&mode=tme';html=requests.get(url,timeout=20).text
   for src in Telegram(html).images[:1]:result['online'].append(image_candidate(book,src,'telegram-preview'))
  except Exception as ex:result['errors'].append('Telegram: '+str(ex)[:180])
 if not book.get('cover'):
  try:
   params={'title':book['title'],'limit':4,'fields':'key,title,author_name,cover_i'}
   if book.get('author'):params['author']=book['author']
   docs=requests.get('https://openlibrary.org/search.json',params=params,timeout=20).json().get('docs',[])
   for d in docs:
    if d.get('cover_i'):
     item=image_candidate(book,'https://covers.openlibrary.org/b/id/'+str(d['cover_i'])+'-L.jpg?default=false','reference-cover');item.update(matchedTitle=d['title'],matchedAuthors=d.get('author_name',[]),reference='https://openlibrary.org'+d['key']);result['online'].append(item);break
  except Exception as ex:result['errors'].append('Online: '+str(ex)[:180])
 print('COVER_AUDIT_ITEM '+json.dumps({'id':book['id'],'pages':len(result['pages']),'online':len(result['online']),'errors':result['errors']}),flush=True)
 return book['id'],result
with ThreadPoolExecutor(max_workers=5) as pool:results=dict(pool.map(audit,BOOKS))
(ROOT/'data/book-cover-audit.json').write_text(json.dumps({'reviewed':time.strftime('%Y-%m-%d'),'books':results},ensure_ascii=False,indent=2)+'\n')
# Compact contact sheets: each candidate is labelled with a stable number.
items=[]
for ident,r in results.items():
 for item in r['pages']+r['online']:items.append((ident,item))
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',12)
for start in range(0,len(items),24):
 subset=items[start:start+24];sheet=Image.new('RGB',(1200,6*260),'#eaf8ff');draw=ImageDraw.Draw(sheet)
 for i,(ident,item) in enumerate(subset):
  x=(i%4)*300;y=(i//4)*260
  with Image.open(ROOT/item['path'].lstrip('/')) as im:
   im.thumbnail((280,215));sheet.paste(im,(x+(300-im.width)//2,y))
  draw.text((x+5,y+218),str(start+i)+' '+ident[:37],fill='#101b43',font=font);draw.text((x+5,y+236),('PDF p'+str(item['page'])) if 'page' in item else item['kind'],fill='#101b43',font=font)
 out=io.BytesIO();sheet.save(out,'JPEG',quality=78);print('COVER_AUDIT_SHEET '+json.dumps({'start':start,'data':base64.b64encode(out.getvalue()).decode()}),flush=True)
(ROOT/'data/book-cover-audit-index.json').write_text(json.dumps([{'id':ident,**item} for ident,item in items],indent=2)+'\n')
print('COVER_AUDIT_DONE '+json.dumps({'books':len(results),'pdfs':sum(bool(r['pages']) for r in results.values()),'candidates':len(items)}))

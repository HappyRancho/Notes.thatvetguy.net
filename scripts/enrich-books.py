#!/usr/bin/env python3
"""Fetch real book/file previews and conservatively match bibliographic metadata."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.request import Request,urlopen
from urllib.parse import urlencode,urlsplit
from html.parser import HTMLParser
from difflib import SequenceMatcher
import threading
from PIL import Image
import json,re,io,time,subprocess,shutil,html
from book_catalogue import books
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'assets/books';OUT.mkdir(parents=True,exist_ok=True)
LOCK=threading.Lock();LAST=[0]
def get(url,limit=4000000):
 host=urlsplit(url).hostname or ''
 allowed=host in ['drive.google.com','drive.googleusercontent.com','t.me','www.googleapis.com','books.google.com','books.googleusercontent.com','covers.openlibrary.org','openlibrary.org','currentbooksint.com','www.currentbooksint.com','www.wiley-vch.de','media.wiley.com','shop.elsevier.com','m.media-amazon.com','images-na.ssl-images-amazon.com'] or host.endswith('.cdn-telegram.org') or host.endswith('.googleusercontent.com')
 if not allowed:raise ValueError('Unreviewed image/metadata host')
 with urlopen(Request(url,headers={'User-Agent':'NotesThatVetGuy-BookCatalogue/1.0 (contact@thatvetguy.net)'}),timeout=18) as r:return r.read(limit)
def norm(text):return re.sub(r'[^a-z0-9]+',' ',text.lower()).strip()
class Telegram(HTMLParser):
 def __init__(self,raw):super().__init__();self.images=[];self.feed(raw)
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'tgme_widget_message_document_thumb' in a.get('class',''):
   m=re.search(r'url\([\'"]?([^\'"\)]+)',a.get('style',''))
   if m:self.images.append(html.unescape(m[1]))
def save_cover(book,url,kind):
 raw=get(url)
 with Image.open(io.BytesIO(raw)) as image:
  image.load()
  if image.width<90 or image.height<135 or not .65<image.height/image.width<2.8:raise ValueError('Not a usable book preview')
  image=image.convert('RGB');image.thumbnail((520,760));dest=OUT/(book['id']+'.webp');image.save(dest,'WEBP',quality=82,method=6)
  ocr=''
  if shutil.which('tesseract'):
   try:ocr=subprocess.run(['tesseract',str(dest),'stdout','--psm','11'],capture_output=True,text=True,timeout=12).stdout.strip()[:1800]
   except Exception:pass
  return {'path':'/assets/books/'+dest.name,'width':image.width,'height':image.height,'source':url,'kind':kind},ocr
def orient_preview(cover,ocr):
 if not cover or cover.get('oriented') or cover['kind']=='reference-cover' or not shutil.which('tesseract'):return cover,ocr
 path=ROOT/cover['path'].lstrip('/')
 try:
  result=subprocess.run(['tesseract',str(path),'stdout','--psm','0'],capture_output=True,text=True,timeout=12)
  match=re.search(r'Rotate:\s*(\d+)',result.stdout+'\n'+result.stderr)
  rotation=int(match[1]) if match else 0
  if rotation:
   with Image.open(path) as image:
    image=image.convert('RGB').rotate(-rotation,expand=True);image.thumbnail((520,760));image.save(path,'WEBP',quality=85,method=6);cover.update(width=image.width,height=image.height)
   ocr=subprocess.run(['tesseract',str(path),'stdout','--psm','11'],capture_output=True,text=True,timeout=12).stdout.strip()[:1800]
  cover['oriented']=True
 except Exception:pass
 return cover,ocr
def bibliography(book,ocr):
 title=book['title'];author=book.get('author') or ''
 with LOCK:
  time.sleep(max(0,1.05-(time.monotonic()-LAST[0])));LAST[0]=time.monotonic()
 params={'title':title,'limit':5,'fields':'key,title,author_name,cover_i,isbn,publisher,first_publish_year'}
 if author:params['author']=author
 data=json.loads(get('https://openlibrary.org/search.json?'+urlencode(params)))
 candidates=[]
 for item in data.get('docs',[]):
  v=item;name=v.get('title','');score=SequenceMatcher(None,norm(title),norm(name)).ratio();authors=v.get('author_name',[])
  author_match=any(norm(a).split()[-1] in norm(author).split() for a in authors if norm(a).split()) if author else False
  ocr_match=any(norm(a).split()[-1] in norm(ocr).split() for a in authors if norm(a).split()) if ocr else False
  if score>=.76 and (author_match or ocr_match) or score>=.97 and len(norm(title).split())>=4:
   candidates.append((score+(.2 if author_match or ocr_match else 0),item,v))
 if not candidates:return {}
 _,item,v=max(candidates,key=lambda c:c[0]);image='https://covers.openlibrary.org/b/id/'+str(v['cover_i'])+'-L.jpg?default=false' if v.get('cover_i') else None
 return {'bibliographyVerified':True,'title':v['title'],'authors':', '.join(v.get('author_name',[])) or None,'publisher':v.get('publisher',[None])[0] if v.get('publisher') else None,'referencePublishedDate':v.get('first_publish_year'),'referenceISBNs':v.get('isbn',[])[:4],'source':'https://openlibrary.org'+item['key'],'coverCandidate':image,'scope':'Bibliographic work reference; linked file edition must be checked separately'}
def enrich(book):
 existing=ROOT/'data/book-details.json';previous=json.loads(existing.read_text()).get('books',{}).get(book['id'],{}) if existing.exists() else {}
 result={};errors=[];cover=previous.get('cover');ocr=previous.get('coverOCR','')
 candidates=[('https://drive.google.com/thumbnail?'+urlencode({'id':f['id'],'sz':'w700'}),'file-preview') for f in book['files'][:1]]
 if book['telegram'] and '/c/' not in book['telegram']:
  try:
   parsed=urlsplit(book['telegram']);raw=get('https://t.me'+parsed.path+'?embed=1&mode=tme').decode('utf-8','replace')
   candidates += [(url,'telegram-preview') for url in Telegram(raw).images[:1]]
  except Exception as e:errors.append('Telegram preview: '+str(e))
 for url,kind in ([] if cover else candidates):
  try:cover,ocr=save_cover(book,url,kind);break
  except Exception as e:errors.append(kind+': '+str(e))
 cover,ocr=orient_preview(cover,ocr)
 try:result.update(bibliography(book,ocr))
 except Exception as e:errors.append('Bibliography: '+str(e))
 if not cover:
  for ref in book['references']:
   isbn=re.search(r'(?<!\d)(97[89][\d-]{10,20})(?!\d)',ref)
   if isbn:
    ident=isbn[1].replace('-','')[:13]
    try:cover,ocr=save_cover(book,'https://covers.openlibrary.org/b/isbn/'+ident+'-L.jpg?default=false','reference-cover');break
    except Exception as e:errors.append('ISBN cover: '+str(e))
   volume=re.search(r'[?&]id=([A-Za-z0-9_-]+)',ref) if 'books.google.' in ref else None
   if volume:
    try:cover,ocr=save_cover(book,'https://books.google.com/books/content?'+urlencode({'id':volume[1],'printsec':'frontcover','img':1,'zoom':2}),'reference-cover');break
    except Exception as e:errors.append('Google reference cover: '+str(e))
 if result.get('coverCandidate'):
  try:cover,ocr=save_cover(book,result['coverCandidate'],'reference-cover')
  except Exception as e:errors.append('Reference cover: '+str(e))
 result.pop('coverCandidate',None);result.update(cover=cover,coverOCR=ocr,errors=errors,reviewed=time.strftime('%Y-%m-%d'))
 print('BOOK_DETAIL '+json.dumps({'id':book['id'],'title':book['title'],**result},ensure_ascii=False),flush=True)
 return book['id'],result
def run():
 with ThreadPoolExecutor(max_workers=4) as pool:details=dict(pool.map(enrich,books()))
 report={'reviewed':time.strftime('%Y-%m-%d'),'books':details,'stats':{'works':len(details),'covers':sum(bool(v.get('cover')) for v in details.values()),'bibliography':sum(bool(v.get('bibliographyVerified')) for v in details.values())}}
 (ROOT/'data/book-details.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print('BOOK_DETAILS_COMPLETE '+json.dumps(report['stats']))
if __name__=='__main__':run()

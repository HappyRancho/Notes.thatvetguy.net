#!/usr/bin/env python3
"""Fill missing covers from checked ISBN references; never invent a book image."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,re,time
from book_catalogue import books
from enrich_books_loader import save_cover
ROOT=Path(__file__).resolve().parent.parent
old=json.loads((ROOT/'data/book-details.json').read_text())['books']
def isbn10(value):
 s=re.sub(r'[^0-9X]','',value)
 if len(s)==10:return s
 if len(s)!=13 or not s.startswith('978'):return None
 s=s[3:12];digit=(11-sum((10-i)*int(n) for i,n in enumerate(s))%11)%11
 return s+('X' if digit==10 else str(digit))
def fill(book):
 source=old.get(book['id'],{});info=dict(source);info['cover']=book.get('cover');found=info['cover']
 candidates=book.get('referenceISBNs',[])+book.get('bibliography',{}).get('referenceISBNs',[])
 for ref in book['references']:
  candidates+=re.findall(r'(?<!\d)(97[89][\d-]{10,20})(?!\d)',ref)
 tried=set()
 if not found:
  for value in candidates[:8]:
   ident=isbn10(value)
   if not ident or ident in tried:continue
   tried.add(ident)
   for host in ['https://images-na.ssl-images-amazon.com/images/P/','https://m.media-amazon.com/images/P/']:
    try:
     cover,ocr=save_cover(book,host+ident+'.01.LZZZZZZZ.jpg','reference-cover')
     if re.search(r'(?:image|cover)\s+(?:not\s+)?available|no\s+image',ocr,re.I):continue
     info['cover']=cover;found=cover;break
    except Exception:pass
   if found:break
 info['reviewed']=time.strftime('%Y-%m-%d');print('BOOK_COVER_FILL '+json.dumps({'id':book['id'],'cover':info.get('cover')},ensure_ascii=False),flush=True)
 return book['id'],info
def run():
 with ThreadPoolExecutor(max_workers=6) as pool:results=dict(pool.map(fill,books()))
 data={'reviewed':time.strftime('%Y-%m-%d'),'books':results,'stats':{'works':len(results),'covers':sum(bool(r.get('cover')) for r in results.values()),'bibliography':sum(bool(r.get('bibliographyVerified')) for r in results.values())}}
 (ROOT/'data/book-details.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');print('BOOK_COVERS_FINAL '+json.dumps(data['stats']))
if __name__=='__main__':run()

#!/usr/bin/env python3
"""Research real covers broadly; candidates require a separate visual approval."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.request import Request,urlopen
from urllib.parse import urlencode
from difflib import SequenceMatcher
from PIL import Image,ImageStat
import json,re,io,subprocess,unicodedata,hashlib,time
from book_catalogue import books
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'assets/books';OUT.mkdir(parents=True,exist_ok=True)
QUERIES={q['id']:q for q in json.loads((ROOT/'data/cover-queries.json').read_text())}
def get(url):
    with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0 (Notes.ThatVetGuy bibliographic image research)'}),timeout=10) as response:return response.read(5_000_000)
def norm(text):return re.sub(r'[^a-z0-9]+',' ',unicodedata.normalize('NFKD',text).encode('ascii','ignore').decode().lower()).strip()
def match(expected,candidate):
    a=set(norm(expected).split());b=set(norm(candidate).split());ignore={'and','of','the','a','in','for','by','edition','textbook','handbook','book'};a-=ignore;b-=ignore
    return len(a&b)/max(1,len(a))
def save(book,url,kind,ref):
    raw=get(url)
    with Image.open(io.BytesIO(raw)) as im:
        im.load();im=im.convert('RGB')
        if im.width<85 or im.height<125 or not .65<im.height/im.width<2.8:raise ValueError('not a book-shaped source image')
        if im.convert('L').entropy()<1.7:raise ValueError('blank/solid placeholder')
        im.thumbnail((520,760));path=OUT/('research-'+book['id']+'.webp');im.save(path,'WEBP',quality=84,method=6)
        ocr=subprocess.run(['tesseract',str(path),'stdout','--psm','11'],capture_output=True,text=True,timeout=10).stdout.strip()
        if re.search(r'(?:image|cover)\s+(?:not\s+)?available|no\s+(?:image|cover)',ocr,re.I):path.unlink();raise ValueError('provider placeholder')
        return dict(path='/assets/books/'+path.name,width=im.width,height=im.height,source=url,kind=kind,reference=ref,ocr=ocr[:2000],sha256=hashlib.sha256(path.read_bytes()).hexdigest())
def research(book):
    q=QUERIES[book['id']];errors=[];candidates=[]
    # Actual file previews are more reliable than guessing an edition by filename.
    for f in book['files'][:1]:
        candidates += [('https://lh3.googleusercontent.com/d/'+f['id']+'=w600','file-preview',f['url']),('https://drive.google.com/thumbnail?'+urlencode({'id':f['id'],'sz':'w600'}),'file-preview',f['url'])]
    for url,kind,ref in candidates:
        try:return book['id'],dict(cover=save(book,url,kind,ref),query=q,errors=errors)
        except Exception as error:errors.append(str(error))
    candidates=[]
    try:
        params=dict(title=q['queryTitle'],limit=6,fields='key,title,author_name,cover_i,isbn')
        if q['queryAuthor']:params['author']=q['queryAuthor']
        items=json.loads(get('https://openlibrary.org/search.json?'+urlencode(params))).get('docs',[])
        for item in items:
            if match(q['queryTitle'],item.get('title',''))<.72:continue
            if item.get('cover_i'):candidates.append(('https://covers.openlibrary.org/b/id/'+str(item['cover_i'])+'-L.jpg?default=false','reference-cover','https://openlibrary.org'+item['key']))
            for isbn in item.get('isbn',[])[:3]:candidates.append(('https://covers.openlibrary.org/b/isbn/'+isbn+'-L.jpg?default=false','reference-cover','https://openlibrary.org'+item['key']))
    except Exception as error:errors.append('Open Library: '+str(error))
    try:
        query='intitle:'+q['queryTitle']+(' inauthor:'+q['queryAuthor'] if q['queryAuthor'] else '')
        for item in json.loads(get('https://www.googleapis.com/books/v1/volumes?'+urlencode({'q':query,'maxResults':4}))).get('items',[]):
            v=item.get('volumeInfo',{})
            if match(q['queryTitle'],v.get('title',''))<.75:continue
            img=v.get('imageLinks',{}).get('thumbnail')
            if img:candidates.append((img.replace('http:','https:'),'reference-cover','https://books.google.com/books?id='+item['id']))
    except Exception as error:errors.append('Google Books: '+str(error))
    # Public archive metadata and thumbnails, not private/restricted book downloads.
    try:
        query='title:('+q['queryTitle']+') AND mediatype:texts'
        items=json.loads(get('https://archive.org/advancedsearch.php?'+urlencode({'q':query,'output':'json','rows':5,'fl[]':['identifier','title','creator']},doseq=True))).get('response',{}).get('docs',[])
        for item in items:
            if match(q['queryTitle'],item.get('title',''))>=.75:candidates.append(('https://archive.org/services/img/'+item['identifier'],'reference-cover','https://archive.org/details/'+item['identifier']))
    except Exception as error:errors.append('Archive: '+str(error))
    for isbn in book.get('referenceISBNs',[])+book.get('bibliography',{}).get('referenceISBNs',[]):
        candidates.append(('https://covers.openlibrary.org/b/isbn/'+isbn+'-L.jpg?default=false','reference-cover','ISBN '+isbn))
    for url,kind,ref in candidates[:12]:
        try:return book['id'],dict(cover=save(book,url,kind,ref),query=q,errors=errors)
        except Exception as error:errors.append(str(error))
    return book['id'],dict(cover=None,query=q,errors=errors)
def run():
    missing=[b for b in books() if b['id'] in QUERIES]
    with ThreadPoolExecutor(max_workers=5) as pool:result=dict(pool.map(research,missing))
    report=dict(reviewed=time.strftime('%Y-%m-%d'),candidates=result)
    (ROOT/'data/book-cover-candidates.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print('COVER_RESEARCH '+json.dumps({k:v['cover'] for k,v in result.items()},ensure_ascii=False))
if __name__=='__main__':run()

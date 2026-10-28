"""A canonical page per book/work, with reviewed copies kept separately."""
from pathlib import Path
from functools import lru_cache
import json,re,hashlib
from library import slug,natural,normal
ROOT=Path(__file__).resolve().parent.parent
def read(name,default):
 p=ROOT/'data'/name;return json.loads(p.read_text()) if p.exists() else default
def clean(name):
 s=re.sub(r'\.(pdf|epub|docx?|djvu|zip|rar)$','',name,flags=re.I).replace('_',' ')
 s=re.sub(r'\s*\([^)]*(?:pdfdrive|vetbooks)[^)]*\)','',s,flags=re.I)
 return re.sub(r'\s+',' ',s).strip(' ._-')
def route(ident):return '/books/'+ident+'/'
@lru_cache(maxsize=1)
def books():
 c=read('book-curation.json',{});details=read('book-details.json',{}).get('books',{});all={}
 for r in read('book-recommendations.json',{'books':[]})['books']:
  ident=slug(r['title']);author=re.sub(r'\s*\([^)]*edition[^)]*\)','',r['author']).strip()
  all[ident]={'id':ident,'title':r['title'],'author':author,'description':r['description'],'subjects':[{'year':r['year'],'name':r['subject']}],'files':[],'telegram':None,'collection':None,'recommended':True,'type':'Book','references':[r['reference']],'lastVerified':r['lastVerified']}
 for r in read('collections.json',{'resources':[]})['resources']:
  ident=r['id'];kind='Reference sheet' if ident in ['wall-drug-dose','vaccination-schedule'] else 'Question bank' if r['collection']=='question-banks' else 'Handbook' if r['collection'] in ['handbooks','drug-index'] else 'Study book'
  known=r.get('sourceCredit') if ident in ['dhruv-desai','e-nanu-qbank','veterinary-clinician-handbook','veterinary-practice-handbook'] else None
  all[ident]={'id':ident,'title':c.get('collectionTitles',{}).get(ident,clean(r['title'])),'author':known,'description':r['description'],'subjects':[],'files':[],'telegram':r['url'],'collection':r['collection'],'recommended':False,'type':kind,'references':[],'lastVerified':read('collections.json',{})['reviewed'],'resourceId':'telegram-'+ident}
 source=read('vetverse-books.json',{'files':[],'reviewed':''});seen={}
 for f in source['files']:
  if f['id'] in c.get('excludedFiles',{}):continue
  title=c.get('fileTitles',{}).get(f['id'],clean(f['name']));key=normal(title);ident=c.get('fileMerge',{}).get(f['id'])
  if not ident:
   ident=seen.get((f['subject'],key)) or slug(title)
   if ident in all and not all[ident]['files']:ident+='-vetverse'
  seen[(f['subject'],key)]=ident
  if ident not in all:all[ident]={'id':ident,'title':c.get('workTitles',{}).get(ident,title),'author':None,'description':None,'subjects':[],'files':[],'telegram':None,'collection':None,'recommended':False,'type':'Clinical guide' if 'guidelines' in title.lower() else 'Book','references':[],'lastVerified':source['reviewed']}
  book=all[ident];subject={'year':f['year'],'name':f['subject']}
  if subject not in book['subjects']:book['subjects'].append(subject)
  book['files'].append(dict(f));book['lastVerified']=source['reviewed']
  book.setdefault('resourceId','book-'+ident)
 for book in all.values():
  if book['id'] in c.get('workTitles',{}):book['title']=c['workTitles'][book['id']]
  if book['id'] in c.get('authors',{}):book['author']=c['authors'][book['id']]
  book['humanReference']=any(t in normal(book['title']) for t in ['guyton','sembulingam','medical pharmacology','goodman and gilman','pocket guide diagnostic tests'])
  book['references']+=c.get('bibliographicReferences',{}).get(book['id'],[])
  info=details.get(book['id'],{})
  if book['id'] in c.get('rejectedBibliography',{}):info={}
  alias=c.get('metadataAliases',{}).get(book['id'])
  if alias and details.get(alias,{}).get('cover'):info=details[alias]
  if book['id'] in c.get('descriptions',{}):book['description']=c['descriptions'][book['id']]
  book['referenceISBNs']=c.get('referenceISBNs',{}).get(book['id'],[])
  if not book['author'] and info.get('bibliographyVerified'):book['author']=info.get('authors')
  book['bibliography']=info if info.get('bibliographyVerified') else {}
  book['cover']=None if book['id'] in c.get('rejectedCovers',{}) else info.get('cover')
  if book['cover'] and c.get('fileCoverEvidence',{}).get(book['id']) and c['fileCoverEvidence'][book['id']] in book['cover'].get('source',''):book['cover']['kind']='file-cover'
  book['page']=route(book['id'])
  book['files'].sort(key=lambda f:(-int(m[1]) if (m:=re.search(r'\b(\d+)(?:st|nd|rd|th)?\s*[- ]?edition',f['name'],re.I)) else 0,natural(f['name'])))
  book['primaryUrl']=book['telegram'] or (book['files'][0]['url'] if book['files'] else None)
  book['access']='Telegram' if book['telegram'] else 'Google Drive' if book['files'] else 'Reading guide'
  book['downloadLabel']='Download via Telegram' if book['telegram'] else 'Open in Google Drive' if book['files'] else 'Request this book'
  if not book['description']:
   subject=book['subjects'][0]['name'];book['description']=f'{book["title"]} is listed in the {subject} Books collection for Year {book["subjects"][0]["year"]} BVSc & AH study. Use it alongside your course outline and teaching notes, and check the linked copy’s title page and edition before citing it.'
  book['clinical']=book['collection'] in ['handbooks','drug-index'] or any(s['year']==4 for s in book['subjects'])
 result=sorted(all.values(),key=lambda b:natural(b['title']))
 (ROOT/'data/books.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 return result
def by_subject(year,subject):return [b for b in books() if {'year':year,'name':subject} in b['subjects']]
def by_url(url):return next((b for b in books() if b['telegram']==url or any(f['url']==url for f in b['files'])),None)
def by_resource(ident):return next((b for b in books() if b.get('resourceId')==ident),None)

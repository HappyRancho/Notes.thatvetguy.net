"""Reviewed VetBVSc links are the sole active notes catalogue."""
from pathlib import Path
from collections import Counter
import json,re
from catalogue import KINDS,GROUPS,normal,slug,natural,clean_title
ROOT=Path(__file__).resolve().parent.parent

def build_library(refresh=False):
 source=json.loads((ROOT/'data/vetbvsc-source.json').read_text());mapping=json.loads((ROOT/'data/subject-map.json').read_text());rows=[]
 tanuvas_path=ROOT/'data/tanuvas-source.json';tanuvas=json.loads(tanuvas_path.read_text()) if tanuvas_path.exists() else {'notes':[],'reviewed':source['reviewed']}
 incoming={}
 for f in source['notes']+tanuvas['notes']:
  if f['id'] in incoming:
   current=incoming[f['id']]
   current.setdefault('alsoListedAt',[]).append({'page':f['sourcePage'],'unit':f['unit'],'year':f['year'],'subject':f['subject']})
   if f.get('collection')=='TANUVAS':current['tanuvas']=True
   continue
  incoming[f['id']]=dict(f)
 for f in incoming.values():
  # Link labels identify the resource; byte sizes and modification times are
  # deliberately unknown until the file owner exposes that metadata.
  fmt=f['format'];kind='notes';n=normal(f['title'])
  if re.search(r'\b(objectives?|mcqs?|question bank|one mark)\b',n):kind='objective'
  elif re.search(r'\b(practical|practicals|practical manual)\b',n):kind='practical'
  collections=[]
  if f.get('tanuvas') or f.get('collection')=='TANUVAS' or 'tanuvas' in (f.get('sourceCredit') or '').lower():collections.append('tanuvas')
  if kind=='objective':collections.append('objective-questions')
  if re.search(r'\b(handbook|handbooks)\b',n):collections.append('handbooks')
  title=clean_title(f['title']).replace('Products 5Technology','Products Technology').replace('BusinessManagement','Business Management');ss=slug(f['subject']);page=f'/bvsc/year-{f["year"]}/{ss}/';path=f'{f["subject"]}/{f["unit"]}/{f["name"]}'
  variant=dict(id=f['id'],name=f['name'],mime='video/mp4' if fmt=='VIDEO' else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' if fmt=='DOCX' else 'application/pdf',size=None,updated=None,url=f['url'],format=fmt,extension=fmt,download=None)
  r=dict(f,title=title,path=path,mime=variant['mime'],size=None,updated=None,subjectSlug=ss,kind=kind,group=KINDS[kind],format=fmt,mapping='Reviewed source subject and unit',duplicateIds=[],photoIds=[],variants=[variant],type='Objective' if kind=='objective' else 'Note',page=page,permalink=page+'#file-'+f['id'],source='VetBVSc',sourceCredit=f.get('sourceCredit'),lastVerified=tanuvas['reviewed'] if f.get('collection')=='TANUVAS' or f.get('tanuvas') else source['reviewed'],description=f'{title} — {f["subject"]}, {f["unit"]}.',keywords=[f['subject'],f['unit'],title]+(['TANUVAS'] if 'tanuvas' in collections else []),collections=collections,new=False)
  rows.append(r)
 rows.sort(key=lambda r:(r['year'],natural(r['subject']),natural(r['unit']),natural(r['title'])))
 years=[]
 for year,names in mapping['years'].items():
  yr=int(year);subjects=[]
  for name in names:
   own=[r for r in rows if r['year']==yr and r['subject']==name]
   subjects.append(dict(name=name,slug=slug(name),count=len(own),groups=dict(Counter(r['kind'] for r in own)),resourceIds=[r['id'] for r in own]))
  total=sum(s['count'] for s in subjects)
  years.append(dict(year=yr,subjects=subjects,count=total,extras=[],rawCount=total,fileCount=total))
 drive_rows=[r for r in rows if r['url'].startswith('https://drive.google.com/')]
 curated=json.loads((ROOT/'data/collections.json').read_text())
 from book_catalogue import books as book_registry
 book_rows=book_registry();book_by_resource={b.get('resourceId'):b for b in book_rows if b.get('resourceId')}
 for f in curated['resources']:
  clinical=f['collection'] in ['drug-index','handbooks'];rid='telegram-'+f['id'];page='/clinical/'+f['collection']+'/' if clinical else '/objective/';kind='other' if clinical else 'objective';fmt='PDF'
  page=book_by_resource[rid]['page']
  variant=dict(id=rid,name=f['title'],mime='application/pdf',size=None,updated=None,url=f['url'],format=fmt,extension=fmt,download=None)
  rows.append(dict(f,id=rid,name=f['title'],year=None,subject='Clinical References' if clinical else 'Veterinary Objective Resources',unit=('Handbooks' if f['collection']=='handbooks' else 'Drug Index Collection') if clinical else 'Objective Notes' if f['collection']=='objective-notes' else 'Question Banks',subjectSlug=None,path=f['collection']+'/'+f['title'],mime=variant['mime'],size=None,updated=None,kind=kind,group='Clinical References' if clinical else 'Objective',format=fmt,variants=[variant],duplicateIds=[],photoIds=[],type='Handbook' if clinical else 'Objective',page=page,permalink=page+'#file-'+rid,sourcePage=f['url'],lastVerified=curated['reviewed'],collections=[f['collection']],keywords=[f['title'],f['description']],new=False))
 for book in book_rows:
  if not book['files']:continue
  variants=[]
  for f in book['files']:
   fmt=f['name'].rsplit('.',1)[-1].upper();binary=f['mime']!='application/vnd.google-apps.folder';download='https://drive.google.com/uc?export=download&id='+f['id'] if isinstance(f['size'],int) and f['size']<25_000_000 and binary else None
   variants.append(dict(f,format=fmt,extension=fmt,download=download))
  f=book['files'][0];rid=book['resourceId'];page=book['page']
  rows.append(dict(id=rid,name=book['title'],title=book['title'],year=f['year'],subject=f['subject'],subjectSlug=slug(f['subject']),unit='Subject Books',path=f['path'],mime=f['mime'],size=f['size'],updated=f['updated'],kind='books',group='Books',format=variants[0]['format'],variants=variants,duplicateIds=[],photoIds=[],type='Book',page=page,permalink=page+'#file-'+rid,url=f['url'],source='Vetverse',sourceCredit=book.get('author') or 'Vetverse collection',sourcePage=f['sourceFolder'],lastVerified=book['lastVerified'],collections=['subject-books'],keywords=[book['title'],book.get('author') or '',f['subject'],'Books'],description=book['description'],new=False))
 from practical_catalogue import build_records,manifest_rows
 rows+=build_records(rows)
 drive_rows=manifest_rows(rows)
 data=dict(schemaVersion=3,lastInspected=max(source['reviewed'],curated['reviewed'],tanuvas['reviewed'],max((b['lastVerified'] for b in book_rows),default=source['reviewed'])),files=rows,years=years,stats=dict(rawFiles=len(drive_rows),canonicalResources=len(rows),curatedResources=len(curated['resources']),tanuvasResources=sum('tanuvas' in r['collections'] for r in rows),duplicatesHidden=source['stats']['duplicateLinksMerged']+len(source['notes'])+len(tanuvas['notes'])-len(incoming),imagesGrouped=sum(len(r['photoIds']) for r in rows)),unsorted=[])
 (ROOT/'data/resources.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 (ROOT/'data/catalogue.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
 (ROOT/'data/drive_manifest.json').write_text(json.dumps(drive_rows,ensure_ascii=False,indent=2)+'\n')
 (ROOT/'data/duplicates-report.json').write_text(json.dumps(dict(source='VetBVSc',duplicateLinksMerged=source['stats']['duplicateLinksMerged'],duplicates=[],formatMerges=[],photoSets=[dict(id=r['id'],subject=r['subject'],knownImages=len(r['photoIds']),url=r['url']) for r in rows if r['photoIds']],reclassified=[],extras=[]),indent=2)+'\n')
 return data

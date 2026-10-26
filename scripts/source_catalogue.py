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
  title=clean_title(f['title']);ss=slug(f['subject']);page=f'/bvsc/year-{f["year"]}/{ss}/';path=f'{f["subject"]}/{f["unit"]}/{f["name"]}'
  variant=dict(id=f['id'],name=f['name'],mime='video/mp4' if fmt=='VIDEO' else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' if fmt=='DOCX' else 'application/pdf',size=None,updated=None,url=f['url'],format=fmt,extension=fmt,download=None)
  r=dict(f,title=title,path=path,mime=variant['mime'],size=None,updated=None,subjectSlug=ss,kind=kind,group=KINDS[kind],format=fmt,mapping='Reviewed source subject and unit',duplicateIds=[],photoIds=[],variants=[variant],type='Objective' if kind=='objective' else 'Note',page=page,permalink=page+'#file-'+f['id'],source='VetBVSc',sourceCredit=f.get('sourceCredit'),lastVerified=tanuvas['reviewed'] if f.get('collection')=='TANUVAS' or f.get('tanuvas') else source['reviewed'],description=f'{title} — {f["subject"]}, {f["unit"]}.',keywords=[f['subject'],f['unit'],title],collections=collections,new=False)
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
 for f in curated['resources']:
  clinical=f['collection'] in ['drug-index','handbooks'];rid='telegram-'+f['id'];page='/clinical/'+f['collection']+'/' if clinical else '/objective/';kind='other' if clinical else 'objective';fmt='PDF'
  variant=dict(id=rid,name=f['title'],mime='application/pdf',size=None,updated=None,url=f['url'],format=fmt,extension=fmt,download=None)
  rows.append(dict(f,id=rid,name=f['title'],year=None,subject='Clinical References' if clinical else 'Veterinary Objective Resources',unit=('Handbooks' if f['collection']=='handbooks' else 'Drug Index Collection') if clinical else 'Objective Notes' if f['collection']=='objective-notes' else 'Question Banks',subjectSlug=None,path=f['collection']+'/'+f['title'],mime=variant['mime'],size=None,updated=None,kind=kind,group='Clinical References' if clinical else 'Objective',format=fmt,variants=[variant],duplicateIds=[],photoIds=[],type='Handbook' if clinical else 'Objective',page=page,permalink=page+'#file-'+rid,sourcePage=f['url'],lastVerified=curated['reviewed'],collections=[f['collection']],keywords=[f['title'],f['description']],new=False))
 data=dict(schemaVersion=3,lastInspected=max(source['reviewed'],curated['reviewed'],tanuvas['reviewed']),files=rows,years=years,stats=dict(rawFiles=len(drive_rows),canonicalResources=len(rows),curatedResources=len(curated['resources']),tanuvasResources=sum('tanuvas' in r['collections'] for r in rows),duplicatesHidden=source['stats']['duplicateLinksMerged']+len(source['notes'])+len(tanuvas['notes'])-len(incoming),imagesGrouped=0),unsorted=[])
 (ROOT/'data/resources.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 (ROOT/'data/catalogue.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
 (ROOT/'data/drive_manifest.json').write_text(json.dumps([{k:r[k] for k in ['year','path','id','name','mime','size','updated','url']} for r in drive_rows],ensure_ascii=False,indent=2)+'\n')
 (ROOT/'data/duplicates-report.json').write_text(json.dumps(dict(source='VetBVSc',duplicateLinksMerged=source['stats']['duplicateLinksMerged'],duplicates=[],formatMerges=[],photoSets=[],reclassified=[],extras=[]),indent=2)+'\n')
 return data

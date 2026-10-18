"""Reviewed VetBVSc links are the sole active notes catalogue."""
from pathlib import Path
from collections import Counter
import json,re
from catalogue import KINDS,GROUPS,normal,slug,natural,clean_title
ROOT=Path(__file__).resolve().parent.parent

def build_library(refresh=False):
 source=json.loads((ROOT/'data/vetbvsc-source.json').read_text());mapping=json.loads((ROOT/'data/subject-map.json').read_text());rows=[]
 for f in source['notes']:
  # Link labels identify the resource; byte sizes and modification times are
  # deliberately unknown until the file owner exposes that metadata.
  fmt=f['format'];kind='notes';n=normal(f['title'])
  if re.search(r'\b(objectives?|mcqs?|question bank|one mark)\b',n):kind='objective'
  elif re.search(r'\b(practical|practicals|practical manual)\b',n):kind='practical'
  collections=[]
  if kind=='objective':collections.append('objective-questions')
  if re.search(r'\b(handbook|handbooks)\b',n):collections.append('handbooks')
  title=clean_title(f['title']);ss=slug(f['subject']);page=f'/bvsc/year-{f["year"]}/{ss}/';path=f'{f["subject"]}/{f["unit"]}/{f["name"]}'
  variant=dict(id=f['id'],name=f['name'],mime='video/mp4' if fmt=='VIDEO' else 'application/pdf',size=None,updated=None,url=f['url'],format=fmt,extension=fmt,download=None)
  r=dict(f,title=title,path=path,mime=variant['mime'],size=None,updated=None,subjectSlug=ss,kind=kind,group=KINDS[kind],format=fmt,mapping='Reviewed source subject and unit',duplicateIds=[],photoIds=[],variants=[variant],type='Objective' if kind=='objective' else 'Note',page=page,permalink=page+'#file-'+f['id'],source='VetBVSc',sourceCredit=f.get('sourceCredit'),lastVerified=source['reviewed'],description=f'{title} — {f["subject"]}, {f["unit"]}.',keywords=[f['subject'],f['unit'],title],collections=collections,new=False)
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
 data=dict(schemaVersion=2,lastInspected=source['reviewed'],files=rows,years=years,stats=dict(rawFiles=len(rows),canonicalResources=len(rows),duplicatesHidden=source['stats']['duplicateLinksMerged'],imagesGrouped=0),unsorted=[])
 (ROOT/'data/resources.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 (ROOT/'data/catalogue.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
 (ROOT/'data/drive_manifest.json').write_text(json.dumps([{k:r[k] for k in ['year','path','id','name','mime','size','updated','url']} for r in rows],ensure_ascii=False,indent=2)+'\n')
 (ROOT/'data/duplicates-report.json').write_text(json.dumps(dict(source='VetBVSc',duplicateLinksMerged=source['stats']['duplicateLinksMerged'],duplicates=[],formatMerges=[],photoSets=[],reclassified=[],extras=[]),indent=2)+'\n')
 return data

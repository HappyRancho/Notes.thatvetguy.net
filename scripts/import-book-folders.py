#!/usr/bin/env python3
"""Read only Books subtrees in the four owner-provided public Drive collections."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import json,re
from public_drive import fetch,FOLDER_MIME
ROOT=Path(__file__).resolve().parent.parent
FOLDERS={1:'18FGhR7f03vR1gXpkVwkuTYOx6c-Xk1a3',2:'12WNUVTXyjCDLLqhCUfZ12eCetQhKihte',3:'1u1HaIPxbTPI7tlu6iVt6T0gh5H4oNDFS',4:'11z4OHfm9OCQvpfekbgOMQGwHj2E5hva5'}
MAPPING=json.loads((ROOT/'data/subject-map.json').read_text())
def normal(text):return re.sub(r'[^a-z0-9]+',' ',text.lower()).strip()
def book_folder(name):return bool(re.fullmatch(r'(?:\d+\s*)?(?:e\s*)?books?(?:\s+collection)?',normal(name)))
def ignored(name):return bool(re.search(r'\b(notes?|topics?|ppts?|presentations?|images?|photos?)\b',normal(name)))
def subject_for(year,path):
 text=normal(' '.join(path));scores=[]
 extra={'Veterinary Gynaecology and Obstetrics':['og'],'Veterinary and Animal Husbandry Extension Education':['animal husbandry and extension'],'Animal Genetics and Breeding':['genetics'],'Veterinary Public Health and Epidemiology':['public health epidemiology']}
 for name in MAPPING['years'][str(year)]:
  for alias in [name,*MAPPING['aliases'].get(name,[]),*extra.get(name,[])]:
   a=normal(alias)
   if a and re.search(r'(?:^| )'+re.escape(a)+r'(?: |$)',text):scores.append((len(a),name))
 return max(scores)[1] if scores else None
def crawl(pair):
 year,root=pair;queue=[(root,[],False)];seen=set();files=[];folders=[];skipped=[];errors=[]
 while queue:
  folder,path,inside=queue.pop(0)
  if folder in seen:continue
  seen.add(folder)
  if len(seen)>200 or len(path)>8:raise ValueError('Unexpected Books folder depth or count')
  try:
   entries,meta=fetch(folder)
   if inside:folders.append({'year':year,'id':folder,'path':'/'.join(path),'embeddedCount':len(entries),'ariaCounts':meta.get('ariaCounts',[]),'complete':len(entries)<50 and not any(n>len(entries) for n in meta.get('ariaCounts',[]))})
   for item in entries:
    if not isinstance(item,list) or len(item)<4:continue
    fid,name,mime=item[0],item[2],item[3]
    if mime==FOLDER_MIME:
     if ignored(name):continue
     queue.append((fid,path+[name],inside or book_folder(name)));continue
    if not inside:continue
    subject=subject_for(year,path)
    if not subject:skipped.append({'year':year,'path':'/'.join(path+[name]),'reason':'No verified subject mapping'});continue
    if not re.search(r'\.(pdf|epub|djvu|docx?|zip|rar)$',name,re.I):skipped.append({'year':year,'path':'/'.join(path+[name]),'reason':'Not a book document/archive'});continue
    size=item[13] if len(item)>13 and isinstance(item[13],int) else None
    files.append({'id':fid,'year':year,'subject':subject,'path':'/'.join(path+[name]),'name':name,'mime':mime,'size':size,'updated':None,'folderId':folder,'rootFolderId':root,'url':'https://drive.google.com/file/d/'+fid+'/view','source':'Vetverse','sourceFolder':'https://drive.google.com/drive/folders/'+folder})
  except Exception as error:errors.append({'year':year,'id':folder,'path':'/'.join(path),'reason':str(error)})
 return files,folders,skipped,errors
def run():
 files=[];folders=[];skipped=[];errors=[]
 with ThreadPoolExecutor(max_workers=4) as pool:
  for f,d,s,e in pool.map(crawl,FOLDERS.items()):files+=f;folders+=d;skipped+=s;errors+=e
 data={'reviewed':datetime.now(timezone.utc).date().isoformat(),'files':files,'folders':folders,'skipped':skipped,'errors':errors,'stats':{'files':len(files),'folders':len(folders),'byYear':{str(y):sum(r['year']==y for r in files) for y in range(1,5)}}}
 if not files or errors or any(not f['complete'] for f in folders):raise ValueError('Incomplete Books-only inspection: '+json.dumps(data,ensure_ascii=False))
 (ROOT/'data/vetverse-books.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 print('BOOKS_SOURCE '+json.dumps(data,ensure_ascii=False))
if __name__=='__main__':run()

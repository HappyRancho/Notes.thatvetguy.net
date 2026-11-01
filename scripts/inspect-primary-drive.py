"""Inventory the owner's primary public Drive tree without guessing matches."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,time
from public_drive import fetch,FOLDER_MIME
ROOT=Path(__file__).resolve().parent.parent
ROOT_ID='1CtC2aBVwE6J2ss1NJdCxOKCizaumSbiw'
pending=[(ROOT_ID,[])];seen=set();folders=[];files=[];errors=[]
def one(item):
 fid,path=item
 try:return fid,path,fetch(fid),None
 except Exception as ex:return fid,path,None,str(ex)
while pending:
 batch=pending;pending=[]
 with ThreadPoolExecutor(max_workers=4) as pool:
  for fid,path,result,error in pool.map(one,batch):
   if fid in seen:continue
   seen.add(fid)
   if error:errors.append({'id':fid,'path':'/'.join(path),'error':error});continue
   entries,meta=result
   folders.append({'id':fid,'path':'/'.join(path),'url':'https://drive.google.com/drive/folders/'+fid,**meta})
   for row in entries:
    if not isinstance(row,list) or len(row)<4:continue
    ident,name,mime=row[0],row[2],row[3]
    if mime==FOLDER_MIME:pending.append((ident,path+[name]))
    else:files.append({'id':ident,'name':name,'path':'/'.join(path+[name]),'parentId':fid,'mime':mime,'url':'https://drive.google.com/file/d/'+ident+'/view'})
   print('PRIMARY_FOLDER '+json.dumps({'id':fid,'path':'/'.join(path),'count':len(entries),'renderedCount':meta['renderedCount']}),flush=True)
 if len(seen)>500:errors.append({'error':'Folder limit reached; inventory incomplete'});break
result={'rootId':ROOT_ID,'rootUrl':'https://drive.google.com/drive/folders/'+ROOT_ID,'reviewed':time.strftime('%Y-%m-%d'),'folders':folders,'files':files,'errors':errors,'paginationReview':[f['id'] for f in folders if f['embeddedCount']>=50 or f['renderedCount']>f['embeddedCount']]}
(ROOT/'data/primary-drive-inventory.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('PRIMARY_INVENTORY '+json.dumps(result,ensure_ascii=False),flush=True)
if errors:raise SystemExit(1)

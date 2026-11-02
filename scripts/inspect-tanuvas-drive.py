"""Read the owner's public TANUVAS hierarchy without changing Drive content."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,time
from public_drive import fetch,FOLDER_MIME
ROOT=Path(__file__).resolve().parent.parent
ROOT_ID='13i3fxBDwbY8WraWKqirBugemkXDdpRyQ'
pending=[(ROOT_ID,[],None,None)];seen=set();folders=[];files=[];errors=[]
def one(item):
 for attempt in range(3):
  try:return item,fetch(item[0]),None
  except Exception as ex:
   if attempt==2:return item,None,str(ex)
   time.sleep(attempt+1)
while pending:
 batch=pending;pending=[]
 with ThreadPoolExecutor(max_workers=4) as pool:
  for item,result,error in pool.map(one,batch):
   fid,parts,parent,name=item
   if fid in seen:errors.append({'id':fid,'error':'Repeated folder ID; hierarchy requires review'});continue
   seen.add(fid)
   if error:errors.append({'id':fid,'pathParts':parts,'error':error});continue
   entries,meta=result
   folders.append({'id':fid,'name':name,'parentId':parent,'pathParts':parts,'url':'https://drive.google.com/drive/folders/'+fid,**meta})
   for order,row in enumerate(entries):
    if not isinstance(row,list) or len(row)<4:errors.append({'parentId':fid,'error':'Unrecognised row'});continue
    ident,label,mime=row[0],row[2],row[3]
    if mime==FOLDER_MIME:pending.append((ident,parts+[label],fid,label))
    else:files.append({'id':ident,'name':label,'pathParts':parts+[label],'parentId':fid,'sourceOrder':order,'mime':mime,'url':'https://drive.google.com/file/d/'+ident+'/view'})
   print('TANUVAS_FOLDER '+json.dumps({'id':fid,'pathParts':parts,'count':len(entries),'renderedCount':meta['renderedCount']}),flush=True)
 if len(seen)>500:errors.append({'error':'Folder limit reached; inventory incomplete'});break
result={'rootId':ROOT_ID,'rootUrl':'https://drive.google.com/drive/folders/'+ROOT_ID,'reviewed':time.strftime('%Y-%m-%d'),'folders':folders,'files':files,'errors':errors,'paginationReview':[f['id'] for f in folders if f['embeddedCount']>=50 or f['renderedCount']>f['embeddedCount']]}
(ROOT/'data/tanuvas-drive-inventory.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('TANUVAS_DRIVE_INVENTORY '+json.dumps(result,ensure_ascii=False),flush=True)
if errors:raise SystemExit(1)

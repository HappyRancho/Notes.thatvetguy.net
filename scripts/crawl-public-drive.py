#!/usr/bin/env python3
"""Inspect the owner's four public trees; preserve metadata and warn about possible truncation."""
from pathlib import Path
import json,datetime,concurrent.futures
from public_drive import fetch,FOLDER_MIME
ROOT=Path(__file__).resolve().parent.parent
FOLDERS={1:'18FGhR7f03vR1gXpkVwkuTYOx6c-Xk1a3',2:'12WNUVTXyjCDLLqhCUfZ12eCetQhKihte',3:'1u1HaIPxbTPI7tlu6iVt6T0gh5H4oNDFS',4:'11z4OHfm9OCQvpfekbgOMQGwHj2E5hva5'}
def crawl(pair):
 year,root=pair;pending=[(root,[])];seen=set();records=[];audit=[];errors=[];sample=False
 while pending:
  fid,path=pending.pop(0)
  if fid in seen:continue
  seen.add(fid)
  try:
   entries,details=fetch(fid);audit.append({'year':year,'id':fid,'path':'/'.join(path),**details});print('DRIVE_FOLDER '+json.dumps(audit[-1]),flush=True)
   for item in entries:
    if not isinstance(item,list) or len(item)<4:continue
    ident,name,mime=item[0],item[2],item[3]
    if mime==FOLDER_MIME:pending.append((ident,path+[name]));continue
    # Unknown fields remain null rather than guessing their positional meaning.
    record={'year':year,'path':'/'.join(path+[name]),'id':ident,'name':name,'mime':mime,'size':item[13] if len(item)>13 and isinstance(item[13],int) else None,'updated':datetime.datetime.fromtimestamp(item[10]/1000,datetime.timezone.utc).isoformat().replace('+00:00','Z') if len(item)>10 and isinstance(item[10],(int,float)) else None,'url':'https://drive.google.com/file/d/'+ident+'/view'}
    records.append(record);print('DRIVE_FILE '+json.dumps(record,ensure_ascii=False),flush=True)
    if not sample:
     print('DRIVE_SAMPLE '+json.dumps({'year':year,'name':name,'fields':{str(i):v for i,v in enumerate(item) if v is not None and (isinstance(v,(str,int,float,bool)) or i in [12,13,14,25,26])}},ensure_ascii=False),flush=True);sample=True
  except Exception as e:
   error={'year':year,'path':'/'.join(path),'id':fid,'reason':type(e).__name__+': '+str(e)};errors.append(error);print('DRIVE_ERROR '+json.dumps(error),flush=True)
 return records,audit,errors
if __name__=='__main__':
 records=[];folders=[];errors=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  for r,a,e in pool.map(crawl,FOLDERS.items()):records+=r;folders+=a;errors+=e
 out=ROOT/'docs/qa/task2-drive';out.mkdir(parents=True,exist_ok=True)
 (ROOT/'data/drive_manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
 (out/'crawl.json').write_text(json.dumps({'folders':folders,'errors':errors,'fileCount':len(records)},ensure_ascii=False,indent=2)+'\n')
 print('DRIVE_COMPLETE '+json.dumps({'files':len(records),'folders':len(folders),'errors':errors}),flush=True)

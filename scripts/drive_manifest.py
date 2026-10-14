#!/usr/bin/env python3
"""Drive API v3 importer. API keys exist only in the build process, never generated assets."""
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlencode,urlsplit
from urllib.error import HTTPError
import argparse,json,os,re,time
ROOT=Path(__file__).resolve().parent.parent
FOLDERS={1:'18FGhR7f03vR1gXpkVwkuTYOx6c-Xk1a3',2:'12WNUVTXyjCDLLqhCUfZ12eCetQhKihte',3:'1u1HaIPxbTPI7tlu6iVt6T0gh5H4oNDFS',4:'11z4OHfm9OCQvpfekbgOMQGwHj2E5hva5'}
FOLDER_MIME='application/vnd.google-apps.folder'
def list_children(folder,key,request=None):
 request=request or urlopen;token=None;seen=set()
 while True:
  params={'q':"'%s' in parents and trashed = false"%folder,'fields':'nextPageToken,incompleteSearch,files(id,name,mimeType,size,modifiedTime,webViewLink)','pageSize':1000,'supportsAllDrives':'true','includeItemsFromAllDrives':'true','orderBy':'name_natural'}
  if token:params['pageToken']=token
  req=Request('https://www.googleapis.com/drive/v3/files?'+urlencode(params),headers={'X-Goog-Api-Key':key})
  for attempt in range(4):
   try:
    with request(req,timeout=30) as response:payload=json.load(response)
    break
   except HTTPError as e:
    if e.code not in [429,500,502,503,504] or attempt==3:raise RuntimeError('Drive API returned HTTP '+str(e.code)) from None
    time.sleep(2**attempt)
  if payload.get('incompleteSearch'):raise RuntimeError('Drive returned incompleteSearch; preserve the last complete manifest')
  yield from payload.get('files',[])
  token=payload.get('nextPageToken')
  if not token:break
  if token in seen:raise RuntimeError('Drive returned a repeated page token')
  seen.add(token)
def import_api(key,request=None):
 records=[]
 for year,root in FOLDERS.items():
  queue=[(root,[])];seen=set()
  while queue:
   folder,path=queue.pop(0)
   if folder in seen:continue
   seen.add(folder)
   for f in list_children(folder,key,request):
    if f['mimeType']==FOLDER_MIME:queue.append((f['id'],path+[f['name']]));continue
    records.append({'year':year,'path':'/'.join(path+[f['name']]),'id':f['id'],'name':f['name'],'mime':f['mimeType'],'size':int(f['size']) if f.get('size') is not None else None,'updated':f.get('modifiedTime'),'url':f.get('webViewLink') or 'https://drive.google.com/file/d/'+f['id']+'/view'})
 return records
def validate(records):
 if not isinstance(records,list):raise ValueError('Manifest must be a JSON array')
 for f in records:
  for field in ['year','path','id','name','mime','size','updated','url']:
   if field not in f:raise ValueError('Missing manifest field '+field)
  if f['year'] not in FOLDERS or not re.fullmatch(r'[A-Za-z0-9_-]{10,}',f['id']):raise ValueError('Invalid year or Drive file ID')
  if f['mime']==FOLDER_MIME:raise ValueError('Folder records must not be treated as files')
  url=urlsplit(f['url'])
  if url.scheme!='https' or url.hostname not in ['drive.google.com','docs.google.com'] or f['id'] not in f['url']:raise ValueError('File URL must match a supplied Drive ID')
  if f['size'] is not None and (not isinstance(f['size'],int) or f['size']<0):raise ValueError('File size must be non-negative bytes or null')
 return records
def load_manifest(refresh=False):
 path=ROOT/'data/drive_manifest.json';key=os.getenv('DRIVE_API_KEY')
 if refresh and key:
  records=validate(import_api(key));tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n');tmp.replace(path)
 if not path.exists():raise RuntimeError('No DRIVE_API_KEY or data/drive_manifest.json. Supply the manifest or inspect the authorized public folders; no files will be invented.')
 return validate(json.loads(path.read_text()))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--refresh',action='store_true');args=ap.parse_args();records=load_manifest(refresh=args.refresh or bool(os.getenv('DRIVE_API_KEY')));print('Validated',len(records),'Drive manifest entries; API key remains build-only.')

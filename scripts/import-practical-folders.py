#!/usr/bin/env python3
"""Inspect only real Practical subtrees in the four user-provided Drive roots."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
from importlib.util import spec_from_file_location,module_from_spec
import json,re,time
from public_drive import fetch,FOLDER_MIME
ROOT=Path(__file__).resolve().parent.parent
spec=spec_from_file_location('book_source',ROOT/'scripts/import-book-folders.py');book_source=module_from_spec(spec);spec.loader.exec_module(book_source)
MAPPING=json.loads((ROOT/'data/subject-map.json').read_text())
def practical_folder(name):return bool(re.search(r'\b(practicals?|practical manuals?|practical records?|lab manuals?|laboratory manuals?)\b',book_source.normal(name)))
def subject_for(root_year,path):
    found=book_source.subject_for(root_year,path)
    if found:return root_year,found
    for year in range(1,5):
        found=book_source.subject_for(year,path)
        if found:return year,found
    return None,None
def inspect(pair):
    root_year,root=pair;queue=[(root,[],False,None)];seen=set();files=[];folders=[];unmapped=[];errors=[];tree=[]
    while queue:
        folder,path,inside,practical_root=queue.pop(0)
        if folder in seen:continue
        seen.add(folder)
        if len(seen)>500 or len(path)>10:raise ValueError('Unexpected folder depth/count')
        for attempt in range(3):
            try:entries,meta=fetch(folder);break
            except Exception as error:
                if attempt==2:errors.append(dict(year=root_year,id=folder,path='/'.join(path),reason=str(error)));entries=None
                else:time.sleep(attempt+1)
        if entries is None:continue
        tree.append(dict(year=root_year,id=folder,path='/'.join(path),count=len(entries)))
        if inside:
            year,subject=subject_for(root_year,path);complete=len(entries)<50 and not any(n>len(entries) for n in meta.get('ariaCounts',[]))
            folders.append(dict(year=year,rootYear=root_year,subject=subject,id=folder,path='/'.join(path),name=path[-1],url='https://drive.google.com/drive/folders/'+folder,complete=complete,embeddedCount=len(entries),practicalRoot=practical_root))
        for item in entries:
            if not isinstance(item,list) or len(item)<4:continue
            fid,name,mime=item[0],item[2],item[3]
            if mime==FOLDER_MIME:
                if not inside and book_source.book_folder(name):continue
                entering=inside or practical_folder(name)
                queue.append((fid,path+[name],entering,practical_root or (fid if entering else None)));continue
            if not inside:continue
            year,subject=subject_for(root_year,path)
            if not subject:unmapped.append(dict(rootYear=root_year,id=fid,name=name,path='/'.join(path)));continue
            size=item[13] if len(item)>13 and isinstance(item[13],int) else None
            files.append(dict(id=fid,name=name,mime=mime,size=size,updated=None,url='https://drive.google.com/file/d/'+fid+'/view',year=year,rootYear=root_year,subject=subject,folderId=folder,folderName=path[-1],path='/'.join(path+[name]),practicalRoot=practical_root,source='Vetverse'))
    return files,folders,unmapped,errors,tree
def run():
    files=[];folders=[];unmapped=[];errors=[];tree=[]
    with ThreadPoolExecutor(max_workers=4) as pool:
        for f,d,u,e,t in pool.map(inspect,book_source.FOLDERS.items()):files+=f;folders+=d;unmapped+=u;errors+=e;tree+=t
    unique={}
    for f in files:
        if f['id'] in unique:unique[f['id']].setdefault('alsoListedAt',[]).append(dict(year=f['year'],subject=f['subject'],path=f['path']))
        else:unique[f['id']]=f
    report=dict(reviewed=datetime.now(timezone.utc).date().isoformat(),files=list(unique.values()),folders=folders,unmapped=unmapped,errors=errors,inspectedFolders=tree,stats=dict(files=len(unique),practicalFolders=len(folders),inspectedFolders=len(tree),byYear={str(y):sum(r['year']==y for r in unique.values()) for y in range(1,5)}))
    if errors:raise ValueError('Incomplete public-folder inspection: '+json.dumps(errors))
    (ROOT/'data/vetverse-practicals.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print('PRACTICAL_SOURCE '+json.dumps(report,ensure_ascii=False))
if __name__=='__main__':run()

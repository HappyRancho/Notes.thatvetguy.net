"""Original Practical-folder documents, with images kept as complete source albums."""
from pathlib import Path
from collections import defaultdict
import json,re
from library import slug,natural
ROOT=Path(__file__).resolve().parent.parent
def vault_url(year,subject):return f'/bvsc/year-{year}/'+slug(subject)+'/practicals/'
def source_data():
    p=ROOT/'data/vetverse-practicals.json'
    return json.loads(p.read_text()) if p.exists() else {'reviewed':'2026-10-28','files':[],'folders':[]}
def title(name):
    text=re.sub(r'\.[A-Za-z0-9]{1,8}$','',name).replace('_',' ')
    text=re.sub(r'^\s*\d+[ ._-]+(?=[A-Za-z])','',text)
    return re.sub(r'\s+',' ',text).strip(' ._-')
def group_title(folder):
    label=folder['name'];n=label.lower().strip()
    return {'practicals':'Practical Files','practical lecture':'Practical Lectures','manual':'Practical Manuals','practical manual':'Practical Manuals','ppts':'Practical Slides','ppt':'Practical Slides','practical exams':'Practical Exam Material','og record':'Practical Records','works':'Worksheets'}.get(n,label)
def build_records(existing):
    source=source_data();folders={f['id']:f for f in source['folders']};existing_ids={v['id'] for r in existing for v in r['variants']};records=[];albums=defaultdict(list)
    for f in source['files']:
        if f['id'] in existing_ids:continue
        if f['mime'].startswith('image/'):albums[f['folderId']].append(f);continue
        fmt=f['name'].rsplit('.',1)[-1].upper();folder=folders[f['folderId']];group=group_title(folder);kind='presentation' if fmt in ['PPT','PPTX'] else 'practical';label=title(f['name']);rid='practical-'+f['id'];page=vault_url(f['year'],f['subject'])
        desc=('Practical slides' if kind=='presentation' else 'Editable practical document' if fmt in ['DOC','DOCX'] else 'Practical reference')+' from the '+group+' collection.'
        variant=dict(f,format=fmt,extension=fmt,download=None)
        if isinstance(f['size'],int) and f['size']<25_000_000:variant['download']='https://drive.google.com/uc?export=download&id='+f['id']
        records.append(dict(f,id=rid,title=label,kind=kind,group=group,format=fmt,variants=[variant],duplicateIds=[],photoIds=[],type='Practical',page=page,permalink=page+'#file-'+rid,sourceCredit='Source collection: Vetverse',sourcePage='https://drive.google.com/drive/folders/'+f['folderId'],lastVerified=source['reviewed'],collections=['practical-vault'],unit=group,subjectSlug=slug(f['subject']),description=desc,keywords=[label,f['subject'],group,'Practical Vault'],new=False))
    for folder_id,files in albums.items():
        f=files[0];folder=folders[folder_id];group=group_title(folder);rid='practical-photos-'+folder_id;page=vault_url(f['year'],f['subject']);label=group+' — Photo Collection'
        variant=dict(id=folder_id,name=folder['name'],mime='application/vnd.google-apps.folder',size=None,updated=None,url=folder['url'],format='IMG',extension='FOLDER',download=None)
        records.append(dict(id=rid,name=folder['name'],title=label,year=f['year'],subject=f['subject'],kind='images',group=group,format='IMG',mime=variant['mime'],size=None,updated=None,url=folder['url'],variants=[variant],duplicateIds=[],photoIds=[p['id'] for p in files],type='Practical',page=page,permalink=page+'#file-'+rid,source='Vetverse',sourceCredit='Source collection: Vetverse',sourcePage=folder['url'],lastVerified=source['reviewed'],collections=['practical-vault'],unit=group,path=folder['path'],folderId=folder_id,subjectSlug=slug(f['subject']),description='Reference images kept together in their original folder. Open the complete collection to browse every image.',keywords=[f['subject'],group,'photos','spotters','Practical Vault'],new=False,completeFolderListing=folder['complete']))
    return sorted(records,key=lambda r:(r['year'],natural(r['subject']),natural(r['group']),natural(r['title'])))
def manifest_rows(records):
    source={f['id']:f for f in source_data()['files']};rows=[]
    for r in records:
        if r['photoIds']:
            rows.extend({k:source[fid].get(k) for k in ['year','path','id','name','mime','size','updated','url']} for fid in r['photoIds'])
        else:
            rows.extend(dict(year=v.get('year',r['year']),path=v.get('path',r['path']),id=v['id'],name=v['name'],mime=v['mime'],size=v['size'],updated=v['updated'],url=v['url']) for v in r['variants'] if v['url'].startswith('https://drive.google.com/'))
    return rows

"""Provenance-preserving catalogue; public folders are inspected separately."""
from pathlib import Path
from difflib import SequenceMatcher
from collections import Counter, defaultdict
from datetime import datetime, timezone
import json, re, unicodedata
from drive_manifest import load_manifest
ROOT=Path(__file__).resolve().parent.parent
KINDS={'notes':'Notes','books':'Books','practical':'Practical','objective':'Objective','presentation':'Slides','images':'Photo sets','other':'Extras'}
GROUPS=list(KINDS.values())
CAMERA=re.compile(r'^(?:IMG[-_]|PXL_|DSC[_-]|Screenshot)',re.I)
EXT=re.compile(r'\.(pdf|docx?|pptx?|xlsx?|jpe?g|png|gif|webp|bmp|txt|zip|rar|mp4|mkv|avi|mp3|epub|rtf)$',re.I)
def normal(s):return re.sub(r'[^a-z0-9]+',' ',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()).strip()
def slug(s):return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')
def natural(s):return [int(p) if p.isdigit() else p.lower() for p in re.split(r'(\d+)',s)]
def clean_title(name):
    title=EXT.sub('',name).replace('_',' ')
    title=re.sub(r'^\s*(?:\d+[.)\-]\s*|\d+\s+-\s*)','',title)
    title=re.sub(r'\s*(?:\(\d+\)|[-–]\s*final|\bcopy(?: of)?\b)\s*',' ',title,flags=re.I)
    title=re.sub('antihyperetensive','antihypertensive',title,flags=re.I)
    title=re.sub(r'vasodilators(?=antihypertensive)','Vasodilators ',title,flags=re.I)
    return re.sub(r'\s+',' ',title).strip(' -') or EXT.sub('',name)
def subject_for(f,m):
    override=m['fileOverrides'].get(f['id'],{})
    if override.get('subject'):return override['subject'],'manual file override'
    path=normal(f['path']);candidates=m['years'][str(f['year'])]
    for prefix,subject in m['pathOverrides'].items():
        if path.startswith(normal(prefix)) and subject in candidates:return subject,'manual path override'
    parts=[normal(p) for p in f['path'].split('/')[:-1]]
    for part in parts:
        matches=[(len(normal(a)),s) for s in candidates for a in [s]+m['aliases'].get(s,[]) if normal(a)==part]
        if matches:return max(matches)[1],'folder alias'
    matches=[(len(normal(a)),s) for s in candidates for a in [s]+m['aliases'].get(s,[]) if len(normal(a))>=3 and re.search(r'\b'+re.escape(normal(a))+r'\b',path)]
    if matches:return max(matches)[1],'name alias'
    fuzzy=sorted([(SequenceMatcher(None,p,normal(a)).ratio(),s) for p in parts for s in candidates for a in [s]+m['aliases'].get(s,[])],reverse=True)
    if fuzzy and fuzzy[0][0]>=.88 and (len(fuzzy)<2 or fuzzy[0][1]==fuzzy[1][1] or fuzzy[0][0]-fuzzy[1][0]>=.08):return fuzzy[0][1],'fuzzy folder match'
    return None,'needs subject review'
def format_for(f):
    ext=f['name'].rsplit('.',1)[-1].lower();mime=f['mime']
    if ext=='pdf' or mime=='application/pdf':return 'PDF'
    if ext in ['doc','docx','rtf'] or 'word' in mime:return 'DOC'
    if ext in ['ppt','pptx'] or 'presentation' in mime:return 'PPT'
    if ext in ['xls','xlsx','csv'] or 'spreadsheet' in mime:return 'XLS'
    if mime.startswith('image/'):return 'IMG'
    return 'FILE'
def classify(f,c):
    move=c['move'].get(f['id'],{})
    if move.get('kind'):return move['kind']
    path=normal(f['path']);parent=normal('/'.join(f['path'].split('/')[:-1]))
    if f['id'] in c['collections']['objective-questions']['include']:return 'objective'
    if re.search(r'\b(practical|practicals|record|spotters|manuals?)\b',parent):return 'practical'
    if re.search(r'\b(books?|textbooks?)\b',parent):return 'books'
    if format_for(f)=='PPT':return 'presentation'
    if re.search(r'\b(objectives?|mcqs?|question papers?|board questions|one mark)\b',path):return 'objective'
    if f['mime'].startswith('image/'):return 'images'
    if re.search(r'\b(notes?|ppt|pdf|unit|lecture|lectures)\b',parent):return 'notes'
    return 'other'
def build_library(refresh=False):
    manifest=load_manifest(refresh=refresh);m=json.loads((ROOT/'data/subject-map.json').read_text());c=json.loads((ROOT/'data/curation.json').read_text())
    folders={(f['year'],f['path']):f['id'] for f in json.loads((ROOT/'data/drive-folders.json').read_text())}
    duplicates=[];merges=[];photos=defaultdict(list);records=[];seen={};seenids=set();reclassified=[]
    for f in sorted(manifest,key=lambda f:(f['year'],natural(f['path']))):
        if f['id'] in seenids:continue
        seenids.add(f['id'])
        if CAMERA.match(f['name']) and f['mime'].startswith('image/'):
            photos[(f['year'],f['path'].rsplit('/',1)[0])].append(f);continue
        title=clean_title(f['name']);subject,method=subject_for(f,m);move=c['move'].get(f['id'],{});subject=move.get('subject',subject);kind=classify(f,c)
        key=(normal(title),f['size']) if f['size'] is not None else (f['id'],None)
        if key in seen:
            kept=seen[key];kept['duplicateIds'].append(f['id']);duplicates.append({'hidden':f['id'],'kept':kept['id'],'name':f['name'],'path':f['path'],'year':f['year'],'reason':'same normalised title and byte size'});continue
        row=dict(f,title=title,subject=subject,subjectSlug=slug(subject) if subject else None,kind=kind,group=KINDS[kind],format=format_for(f),mapping=method,duplicateIds=[],photoIds=[],variants=[])
        records.append(row);seen[key]=row
        if move:reclassified.append({'id':f['id'],'title':title,**move})
    merged=[];bytitle={}
    for r in records:
        key=(r['year'],r['subject'],normal(r['title']));prior=bytitle.get(key)
        if prior and r['format'] not in {v['format'] for v in prior['variants']}:
            prior['variants'].append({k:r[k] for k in ['id','name','mime','size','updated','url','format']});prior['duplicateIds']+=r['duplicateIds'];merges.append({'id':r['id'],'into':prior['id'],'format':r['format']})
        else:
            r['variants']=[{k:r[k] for k in ['id','name','mime','size','updated','url','format']}];merged.append(r);bytitle.setdefault(key,r)
    photo_report=[]
    for (year,path),files in photos.items():
        subject,method=subject_for(files[0],m);folder=folders.get((year,path))
        if not folder:raise ValueError('Missing photo-folder provenance: '+path)
        title='Photo set — '+(subject or 'Year '+str(year)+' revision')+' — '+str(len(files))+' images'
        r=dict(year=year,path=path,id='photos-'+folder,name=title,title=title,mime='image/*',size=sum(f['size'] or 0 for f in files),updated=max(f['updated'] or '' for f in files),url='https://drive.google.com/drive/folders/'+folder,subject=subject,subjectSlug=slug(subject) if subject else None,kind='images',group=KINDS['images'],format='IMG',mapping=method,photoIds=[f['id'] for f in files],duplicateIds=[],variants=[])
        r['variants']=[{k:r[k] for k in ['id','name','mime','size','updated','url','format']}];merged.append(r)
        photo_report.append({'year':year,'subject':subject,'folder':path,'url':r['url'],'count':len(files)})
    for r in merged:
        r['type']={'notes':'Note','books':'Book','practical':'Practical','objective':'Objective','presentation':'Slides','images':'Photo set','other':'Resource'}[r['kind']]
        r['page']='/bvsc/year-'+str(r['year'])+'/'+(r['subjectSlug']+'/' if r['subjectSlug'] else '')
        r['permalink']=r['page']+'#file-'+r['id'];r['source']='Google Drive';r['sourceCredit']=m['fileOverrides'].get(r['id'],{}).get('sourceCredit')
        r['lastVerified']=m['lastInspected'];r['description']=r['group']+' · '+(r['subject'] or 'Year '+str(r['year'])+' extras');r['keywords']=r['path']
        for v in r['variants']:v['download']='https://drive.google.com/uc?export=download&id='+v['id'] if not r['photoIds'] and isinstance(v['size'],int) and v['size']<25_000_000 and not v['mime'].startswith('application/vnd.google-apps.') else None
        r['download']=r['variants'][0]['download'];allids={v['id'] for v in r['variants']}|set(r['duplicateIds'])
        r['collections']=[name for name,col in c['collections'].items() if allids&set(col['include']) and not allids&set(col['exclude'])]
        r['new']=bool(r['updated'] and 0 <= (datetime.now(timezone.utc)-datetime.fromisoformat(r['updated'].replace('Z','+00:00'))).days <=30)
    merged.sort(key=lambda r:(r['year'],natural(r['subject'] or 'zz'),natural(r['title'])))
    years=[]
    for y,names in m['years'].items():
        rows=[r for r in merged if r['year']==int(y)];subjects=[]
        for name in names:
            own=[r for r in rows if r['subject']==name];subjects.append({'name':name,'slug':slug(name),'count':len(own),'groups':dict(Counter(r['kind'] for r in own)),'resourceIds':[r['id'] for r in own]})
        years.append({'year':int(y),'subjects':subjects,'count':len(rows),'extras':[r['id'] for r in rows if not r['subject']],'rawCount':sum(f['year']==int(y) for f in manifest),'fileCount':sum(len(r['photoIds']) if r['photoIds'] else len(r['variants']) for r in rows)})
    report={'rawFiles':len(manifest),'visibleRows':len(merged),'duplicatesHidden':len(duplicates),'duplicates':duplicates,'formatsMerged':merges,'imagesGrouped':sum(p['count'] for p in photo_report),'photoSets':photo_report,'reclassified':reclassified,'extras':[{'id':r['id'],'year':r['year'],'title':r['title'],'path':r['path']} for r in merged if not r['subject']]}
    result={'schemaVersion':3,'lastInspected':m['lastInspected'],'files':merged,'years':years,'stats':{k:report[k] for k in ['rawFiles','visibleRows','duplicatesHidden','imagesGrouped']},'unsorted':[]}
    for filename,value in [('resources.json',result),('catalogue.json',merged),('duplicates-report.json',report)]:(ROOT/'data'/filename).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    return result
if __name__=='__main__':print(json.dumps(build_library()['stats']))

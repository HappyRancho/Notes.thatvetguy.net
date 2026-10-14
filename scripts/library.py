"""One canonical library, derived solely from verified Drive file records."""
from pathlib import Path
from difflib import SequenceMatcher
from collections import Counter
import json,re,unicodedata,os
from drive_manifest import load_manifest
ROOT=Path(__file__).resolve().parent.parent
GROUPS=['Notes','Books','Practical manuals','Other']
def normal(s):return re.sub(r'[^a-z0-9]+',' ',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()).strip()
def slug(s):return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')
def natural(s):return [int(p) if p.isdigit() else p.lower() for p in re.split(r'(\d+)',s)]
def clean_title(name):
 title=re.sub(r'\.(pdf|docx?|pptx?|xlsx?|jpe?g|png|gif|webp|bmp|txt|zip|rar|mp4|mkv|avi|mp3|epub)$','',name,flags=re.I)
 return re.sub(r'\s+',' ',title.replace('_',' ')).strip() or name

def subject_for(f,mapping):
 override=mapping['fileOverrides'].get(f['id'],{})
 if override.get('subject'):return override['subject'],'manual file override'
 path=normal(f['path']);year=str(f['year']);candidates=mapping['years'][year]
 for prefix,subject in mapping['pathOverrides'].items():
  if path.startswith(normal(prefix)):return subject,'manual path override'
 # Prefer exact parent-folder matches over filename hints; do not map generic media filenames.
 parts=[normal(p) for p in f['path'].split('/')[:-1]]
 for part in parts:
  matches=[(len(normal(alias)),subject) for subject in candidates for alias in [subject]+mapping['aliases'].get(subject,[]) if normal(alias)==part]
  if matches:return max(matches)[1],'folder alias'
 matches=[(len(normal(alias)),subject) for subject in candidates for alias in [subject]+mapping['aliases'].get(subject,[]) if len(normal(alias))>=3 and re.search(r'\b'+re.escape(normal(alias))+r'\b',path)]
 if matches:return max(matches)[1],'name alias'
 fuzzy=sorted([(SequenceMatcher(None,part,normal(alias)).ratio(),subject) for part in parts for subject in candidates for alias in [subject]+mapping['aliases'].get(subject,[])],reverse=True)
 if fuzzy and fuzzy[0][0]>=.88 and (len(fuzzy)<2 or fuzzy[0][1]==fuzzy[1][1] or fuzzy[0][0]-fuzzy[1][0]>=.08):return fuzzy[0][1],'fuzzy folder match'
 return 'Unsorted','unmatched'
def file_group(f,mapping):
 manual=mapping['fileOverrides'].get(f['id'],{}).get('group')
 if manual:return manual
 parent=normal('/'.join(f['path'].split('/')[:-1]))
 for group,aliases in mapping['groups'].items():
  if any(re.search(r'\b'+re.escape(normal(a))+r'\b',parent) for a in aliases):return group
 return 'Other'
def format_for(f):
 ext=f['name'].rsplit('.',1)[-1].lower();mime=f['mime']
 if ext=='pdf' or mime=='application/pdf':return 'PDF'
 if ext in ['doc','docx'] or 'wordprocessing' in mime or mime.endswith('.document'):return 'DOC'
 if ext in ['ppt','pptx'] or 'presentation' in mime:return 'PPT'
 if ext in ['xls','xlsx','csv'] or 'spreadsheet' in mime:return 'XLS'
 if mime.startswith('image/'):return 'IMG'
 return 'FILE'
def build_library(refresh=False):
 manifest=load_manifest(refresh=refresh);mapping=json.loads((ROOT/'data/subject-map.json').read_text());records=[];seen={};duplicates=[]
 for f in sorted(manifest,key=lambda f:(f['year'],natural(f['path']))):
  if f['id'] in seen:duplicates.append({'id':f['id'],'kept':seen[f['id']],'also':f['path']});continue
  seen[f['id']]=f['path'];subject,method=subject_for(f,mapping);group=file_group(f,mapping);override=mapping['fileOverrides'].get(f['id'],{})
  resource=dict(f,title=clean_title(f['name']),subject=subject,subjectSlug=slug(subject),group=group,format=format_for(f),type={'Notes':'Note','Books':'Book','Practical manuals':'Practical manual','Other':format_for(f)}[group],source='Google Drive',sourceCredit=override.get('sourceCredit') or f.get('sourceCredit'),mapping=method,lastVerified=mapping['lastInspected'],description=group+' · '+subject)
  resource['page']='/bvsc/year-'+str(f['year'])+'/'+slug(subject)+'/'
  resource['permalink']=resource['page']+'#file-'+f['id'];resource['download']='https://drive.google.com/uc?export=download&id='+f['id'] if isinstance(f['size'],int) and f['size']<25_000_000 and not f['mime'].startswith('application/vnd.google-apps.') else None
  resource['keywords']=f['path'];records.append(resource)
 years=[]
 for y,names in mapping['years'].items():
  counts=Counter(r['subject'] for r in records if r['year']==int(y));subjects=[{'name':name,'slug':slug(name),'count':counts[name],'resourceIds':[r['id'] for r in records if r['year']==int(y) and r['subject']==name]} for name in names]
  if counts['Unsorted']:subjects.append({'name':'Unsorted','slug':'unsorted','count':counts['Unsorted'],'resourceIds':[r['id'] for r in records if r['year']==int(y) and r['subject']=='Unsorted']})
  years.append({'year':int(y),'subjects':subjects,'count':sum(counts.values())})
 result={'schemaVersion':2,'lastInspected':mapping['lastInspected'],'source':'Owner-supplied public Google Drive folders','files':records,'years':years,'unsorted':[{'id':r['id'],'year':r['year'],'path':r['path']} for r in records if r['subject']=='Unsorted'],'duplicateObservations':duplicates}
 (ROOT/'data/resources.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 (ROOT/'data/catalogue.json').write_text(json.dumps(records,ensure_ascii=False,separators=(',',':'))+'\n')
 return result

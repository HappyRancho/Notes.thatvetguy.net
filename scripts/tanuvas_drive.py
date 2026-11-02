"""Build TANUVAS records from the owner's reviewed Drive folder hierarchy."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parent.parent
YEAR_NAMES={'FIRST PROFESSIONAL YEAR':1,'SECOND PROFESSIONAL YEAR':2,'THIRD PROFESSIONAL YEAR':3,'FOURTH PROFESSIONAL YEAR':4}
SUBJECT_NAMES={
 'LIVESTOCK PRODUCTION MANAGEMENT':'Livestock Production Management',
 'VETERINARY ANATOMY':'Veterinary Anatomy','VETERINARY PHYSIOLOGY':'Veterinary Physiology',
 'ANIMAL GENETICS & BREEDING':'Animal Genetics and Breeding','ANIMAL NUTRITION':'Animal Nutrition',
 'VETERINARY BIOCHEMISTRY':'Veterinary Biochemistry','VETERINARY MICROBIOLOGY':'Veterinary Microbiology','VETERINARY PATHOLOGY':'Veterinary Pathology',
 'LIVESTOCK PRODUCTS TECHNOLOGY':'Livestock Products Technology',
 'VETERINARY & ANIMAL HUSBANDRY EXTENSION AND EDUCATION':'Veterinary and Animal Husbandry Extension Education',
 'VETERINARY PARASITOLOGY':'Veterinary Parasitology','VETERINARY PHARMACOLOGY & TOXICOLOGY':'Veterinary Pharmacology and Toxicology',
 'VETERINARY PUBLIC HEALTH & EPIDEMIOLOGY':'Veterinary Public Health and Epidemiology',
 'VETERINARY GYNAECOLOGY':'Veterinary Gynaecology and Obstetrics','VETERINARY MEDICINE':'Veterinary Medicine','VETERINARY SURGERY AND RADIOLOGY':'Veterinary Surgery and Radiology'}
def display_name(name):
    # Preserve spelling, case, punctuation, internal numbers and file extensions.
    return re.sub(r'^\s*\d+(?:[.)_\-–—]\s*|\s+)', '', name, count=1)
def build(inventory,previous,topic_source):
    assert not inventory['errors'] and not inventory['paginationReview'],'Incomplete Drive inventory'
    mapping=json.loads((ROOT/'data/subject-map.json').read_text())['years']
    folders={f['id']:f for f in inventory['folders']};subjects=[];notes=[]
    for folder in inventory['folders']:
        parts=folder['pathParts']
        assert len(parts)<=2,('Unexpected folder depth',parts)
        if len(parts)!=2:continue
        year=YEAR_NAMES[display_name(parts[0])];subject=SUBJECT_NAMES[display_name(parts[1])]
        assert subject in mapping[str(year)],('Year/subject mismatch',parts)
        subjects.append(dict(id=folder['id'],year=year,subject=subject,name=display_name(folder['name']),originalName=folder['name'],yearName=display_name(parts[0]),url=folder['url']))
    by_folder={s['id']:s for s in subjects}
    for f in inventory['files']:
        assert len(f['pathParts'])==3 and f['mime']=='application/pdf',('Unexpected file',f)
        s=by_folder[f['parentId']];title=display_name(f['name'])
        notes.append(dict(id=f['id'],year=s['year'],subject=s['subject'],subjectLabel=s['name'],yearLabel=s['yearName'],unit=title,name=title,title=title,originalSourceTitle=f['name'],driveName=f['name'],url=f['url'],sourcePage=s['url'],sourceIndex=inventory['rootUrl'],sourceLabel='ThatVetGuy TANUVAS Drive',sourceCredit='TANUVAS',collection='TANUVAS',format='PDF',mime=f['mime'],folderId=f['parentId'],sourceOrder=f['sourceOrder'],drivePath=f['pathParts'],preserveSourceName=True,verification={'status':'public-folder-listed','reason':'Name, PDF type and parent folder read from the public Drive listing; PDF text not re-audited'},alsoListedAt=[]))
    assert len({r['id'] for r in notes})==len(notes)==len(inventory['files']),'Repeated or omitted file'
    old_topics=[r for r in topic_source['notes'] if r.get('collection')=='TANUVAS' or r.get('sourceCredit')=='TANUVAS' or r.get('tanuvas')]
    new_ids={n['id'] for n in notes}
    legacy=previous.get('legacyAnchors',[])+[{k:r[k] for k in ['id','year','subject','unit']} for r in previous['notes']+old_topics if r['id'] not in new_ids]
    legacy=list({(r['id'],r['year'],r['subject'],r['unit']):r for r in legacy}.values())
    return dict(schemaVersion=2,reviewed=inventory['reviewed'],sourceType='owner-organized-drive',rootId=inventory['rootId'],rootUrl=inventory['rootUrl'],subjectFolders=subjects,notes=notes,legacyAnchors=legacy,supersededTopicIds=[r['id'] for r in old_topics],unavailable=[],stats={'resources':len(notes),'subjects':len(subjects),'byYear':{str(y):sum(r['year']==y for r in notes) for y in range(1,5)},'duplicatesMerged':0,'unavailable':0})
def legacy_hashes(year,subject):
    from catalogue import slug
    data=json.loads((ROOT/'data/tanuvas-source.json').read_text());ids=set()
    for row in data.get('legacyAnchors',[]):
        if row['year']==year and row['subject']==subject:
            ids.update(['file-'+row['id'],slug(subject)+'-tanuvas-'+slug(row['unit'])])
    return sorted(ids)
if __name__=='__main__':
    p=ROOT/'data/tanuvas-source.json'
    data=build(json.loads((ROOT/'data/tanuvas-drive-inventory.json').read_text()),json.loads(p.read_text()),json.loads((ROOT/'data/vetbvsc-source.json').read_text()))
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(data['stats']))

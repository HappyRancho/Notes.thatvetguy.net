#!/usr/bin/env python3
"""Folder-only public Vaults; original documents remain auditable and hash-compatible."""
from pathlib import Path
from collections import Counter
import json,re
ROOT=Path(__file__).resolve().parent.parent
source=json.loads((ROOT/'data/vetverse-practicals.json').read_text());data=json.loads((ROOT/'data/resources.json').read_text());rows=[r for r in data['files'] if 'practical-vault' in r['collections']];folders=[r for r in data['files'] if 'practical-folders' in r['collections']];search=json.loads((ROOT/'search-index.json').read_text());search_ids={s['id'] for s in search}
original={f['id']:f for f in source['files']};accounted=Counter(fid for r in rows for fid in (r['photoIds'] or [v['id'] for v in r['variants']]))
assert set(accounted)==set(original) and set(accounted.values())=={1},'Lost or duplicated source file'
assert not source['unmapped'] and not source['errors']
assert {r['folderId'] for r in folders}=={f['id'] for f in source['folders']}
assert all(r.get('public') is False and r['id'] not in search_ids for r in rows),'Individual practical files exposed'
assert Counter(fid for r in folders for fid in r['memberIds'])==Counter(original.keys()),'Folder membership mismatch'
for r in folders:
 f=next(f for f in source['folders'] if f['id']==r['folderId']);assert r['url']==f['url'] and r['id'] in search_ids
 raw=(ROOT/r['page'].strip('/')/'index.html').read_text();assert raw.count('data-resource-id="'+r['id']+'"')==1
 for alias in r['searchFileIds']:
  if alias!=r['folderId']:assert 'id="file-'+alias+'"' in raw,'Old saved hash lost'
for page in {r['page'] for r in folders}:
 raw=(ROOT/page.strip('/')/'index.html').read_text();graph=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',raw,re.S)[1])['@graph'];ids=[x['@id'] for x in graph if '@id' in x];assert len(ids)==len(set(ids)),'Duplicate structured resource entity'
 listing=next(x for x in graph if x.get('@type')=='ItemList');assert listing['numberOfItems']==sum(r['page']==page for r in folders)
for y in data['years']:
 for s in y['subjects']:
  path=f'/bvsc/year-{y["year"]}/{s["slug"]}/practicals/';html=(ROOT/path.strip('/')/'index.html').read_text();own=[r for r in folders if r['page']==path]
  assert set(re.findall(r'data-resource-id="([^"]+)"',html))=={r['id'] for r in own}
  assert 'practical-checklist-link' in html and 'Assessment at a glance' in html and 'file-row' not in html
  if not own:assert 'No practical folder is available' in html
report=dict(publicFolders=len(folders),sourceFiles=len(original),individualFilesPublished=0,bySubject={s:sum(r['subject']==s for r in folders) for s in sorted({r['subject'] for r in folders})})
out=ROOT/'docs/qa/subject-hubs';out.mkdir(parents=True,exist_ok=True);(out/'practical-data.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS PRACTICALS '+json.dumps(report))

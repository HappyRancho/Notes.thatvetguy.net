#!/usr/bin/env python3
"""Every Practical document and image stays accounted for exactly once."""
from pathlib import Path
from collections import Counter
import json,re
ROOT=Path(__file__).resolve().parent.parent
source=json.loads((ROOT/'data/vetverse-practicals.json').read_text());data=json.loads((ROOT/'data/resources.json').read_text());rows=[r for r in data['files'] if 'practical-vault' in r['collections']];search=json.loads((ROOT/'search-index.json').read_text())
original={f['id']:f for f in source['files']};accounted=Counter(fid for r in rows for fid in (r['photoIds'] or [v['id'] for v in r['variants']]))
assert set(accounted)==set(original) and set(accounted.values())=={1},'Lost or duplicated practical material'
assert all(re.search(r'\bpracticals?\b',f['path'],re.I) for f in source['files']),'File imported from outside a Practical folder'
assert not source['unmapped'] and not source['errors']
for r in rows:
 assert r['id'] in {s['id'] for s in search} and r['url'].startswith('https://drive.google.com/')
 raw=(ROOT/r['page'].strip('/')/'index.html').read_text();assert raw.count('data-resource-id="'+r['id']+'"')==1
 if r['photoIds']:
  assert all(original[fid]['mime'].startswith('image/') for fid in r['photoIds'])
  assert r['url']=='https://drive.google.com/drive/folders/'+r['folderId']
  assert 'IMG-' not in r['title'] and 'IMG_' not in r['title']
 else:
  f=original[r['variants'][0]['id']];assert r['url']==f['url'] and r['size']==f['size']
  assert r['name']==f['name'] and r['subject']==f['subject'] and r['year']==f['year']
for folder in source['folders']:
 if not folder['complete']:assert any(r['url']==folder['url'] and r['photoIds'] for r in rows),'A capped preview must retain the complete photo folder link'
for y in data['years']:
 for s in y['subjects']:
  path=f'/bvsc/year-{y["year"]}/{s["slug"]}/practicals/';html=(ROOT/path.strip('/')/'index.html').read_text();own=[r for r in rows if r['page']==path]
  assert set(re.findall(r'data-resource-id="([^"]+)"',html))=={r['id'] for r in own}
  assert 'practical-checklist-link' in html
  if not own:assert 'Practical material coming soon' in html
out=ROOT/'docs/qa/subject-hubs';out.mkdir(parents=True,exist_ok=True)
report=dict(documents=sum(not r['photoIds'] for r in rows),photoCollections=sum(bool(r['photoIds']) for r in rows),observedImages=sum(len(r['photoIds']) for r in rows),sourceFiles=len(original),folders=len(source['folders']),bySubject={s:sum(r['subject']==s for r in rows) for s in sorted({r['subject'] for r in rows})},limitedPhotoPreviews=[f['path'] for f in source['folders'] if not f['complete']])
(out/'practical-data.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS PRACTICALS '+json.dumps(report))

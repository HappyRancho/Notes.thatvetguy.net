#!/usr/bin/env python3
"""Canonical subject readers, source provenance and backwards-compatible notes."""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
data=json.loads((ROOT/'data/resources.json').read_text())
rows={r['id']:r for r in data['files']}
routes=[]
for year in data['years']:
 n=year['year'];base=f'/bvsc/year-{n}/';raw=(ROOT/base.strip('/')/'index.html').read_text()
 assert 'year-subject-roadmap' not in raw and 'year-roadmap-details' not in raw
 assert raw.count('class="academic-subject-card"')==len(year['subjects'])
 for other in range(1,5):assert f'href="/bvsc/year-{other}/"' in raw
 assert base+'roadmap/' in raw and f'id="road-map"' in raw
 legacy=(ROOT/base.strip('/')/'notes/index.html').read_text()
 assert 'noindex,follow' in legacy and 'data-resource-id=' not in legacy
 for subject in year['subjects']:
  path=base+subject['slug']+'/';routes.append(path)
  html=(ROOT/path.strip('/')/'index.html').read_text()
  assert f'href="{path}"' in raw
  assert 'id="notes"' in html and 'id="tanuvas"' in html and 'id="books"' in html
  assert set(re.findall('data-resource-id="([^"]+)"',html))==set(subject['resourceIds'])
  for rid in subject['resourceIds']:
   assert rows[rid]['page']==path and rows[rid]['permalink']==path+'#file-'+rid
   assert 'data-destination="'+path+'#file-'+rid+'"' in legacy
for line in (ROOT/'_redirects').read_text().splitlines():
 assert not any(line.startswith(p+' ') for p in routes),'Canonical subject page redirected'
tanuvas=json.loads((ROOT/'data/tanuvas-source.json').read_text())
assert len({r['url'] for r in tanuvas['notes']})==len(tanuvas['notes'])
for r in tanuvas['notes']:
 assert r['id'] in rows and 'tanuvas' in rows[r['id']]['collections']
 assert rows[r['id']]['url']==r['url']
assert all('TANUVAS' in r['keywords'] for r in rows.values() if 'tanuvas' in r['collections'])
assert len(routes)==19
print(f'PASS: {len(routes)} canonical subject pages; four compact year hubs; old file anchors preserved; {len(tanuvas["notes"])} TANUVAS source entries reconciled.')

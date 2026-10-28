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
  assert 'data-subject-reader' in html and html.count('data-note-option=')==sum(any(('tanuvas' in rows[r]['collections'])==is_tanuvas for r in subject['resourceIds']) for is_tanuvas in [False,True])
  assert path+'syllabus/' in html and 'subject-practical-link' in html
  assert 'subject-book-grid' in html or not any({'year':n,'name':subject['name']} in book['subjects'] for book in json.loads((ROOT/'data/books.json').read_text()))
  assert 'subject-jump-links' not in html and 'filter-chips' not in html
  assert html.index('/assets/logic.js?')<html.index('/assets/subject-reader.js?')
  tanuvas_panel=html.split('id="tanuvas"',1)[1].split('id="books"',1)[0]
  assert 'class="resource-group' not in tanuvas_panel,'Single TANUVAS files must open directly'
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
anatomy=(ROOT/'bvsc/year-1/veterinary-anatomy/index.html').read_text().split('<main',1)[1]
assert anatomy.index('Units 1–6')<anatomy.index('Unit 7'), 'Unit order must be numeric'
assert len(routes)==19
print(f'PASS: {len(routes)} canonical subject pages; four compact year hubs; old file anchors preserved; {len(tanuvas["notes"])} TANUVAS source entries reconciled.')

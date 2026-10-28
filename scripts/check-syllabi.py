#!/usr/bin/env python3
"""Check unit coverage, topic identity, original PDF hashes and subject-only scope."""
from pathlib import Path
from collections import Counter
from html.parser import HTMLParser
import json,hashlib,re
from syllabus_pages import DATA,checklist_url
ROOT=Path(__file__).resolve().parent.parent
resources=json.loads((ROOT/'data/resources.json').read_text());mapping=json.loads((ROOT/'data/subject-map.json').read_text());outlines=json.loads((ROOT/'data/course-outlines.json').read_text())
assert {(s['year'],s['subject']) for s in DATA['subjects']}=={(int(y),n) for y,names in mapping['years'].items() for n in names}
allids=[];counts={}
for s in DATA['subjects']:
 assert s['sourceSha256']==hashlib.sha256((ROOT/s['sourceUrl'].lstrip('/')).read_bytes()).hexdigest()
 assert all(0<u['sourcePage']<=outlines['years'][str(s['sourcePdfYear'])]['pages'] for u in s['units'])
 assert len({u['key'] for u in s['units']})==len(s['units'])
 for kind in ['theory','practical']:
  nums=[u['number'] for u in s['units'] if u['kind']==kind and u['number'] is not None];assert nums==list(range(1,len(nums)+1)),(s['subject'],kind,'missing course unit')
 for unit in s['units']:
  assert unit['topics']
  # Splitting sentences and list separators must never drop syllabus words.
  compact=lambda text:re.sub(r'\W','',text)
  assert compact(' '.join(t['text'] for t in unit['topics']))==compact(unit['sourceText']),(s['subject'],unit['key'],'topic content omitted')
  allids.extend(t['id'] for t in unit['topics'])
 assert s['totalTopics']==sum(len(u['topics']) for u in s['units'])
 path=checklist_url(s['year'],s['subject']);html=(ROOT/path.strip('/')/'index.html').read_text();parent=f'/bvsc/year-{s["year"]}/{s["slug"]}/';hub=(ROOT/parent.strip('/')/'index.html').read_text()
 assert set(re.findall(r'data-topic="([^"]+)"',html))=={t['id'] for u in s['units'] for t in u['topics']}
 assert html.count('type="checkbox"')==s['totalTopics'] and 'data-syllabus=' in html
 assert 'data-syllabus=' not in hub and 'subject-syllabus-link' in hub
 assert hub.index('Syllabus Checklist')<hub.index('id="notes-title"')<hub.index('id="subject-books-title"')
 assert f'href="{parent}practicals/"' in hub and f'href="{path}"' in hub
 assert 'data-reader-tab=' not in hub and 'subject-notes-options' in hub
 assert all(x not in html for x in ['data-resource-id=','data-subject-reader'])
 assert 'Syllabus checklist' in html and path in (ROOT/'llms.txt').read_text()
 counts[s['subject']]={'units':len(s['units']),'topics':s['totalTopics']}
assert len(allids)==len(set(allids)),'Topic keys must not collide across repeated species or units'
for path in ['index.html','objective/index.html','clinical/handbooks/index.html','clinical/drug-index/index.html','books/index.html']:
 raw=(ROOT/path).read_text();assert '/assets/subject-hub.css' not in raw and '/assets/syllabus-checklist.js' not in raw,(path,'subject-only stylesheet leaked')
out=ROOT/'docs/qa/subject-hubs';out.mkdir(parents=True,exist_ok=True);(out/'syllabus-data.json').write_text(json.dumps({'subjects':len(DATA['subjects']),'units':sum(c['units'] for c in counts.values()),'topics':len(allids),'counts':counts},indent=2)+'\n')
print(f'PASS: {len(DATA["subjects"])} source-credited checklists, {sum(c["units"] for c in counts.values())} units/sections, {len(allids)} unique topic checkboxes; no syllabus text dropped; subject-only styles.')

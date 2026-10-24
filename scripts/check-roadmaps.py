#!/usr/bin/env python3
"""Guard researched credits, meaningful routes and preservation of original resources."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parent.parent
data=json.loads((ROOT/'data/year-roadmaps.json').read_text())
mapping=json.loads((ROOT/'data/subject-map.json').read_text())['years']
expected={1:(12,6,18,3),2:(15,7,22,5),3:(15,9,24,7),4:(8,9,17,4)}
rules=data['rules']
assert (rules['passPercent'],rules['attendancePercent'],rules['internalMarks'],rules['internshipMonths'])==(50,75,40,12)
assert rules['coverage']==[30,60,90,100]
assert rules['firstThreeTeachingDays']==210 and rules['fourthTeachingDays']==315
assert all(x['url'].startswith(('https://vci.dahd.gov.in/','https://ivri.nic.in/')) for x in data['academicSources'])
for key,year in data['years'].items():
 n=int(key);t,p,total,count=expected[n];subjects=year['subjects']
 assert (year['theory'],year['practical'],len(subjects))==(t,p,count)
 assert sum(s['theory'] for s in subjects)==t and sum(s['practical'] for s in subjects)==p
 assert t+p==total and {s['name'] for s in subjects}==set(mapping[key])
 assert year['durationYears']==(1.5 if n==4 else 1)
 path=f'/bvsc/year-{n}/roadmap/';html=(ROOT/path.strip('/')/'index.html').read_text()
 assert html.count('class="road-credit"')==count and 'aria-current="step"' in html
 assert html.count('class="road-check-track"')==4
 assert 'MSVE 2016' in html and 'current syllabus' in html
 assert 'LearningResource' in html and 'Sources &amp; academic notes' in html
 assert '/assets/roadmaps.css?' in html and path in (ROOT/'sitemap.xml').read_text()
 assert path in (ROOT/'llms.txt').read_text() and (ROOT/path.strip('/')/'index.md').exists()
 assert path in (ROOT/'index.html').read_text() and path in (ROOT/f'bvsc/year-{n}/index.html').read_text()
 assert 'roadmap/' in (ROOT/'study-tools/index.html').read_text()
 if n in [1,2]:assert 'Course-outline note.' in html
 if n==3:assert any(s['name']=='Livestock Farm Practices' and s['practical']==2 for s in subjects)
 if n==4:assert 'not the internship' in html and 'id="internship"' in html
 main=re.search(r'<main\b[^>]*>(.*?)</main>',html,re.S)[1]
 assert not re.search(r'<a[^>]+href="https?://(?!notes\.thatvetguy\.net)',main),'Roadmap content must not add forbidden outbound links'
assert sum(x[2] for x in expected.values())==rules['totalCredits']==81
print('PASS: four roadmap routes; 18/22/24/17 credits reconcile; 19 course entries; cited academic scheme; no new outbound links.')

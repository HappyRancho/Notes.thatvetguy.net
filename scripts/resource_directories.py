"""Source-backed discovery routes; catalogue entries remain on their subject pages."""
from html import escape as e
from pathlib import Path
import json
from subject_pages import url as subject_url
from syllabus_pages import DATA as SYLLABI,checklist_url
from course_outlines import outline_url
ROOT=Path(__file__).resolve().parent.parent
TANUVAS=json.loads((ROOT/'data/tanuvas-source.json').read_text())
ROUTES=[('/bvsc/tanuvas-notes/','TANUVAS Notes','TANUVAS veterinary notes by professional year, subject and unit'),('/bvsc/syllabus/','BVSc Syllabus & Course Outlines','MSVE 2016 theory and practical syllabus checklists by subject')]

def shortcuts(b):
    return '<nav class="resource-shortcuts" aria-label="Browse veterinary study material">'+''.join(b.link(path,b.icon(ic)+'<span>'+label+'</span>') for path,label,ic in [('/bvsc/','All subjects','book'),('/bvsc/tanuvas-notes/','TANUVAS notes','paper'),('/bvsc/syllabus/','Syllabus &amp; outlines','check')])+'</nav>'

def tanuvas(b):
    path='/bvsc/tanuvas-notes/'
    desc='TANUVAS veterinary notes across all four BVSc & AH professional years. Browse 16 subjects and 59 PDFs, with Google Drive access and subject syllabus checklists.'
    body=b.article_intro('TANUVAS Notes for BVSc & AH',desc).replace('container reading-page','container reading-page resource-directory')
    source_guide='<section class="directory-guide"><h2>Your subject, then your unit</h2><p>Open a title to find its exact entry on the subject page, or browse the subject’s Drive folder. Compare the notes with your syllabus checklist to identify topics that need another source.</p><p>TANUVAS stands for Tamil Nadu Veterinary and Animal Sciences University. Original authors retain credit. This is an independent study directory, not an official university website.</p>'+b.link(TANUVAS['rootUrl'],'Browse the complete TANUVAS Drive '+b.icon('external'),'directory-next')+shortcuts(b)+'</section>'
    available=[y for y in b.LIBRARY['years'] if any(r['year']==y['year'] for r in TANUVAS['notes'])]
    body+='<nav class="directory-jump" aria-label="TANUVAS years">'+''.join(b.link('#year-'+str(y['year']),b.DATA['labels'][str(y['year'])]) for y in available)+'</nav>'
    items=[]
    for year in available:
        n=year['year'];label=b.DATA['labels'][str(n)]
        folders=[f for f in TANUVAS['subjectFolders'] if f['year']==n]
        body+='<section class="directory-year" id="year-'+str(n)+'"><header><span class="rx-row-icon sky">'+str(n)+'</span><h2>'+e(folders[0]['yearName'])+'</h2></header><div class="directory-grid">'
        for subject in folders:
            rows=sorted([r for r in TANUVAS['notes'] if r['folderId']==subject['id']],key=lambda r:r['sourceOrder'])
            if not rows:continue
            target=subject_url(n,subject['subject'])
            body+='<article class="directory-card"><h3>'+b.link(target+'#tanuvas',e(subject['name']))+'</h3><ul class="directory-courses">'
            for row in rows:
                href=target+'#file-'+row['id'];items.append((row['title'],href))
                body+='<li data-tanuvas-course="'+e(row['id'])+'">'+b.link(href,'<span><strong>'+e(row['title'])+'</strong><small>PDF · View in subject notes</small></span>'+b.icon('chevron'))+'</li>'
            body+='</ul><nav class="directory-actions" aria-label="'+e(subject['name'],quote=True)+' resources">'+b.link(checklist_url(n,subject['subject']),'Syllabus checklist '+b.icon('check'),'directory-next')+b.link(subject['url'],'Drive folder '+b.icon('external'),'directory-next')+'</nav></article>'
        body+='</div></section>'
    body+=source_guide+'<p class="source-note">'+str(len(TANUVAS['notes']))+' PDFs · '+str(len(TANUVAS['subjectFolders']))+' subjects · Drive listing checked '+e(TANUVAS['reviewed'])+'. Access to external files may change.</p></div>'
    b.write_page(path,'TANUVAS Notes for BVSc & AH',desc,body,items)

def syllabus(b):
    path='/bvsc/syllabus/';desc='Your BVSc & AH syllabus in one place: subject checklists, original professional-year course outlines, and theory and practical topics from MSVE 2016.'
    body=b.article_intro('BVSc & AH Syllabus & Course Outlines',desc).replace('container reading-page','container reading-page resource-directory')
    source_guide='<section class="directory-guide"><h2>Use the outline to plan; use the checklist to track</h2><p>The checklists reproduce course topics from the Veterinary Council of India’s MSVE 2016 curriculum hosted by DUVASU. They separate theory and practical work and link back to the source. Your university’s current timetable, amendments and examination instructions take precedence.</p><p>Ticked topics are saved in this browser on this device. A tick is a personal study marker, not a record of attendance or an official completion certificate.</p>'+shortcuts(b)+'</section>'
    body+='<nav class="directory-jump" aria-label="Syllabus years">'+''.join(b.link('#year-'+str(n),b.DATA['labels'][str(n)]) for n in range(1,5))+'</nav>'
    items=[]
    for n in range(1,5):
        label=b.DATA['labels'][str(n)]
        body+='<section class="directory-year" id="year-'+str(n)+'"><header><span class="rx-row-icon mint">'+str(n)+'</span><h2>'+label+'</h2>'+b.link(outline_url(n),'Course outline PDF '+b.icon('paper'),'directory-outline')+'</header><ul class="directory-checklists">'
        for subject in SYLLABI['subjects']:
            if subject['year']!=n:continue
            href=checklist_url(n,subject['subject']);items.append((subject['subject']+' syllabus checklist',href))
            counts=[str(sum(len(u['topics']) for u in subject['units'] if u['kind']==kind))+' '+kind+' topics' for kind in ['theory','practical'] if any(u['kind']==kind for u in subject['units'])]
            body+='<li>'+b.link(href,'<span class="rx-row-icon sky">'+b.icon('check')+'</span><span><strong>'+e(subject['subject'])+'</strong><small>'+e(' · '.join(counts))+'</small></span>'+b.icon('chevron'))+'</li>'
        body+='</ul></section>'
    body+=source_guide+'<section class="directory-guide"><h2>Why a subject may appear in a different year</h2><p>The library keeps its existing professional-year navigation. The original first-professional outline includes Biochemistry, while this library places its resources in Year 2. The checklist links to the original source location; use the subject name and course content to resolve the difference.</p><h2>Turn an outline into a working revision list</h2><p>Open your subject checklist beside your lecture plan. Identify the topics currently being taught, read the matching notes, then tick a topic when you can explain it without the page in front of you. Keep practical identification, procedures and records separate from theory revision: reading a procedure is not the same as performing it under supervision.</p>'+b.link(SYLLABI['source'],'Read the full VCI MSVE 2016 curriculum (PDF) '+b.icon('external'),'directory-next')+'<p class="source-note">Source transcription checked '+e(SYLLABI['reviewed'])+'. This is a study aid, not an official university portal.</p></section></div>'
    b.write_page(path,'BVSc & AH Syllabus & Course Outlines',desc,body,items)

def render(b):
    tanuvas(b);syllabus(b)

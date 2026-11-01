"""Year-start field guides with verified academic data and direct study routes."""
from pathlib import Path
from html import escape as e
import json,re
from library import slug
from course_outlines import outline_url

ROOT=Path(__file__).resolve().parent.parent
DATA=json.loads((ROOT/'data/year-roadmaps.json').read_text())
GUIDANCE=json.loads((ROOT/'data/roadmap-guidance.json').read_text())

def url(year):return f'/bvsc/year-{year}/roadmap/'
def subject_url(year,name):return f'/bvsc/year-{year}/{slug(name)}/'
def plus():return '<span class="road-expand" aria-hidden="true"></span>'

def stages(b,year):
    labels=['Start strong','Connect','Apply','Clinics']
    return '<nav class="road-stages" aria-label="BVSc study journey"><ol>'+''.join('<li>'+b.link(url(n),'<span>'+str(n)+'</span><small>'+label+'</small>','road-stage'+(' road-current' if n==year else '')).replace('class="road-stage road-current"','class="road-stage road-current" aria-current="step"')+'</li>' for n,label in enumerate(labels,1))+'<li>'+b.link(url(4)+'#internship',b.icon('cap')+'<small>Internship</small>','road-internship-step')+'</li></ol></nav>'

def heading(number,title,deck):
    return '<header class="road-heading"><span aria-hidden="true">'+number+'</span><div><h2>'+e(title)+'</h2><p>'+e(deck)+'</p></div></header>'

def hero(b,year,d,g):
    from homepage import roadmap_art
    label=b.DATA['labels'][str(year)]
    return '<header class="road-hero"><div class="road-hero-top"><div><p class="road-eyebrow">BVSc &amp; AH · YOUR YEAR STARTS HERE</p><h1>'+label+' Roadmap</h1></div>'+roadmap_art(year)+'</div><p class="road-headline">'+e(g['headline'])+'</p><p class="road-intro">'+e(g['intro'])+'</p><div class="road-hero-actions">'+b.link('#subjects',b.icon('check')+'Subject checklists','road-action road-action-primary')+b.link(outline_url(year),b.icon('paper')+'Year course outline','road-action road-outline')+'</div><p class="road-mission">'+b.icon('spark')+e(g['mission'])+'</p></header>'

def start(b,g):
    return '<section class="road-start" id="start">'+heading('01','Start with these three moves','A practical setup for your first week.')+'<ol class="road-launch">'+''.join('<li><span class="road-step" aria-hidden="true">'+str(i)+'</span><div><h3>'+e(p['title'])+'</h3><p>'+e(p['text'])+'</p></div></li>' for i,p in enumerate(g['priorities'],1))+'</ol></section>'

def subjects(b,year,d,g):
    body='<section id="subjects" class="road-subject-section">'+heading('02','Your subjects, with a method','Open a study approach. Use the unit checklist to track the actual syllabus.')+'<div class="road-subject-grid">'
    for i,s in enumerate(d['subjects']):
        tip=g['subjects'][s['name']];base=subject_url(year,s['name'])
        from homepage import subject_icon
        ic,tone=subject_icon(s['name'])
        body+='<article class="road-subject-card"><div class="road-subject-title"><span class="road-subject-icon '+tone+'" aria-hidden="true">'+b.icon(ic)+'</span><h3>'+e(s['name'])+'</h3></div><p class="road-subject-goal">'+e(tip['goal'])+'</p><details class="road-subject"><summary><span>Study approach</span>'+plus()+'</summary><div class="road-subject-body"><dl>'
        for label,key in [('Build the idea','build'),('Practise it','practise'),('Check yourself','test')]:body+='<div><dt>'+label+'</dt><dd>'+e(tip[key])+'</dd></div>'
        body+='</dl><p class="road-watch"><strong>Avoid this trap</strong>'+e(tip['trap'])+'</p>'+b.link(base+'practicals/','Open practical vault '+b.icon('arrow'),'road-practical-link')+'</div></details><div class="road-subject-links">'+b.link(base+'syllabus/',b.icon('check')+'Syllabus checklist','road-checklist-link')+b.link(base,'Notes & books '+b.icon('arrow'))+'</div></article>'
    return body+'</div></section>'

def methods(b,g):
    body='<section id="study-method" class="road-methods">'+heading('03','Make the work count','Specific techniques for the places students get stuck.')+'<div class="road-chapters">'
    for i,c in enumerate(g['chapters'],1):
        body+='<details class="road-chapter"><summary><span class="road-chapter-index" aria-hidden="true">'+str(i).zfill(2)+'</span><span class="road-chapter-label"><strong>'+e(c['title'])+'</strong><small>'+e(c['deck'])+'</small><span class="road-read">Read the guide</span></span>'+plus()+'</summary><div class="road-chapter-body">'+''.join('<p>'+e(p)+'</p>' for p in c['paragraphs'])+'<aside class="road-example"><strong>'+e(c['exampleLabel'])+'</strong><p>'+e(c['example'])+'</p></aside><p class="road-takeaway">'+b.icon('bulb')+'<span>'+e(c['takeaway'])+'</span></p></div></details>'
    return body+'</div></section>'

def finish(b,g):
    body='<section id="keep-on-track" class="road-finish">'+heading('04','Keep the year on track','Use the next small task to regain momentum.')+'<div class="road-finish-grid">'
    for tone,title,items,ic in [('mint','When the backlog builds',g['reset'],'map'),('yellow','Before the exam stretch',g['exam'],'target')]:
        body+='<article class="road-finish-card '+tone+'"><h3>'+b.icon(ic)+title+'</h3><ol>'+''.join('<li>'+e(t)+'</li>' for t in items)+'</ol></article>'
    return body+'</div></section>'

def credits(b,year,d):
    body='<div class="road-credit-list">'
    for s in d['subjects']:
        body+=b.link(subject_url(year,s['name']),'<span>'+e(s['short'])+'<small>'+str(s['theory'])+' theory + '+str(s['practical'])+' practical</small></span><strong>'+str(s['theory']+s['practical'])+'<span class="sr-only"> credits</span></strong>','road-credit')
    return body+'</div>'

def academic(b,year,d):
    r=DATA['rules']
    body='<details class="road-academic-brief" id="academic-details"><summary><span>'+b.icon('paper')+'<strong>Credits, exams & course-outline notes</strong></span>'+plus()+'</summary><div class="road-academic-body"><p>'+e(DATA['scope'])+'</p>'
    if year in [1,2]:body+='<p class="road-watch"><strong>Course-outline note.</strong>'+e(d['outlineNote'])+'</p>'
    body+='<div class="road-rule-grid"><div><strong>'+str(d['theory']+d['practical'])+' credits</strong><span>'+str(d['theory'])+' theory + '+str(d['practical'])+' practical</span></div><div><strong>'+str(r['attendancePercent'])+'% attendance</strong><span>Theory and practical separately</span></div><div><strong>'+str(r['passPercent'])+'% to pass</strong><span>Theory and practical separately</span></div><div><strong>'+str(315 if year==4 else 210)+' teaching days</strong><span>Minimum; annual exams excluded</span></div></div>'+credits(b,year,d)
    body+='<h3>Theory-bearing subject assessments</h3><p>MSVE 2016 specifies three internal assessments of 40 marks each; the best two count under that scheme. The 30%, 60% and 90% coverage milestones are cumulative, not predictions of chapters or exam weightage. The annual examination covers the whole course. Confirm the dates and marking scheme with your university.</p>'
    if year>=3:body+='<p><strong>Practical-only courses:</strong> VCC/LFC follow separate assessments at 50% and full course completion. Use the department’s skill, record and viva requirements rather than the theory-internal pattern.</p>'
    body+=b.link(outline_url(year),'Read the year course outline (PDF) '+b.icon('paper'),'road-action road-outline')+'</div></details>'
    return body

def sources(b,year,d,g):
    body='<details class="road-sources"><summary><span>'+b.icon('book')+'<strong>Sources & reading notes</strong></span>'+plus()+'</summary><div class="road-source-body"><p>The academic figures use MSVE 2016. The study workflows and examples are original editorial guidance informed by the readings below. Student discussions describe individual experiences; they do not establish examination rules or guaranteed outcomes.</p><ul>'
    for s in DATA['academicSources'][:2]:body+='<li>'+b.link(s['url'],e(s['title']))+'<small>'+e(s['location'])+'</small></li>'
    for ident in g['sources']:
        s=next(s for s in GUIDANCE['sources'] if s['id']==ident)
        body+='<li>'+b.link(s['url'],e(s['title']))+'<small>'+e(s['kind'])+' · '+e(s['note'])+'</small></li>'
    body+='</ul><p>Research reviewed <time datetime="'+GUIDANCE['reviewed']+'">1 November 2026</time>. International learning resources inform study methods only; your university’s current syllabus and assessment rules take precedence.</p></div></details>'
    return body

def render(b):
    for key,d in DATA['years'].items():
        year=int(key);g=GUIDANCE['years'][key];label=b.DATA['labels'][key];path=url(year)
        description=f'{label} BVSc & AH roadmap with practical subject study methods, first-week priorities, exam preparation, syllabus checklists and the year course outline.'
        body=b.article_intro(label+' Roadmap',description,[('BVSc','/bvsc/'),(label,f'/bvsc/year-{year}/')]).replace('container reading-page','container reading-page roadmap-page',1)
        body=re.sub(r'<header class="reading-header rx-section">.*?</header>',lambda _:stages(b,year)+hero(b,year,d,g),body,flags=re.S)
        body+='<nav class="road-jumps" aria-label="On this roadmap">'+''.join(b.link('#'+ident,text) for ident,text in [('start','Start here'),('subjects','Subjects'),('study-method','Study methods'),('keep-on-track','Stay on track')])+'</nav>'
        body+=start(b,g)+subjects(b,year,d,g)+methods(b,g)+finish(b,g)
        if year==4:body+='<section class="road-internship" id="internship"><span class="road-eyebrow">THE NEXT CHAPTER</span><h2>Ready for internship</h2><p>'+e(g['internship'])+'</p>'+b.link('/study-tools/veterinary-careers/','Explore where veterinary can take you '+b.icon('arrow'),'road-action')+'</section>'
        body+=academic(b,year,d)+sources(b,year,d,g)+'<nav class="road-next" aria-label="Continue exploring">'+b.link(f'/bvsc/year-{year}/',b.icon('arrow')+'All '+label+' resources')+b.link(url(year+1) if year<4 else '/study-tools/veterinary-careers/','Next year’s roadmap' if year<4 else 'Explore career options')+'</nav></div>'
        b.write_page(path,label+' BVSc Roadmap: Study Guide & Subject Checklists',description,body,[(s['name']+' syllabus checklist',subject_url(year,s['name'])+'syllabus/') for s in d['subjects']])

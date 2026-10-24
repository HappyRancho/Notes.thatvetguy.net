"""Researched professional-year roadmaps, using the existing Rx Notes shell."""
from pathlib import Path
from html import escape as e
import json
from library import slug
from course_outlines import outline_url

ROOT=Path(__file__).resolve().parent.parent
DATA=json.loads((ROOT/'data/year-roadmaps.json').read_text())

def url(year):return f'/bvsc/year-{year}/roadmap/'

def section(b,title,ic,note=''):
    return '<header class="road-section-heading"><span class="road-section-icon">'+b.icon(ic)+'</span><div><h2>'+e(title)+'</h2>'+('<p class="road-hand">'+e(note)+'</p>' if note else '')+'</div></header>'

def stages(b,year):
    body='<nav class="road-stages" aria-label="BVSc study journey"><ol>'
    for n in range(1,5):
        label=DATA['years'][str(n)]['phase']
        if n==1:label='Foundation'
        body+='<li><a href="'+url(n)+'"'+(' aria-current="step"' if n==year else '')+'><span>'+str(n)+'</span><small>'+e(label)+'</small></a></li>'
    body+='<li><a href="'+url(4)+'#internship" class="road-internship-step"><span aria-hidden="true">'+b.icon('cap')+'</span><small>Internship</small></a></li></ol></nav>'
    return body

def glance(b,year,d):
    total=d['theory']+d['practical'];r=DATA['rules']
    fourth_stat=('210','teaching days','minimum; annual exam days excluded') if year==1 else ('3 × 40','internal marks','three scheduled tests; 40 marks each')
    third=('1.5','years','18 months before the separate internship') if year==4 else ('50%','to pass','theory and practical, counted separately')
    if year==4:fourth_stat=('50%','to pass','theory and practical, counted separately')
    stats=[(str(total),'credits',f'{d["theory"]} theory + {d["practical"]} practical'),(str(len(d['subjects'])),'core courses','Anatomy · Physiology · LPM' if year==1 else 'Theory and practical courses'),third,fourth_stat]
    body='<section class="road-card">'+section(b,'Year at a glance','spark')+'<ul class="road-stats">'
    for tone,(value,label,detail) in zip(['yellow','peach','sky','mint'],stats):
        body+='<li class="'+tone+'"><strong>'+e(value)+'</strong><span>'+e(label)+'</span><small>'+e(detail)+'</small></li>'
    body+='</ul><ul class="road-brief">'+''.join('<li>'+e(t)+'</li>' for t in d['notes'])+'</ul>'
    body+='<p class="road-rule"><strong>Attendance: '+str(r['attendancePercent'])+'%</strong> minimum in theory and practical separately. '+('315' if year==4 else '210')+' teaching days minimum, excluding annual exams.</p></section>'
    return body

def credits(b,year,d):
    maximum=max(s['theory']+s['practical'] for s in d['subjects'])
    body='<section class="road-card">'+section(b,'Where the credits go','chart','Bigger bar, bigger commitment.')+'<p class="road-legend"><span><i class="road-theory-key"></i>Theory</span><span><i class="road-practical-key"></i>Practical</span></p><p class="road-hint">Tap a row to find its books and notes.</p><ul class="road-credit-list">'
    for s in d['subjects']:
        total=s['theory']+s['practical'];label=f'{s["theory"]} theory + {s["practical"]} practical'
        chart='<span class="road-bar" aria-hidden="true"><i class="road-theory" style="width:'+f'{s["theory"]/maximum*100:.4f}'+'%"></i><i class="road-practical" style="width:'+f'{s["practical"]/maximum*100:.4f}'+'%"></i></span>'
        body+='<li>'+b.link(f'/bvsc/year-{year}/#'+slug(s['name']),'<span class="road-credit-label">'+e(s['short'])+'<small>'+e(label)+'</small></span>'+chart+'<strong>'+str(total)+'<span class="sr-only"> credits</span></strong>','road-credit')+'</li>'
    body+='</ul><p class="road-rule">'+str(d['theory']+d['practical'])+' credits in total · '+str(d['theory'])+' theory + '+str(d['practical'])+' practical.</p></section>'
    return body

def checkpoints(b,year):
    notes={1:'Internal marks are your safety net.',2:'Keep the number subjects warm all year.',3:'Applied subjects reward practical understanding.',4:'Practise the reasoning, not just the answer.'}
    body='<section class="road-card">'+section(b,'Exam checkpoints','target',notes[year])+'<ol class="road-checkpoints">'
    for i,(percent,label,helptext) in enumerate(zip(DATA['rules']['coverage'],['Internal 1','Internal 2','Internal 3','Annual exam'],['40 marks · close the first gaps','40 marks · connect the concepts','40 marks · revisit weak areas','Full course · theory and practical'])):
        body+='<li><span class="road-check-number" aria-hidden="true">'+str(i+1)+'</span><h3>'+label+'</h3><p>'+('By '+str(percent)+'% course coverage' if i<3 else '100% of the course')+'</p><span class="road-check-track" aria-hidden="true"><i style="width:'+str(percent)+'%"></i></span><small>'+helptext+'</small></li>'
    body+='</ol><p class="road-rule">For theory-bearing subjects: three internals of 40 marks each; the best two assessments count under MSVE 2016. Use your university’s current dates and marking scheme.</p>'
    if year in [3,4]:body+='<p class="road-rule"><strong>Practical-only courses:</strong> VCC/LFC assessments follow a separate schedule at 50% and full course completion. Records, observed skills and viva preparation matter.</p>'
    return body+'</section>'

def playbook(b,year,d):
    body='<section class="road-card road-playbook">'+section(b,'Your subject playbook','book','Know what to learn. Know how to revise.')
    for i,s in enumerate(d['subjects']):
        body+='<details class="road-subject"'+(' open' if i==0 else '')+'><summary><span class="road-subject-number" aria-hidden="true">'+str(i+1)+'</span><h3>'+e(s['name'])+'</h3>'+b.icon('chevron')+'</summary><div class="road-subject-body"><p><strong>Focus on</strong> '+e(s['focus'])+'</p><p><strong>Try this</strong> '+e(s['method'])+'</p><p class="road-small-tip">'+e(s['pitfall'])+'</p><div class="road-subject-links">'+b.link(f'/bvsc/year-{year}/#'+slug(s['name']),'Books & course outline '+b.icon('arrow'))
        own=next(y for y in b.LIBRARY['years'] if y['year']==year);subject=next(x for x in own['subjects'] if x['name']==s['name'])
        if subject['count']:body+=b.link(f'/bvsc/year-{year}/notes/#'+slug(s['name']),'Topic-wise notes '+b.icon('arrow'))
        body+='</div></div></details>'
    return body+'</section>'

def habits(b,d):
    body='<section class="road-card">'+section(b,'A week that works','map','Suggested rhythm. Adjust it to your timetable.')+'<ol class="road-rhythm">'
    body+=''.join('<li><h3>'+e(title)+'</h3><p>'+e(text)+'</p></li>' for title,text in d['rhythm'])+'</ol></section>'
    body+='<section class="road-card">'+section(b,'Small habits, big saves','bulb')+'<ul class="road-brief">'+''.join('<li>'+e(t)+'</li>' for t in d['habits'])+'</ul><p class="road-editorial">Study advice, not an exam rule. A first-person account by Dr. Bhupender (AIEEA Animal Science 2022 Rank 1) informed the concise-revision and error-review habits; his PG strategy is not a professional-exam blueprint.</p></section>'
    body+='<section class="road-card">'+section(b,'Before the final stretch','check')+'<ol class="road-rhythm">'+''.join('<li><h3>'+e(title)+'</h3><p>'+e(text)+'</p></li>' for title,text in d['finish'])+'</ol><p class="road-hand road-margin">'+e(d['margin'])+'</p></section>'
    return body

def sources(b,year,d):
    body='<details class="road-sources road-card"><summary>Sources &amp; academic notes '+b.icon('chevron')+'</summary><div><p>'+e(DATA['scope'])+'</p><p>'+e(d['outlineNote'])+'</p><ol>'
    for s in DATA['academicSources'][:2]:body+='<li><cite>'+e(s['title'])+'</cite><span>'+e(s['location'])+'</span></li>'
    body+='</ol><p>Assessment coverage is cumulative: the 30%, 60% and 90% milestones are not guaranteed chapter ranges or predicted exam weightage.</p><p>Study suggestions are original editorial guidance based on the course topics and a reviewed first-person preparation account. No marks or rank are promised.</p><p>Research checked <time datetime="'+DATA['reviewed']+'">24 October 2026</time>.</p>'+b.link(outline_url(year),'Read the '+b.DATA['labels'][str(year)]+' course outline (PDF) '+b.icon('paper'),'road-outline')+'</div></details>'
    return body

def render(b):
    for key,d in DATA['years'].items():
        year=int(key);label=b.DATA['labels'][key];path=url(year)
        description=f'{label} BVSc & AH study roadmap: subjects, theory and practical credits, exam checkpoints and practical revision advice. Based on the MSVE 2016 professional-year scheme.'
        body=b.article_intro(label+' BVSc & AH Roadmap',description,[('BVSc','/bvsc/'),(label,f'/bvsc/year-{year}/')])
        body=body.replace('container reading-page','container reading-page roadmap-page',1)
        # The shell, header and bottom navigation are the existing shared components.
        body=body.replace('<h1>'+e(label+' BVSc & AH Roadmap')+'</h1>','<h1>'+e(label+' Roadmap')+'</h1>',1)
        body=body.replace('<p>'+e(description)+'</p>','<p class="road-hand">'+e(d['subtitle'])+'</p>',1)
        body+=stages(b,year)+'<details class="road-academic-brief"><summary><span>MSVE 2016 · Syllabus &amp; outline notes</span>'+b.icon('chevron')+'</summary><div><p>'+e(DATA['scope'])+'</p>'
        if year in [1,2]:body+='<p><strong>Course-outline note.</strong> '+e(d['outlineNote'])+'</p>'
        body+='</div></details>'
        body+='<div class="roadmap-columns"><div class="roadmap-column">'+glance(b,year,d)+credits(b,year,d)+checkpoints(b,year)+'</div><div class="roadmap-column">'+playbook(b,year,d)+habits(b,d)
        if year==4:body+='<section class="road-card" id="internship">'+section(b,'Next stop: internship','stethoscope')+'<p>After passing the fourth professional and completing the required credits, the MSVE 2016 programme includes a separate compulsory 12-month rotating internship.</p><p>Follow your university’s posting schedule, supervision, logbook and completion requirements. Clinical Practices II is part of the fourth professional; it is not the internship.</p></section>'
        body+='</div></div>'+sources(b,year,d)+'</div>'
        b.write_page(path,label+' BVSc Roadmap: Subjects, Credits & Study Plan',description,body,[(s['name'],f'/bvsc/year-{year}/#'+slug(s['name'])) for s in d['subjects']])

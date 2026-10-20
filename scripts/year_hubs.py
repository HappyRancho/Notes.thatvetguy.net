"""Four year hubs: books, a direct notes destination and a roadmap per subject."""
from html import escape as e
from pathlib import Path
import json,re
from library import slug,natural
ROOT=Path(__file__).resolve().parent.parent

def subject_books(b,books):
    if not books:return '<p class="year-book-empty">No book recommendation listed yet. Check your department’s prescribed practical manual.</p>'
    rows=[]
    for r in books:
        summary='<span class="rx-row-icon sky" aria-hidden="true">'+b.icon('book')+'</span><span class="year-book-copy"><strong>'+e(r['title'])+'</strong><span>'+e(r['author'])+'</span></span>'+b.icon('chevron')
        # Research references are not shared copies. A real disclosure exposes
        # the existing reading guidance without inventing a download URL.
        rows.append('<li><details class="year-book-detail"><summary>'+summary+'</summary><div class="year-book-guidance"><p>'+e(r['description'])+'</p><p class="year-book-status">Reading recommendation · no linked copy available.</p></div></details></li>')
    return '<ul class="year-book-list">'+''.join(rows)+'</ul>'

def roadmap(b,name,ident):
    m=b.SUBJECTS[name];steps=['Make a checklist from your university syllabus.',m['studyTip'],'Revisit '+', '.join(m['topics'][:2])+', then test your recall without the notes.']
    return '<details class="year-subject-roadmap" id="roadmap-'+ident+'"><summary>'+b.icon('map')+'<span>Roadmap</span>'+b.icon('chevron')+'</summary><ol>'+''.join('<li>'+e(t)+'</li>' for t in steps)+'</ol></details>'

def notes_page(b,y):
    from library_views import controls,group,empty
    year=y['year'];label=b.DATA['labels'][str(year)];path=f'/bvsc/year-{year}/notes/'
    desc=f'Topic-wise {label} BVSc & AH notes, grouped by subject and unit. Pick a subject below or search for the topic you need.'
    body=b.article_intro(label+' Topic-wise Notes',desc,[('BVSc','/bvsc/'),(label,f'/bvsc/year-{year}/')])
    body+='<div class="filter-collection year-notes-reader" data-filter-subjects>'+controls(b,[(s['slug'],s['name']) for s in y['subjects'] if s['count']],f'year-{year}',True)
    allrows=[]
    for si,s in enumerate(y['subjects']):
        rows=[b.CATALOGUE[r] for r in s['resourceIds']];allrows+=rows
        body+='<section class="year-note-subject" data-subject-section id="'+s['slug']+'"><header><h2>'+e(s['name'])+'</h2><button type="button" class="studied-button js-only" data-studied="'+s['slug']+'" aria-pressed="false">'+b.icon('check')+'<span>Mark as studied</span></button></header>'
        guide=b.SUBJECTS.get(s['name'],{})
        if guide.get('summary'):
            intro=guide['summary'].split('. ',1)[0]+'. '+guide.get('studyTip','')
            body+='<p class="year-subject-summary">'+e(intro)+'</p>'
        units=sorted({r['unit'] for r in rows},key=lambda u:(int(re.search(r'\d+',u)[0]) if re.search(r'\d+',u) else 999,natural(u)))
        for ui,unit in enumerate(units):body+=group(b,unit,[r for r in rows if r['unit']==unit],s['slug']+'-'+slug(unit),si==0 and ui==0,level=3,filterkey=s['slug'])
        if not rows:body+=empty(b,'Notes are coming soon')
        body+='</section>'
    body+='<p class="filter-empty" hidden>No notes match. '+b.link('/request-resource/','Request a topic')+'</p></div></div>'
    b.write_page(path,label+' Topic-wise BVSc Notes',desc,body,[(r['title'],r['url']) for r in allrows])

def index(b):
    from homepage import subject_icon
    books=json.loads((ROOT/'data/book-recommendations.json').read_text())['books']
    desc='Recommended books, topic-wise notes and roadmaps for BVSc & AH. Choose a subject to open its section in the right year.'
    body=b.article_intro('BVSc Notes & Books',desc)+'<div class="bvsc-year-sections">';items=[]
    for y in b.LIBRARY['years']:
        year=y['year'];label=b.DATA['labels'][str(year)];path=f'/bvsc/year-{year}/';tone=['yellow','peach','sky','mint'][year-1]
        body+='<section class="bvsc-year-section" id="year-'+str(year)+'"><header class="bvsc-year-heading"><span class="bvsc-year-number '+tone+'" aria-hidden="true">'+str(year)+'</span><div><h2>'+e(label)+'</h2><p>'+str(len(y['subjects']))+' subjects · '+str(y['count'])+' notes</p></div>'+b.link(path,'View year '+b.icon('arrow'),'bvsc-year-link')+'</header><div class="bvsc-subject-grid">'
        for subject in y['subjects']:
            ic,icon_tone=subject_icon(subject['name']);nbooks=sum(r['year']==year and r['subject']==subject['name'] for r in books)
            meta=(str(nbooks)+' '+('book' if nbooks==1 else 'books')+' · ' if nbooks else '')+str(subject['count'])+' '+('note' if subject['count']==1 else 'notes')
            if not nbooks and not subject['count']:meta='Roadmap available'
            url=path+'#'+subject['slug'];items.append((subject['name']+' · '+label,url))
            body+=b.link(url,'<span class="rx-row-icon '+icon_tone+'" aria-hidden="true">'+b.icon(ic)+'</span>'+b.icon('chevron')+'<h3>'+e(subject['name'])+'</h3><p>'+e(meta)+'</p>','bvsc-subject-tile')
        body+='</div></section>'
    body+='</div><p class="source-note bvsc-syllabus-note">Year grouping may vary by university. Check your syllabus.</p></div>'
    b.write_page('/bvsc/','BVSc Notes & Books',desc,body,items)

def render(b):
    from course_outlines import outline_url
    books=json.loads((ROOT/'data/book-recommendations.json').read_text())['books'];copy=json.loads((ROOT/'data/year-hub-microcopy.json').read_text())
    from homepage import subject_icon,CONTENT
    for y in b.LIBRARY['years']:
        year=y['year'];label=b.DATA['labels'][str(year)];path=f'/bvsc/year-{year}/'
        desc=f'{label} BVSc & AH notes, books and study roadmaps, organised by subject.'
        body=b.article_intro(label+' Notes & Books',desc,[('BVSc','/bvsc/')])
        body=body.replace('<div class="container reading-page">','<div class="container reading-page year-page">',1)
        body=body.replace(b.icon('book'),b.icon('cap'),1)
        body+='<a href="#road-map" class="year-roadmap-cta"><span class="year-map-art" aria-hidden="true">'+b.icon('map')+'</span><span><strong>'+label+' BVSc Road Map</strong><span class="rx-hand">'+e(CONTENT['roadmaps'][str(year)]['description'])+'</span></span><span class="year-roadmap-arrow" aria-hidden="true">'+b.icon('arrow')+'</span></a>'
        body+='<span id="books" class="anchor-alias"></span><div class="year-subject-sections">'
        for i,subject in enumerate(y['subjects']):
            name=subject['name'];own=[r for r in books if r['year']==year and r['subject']==name];ic,tone=subject_icon(name)
            display='Livestock Production & Management' if name=='Livestock Production Management' else name
            body+='<section class="year-subject-section" id="'+subject['slug']+'"><header><span class="rx-row-icon '+tone+'" aria-hidden="true">'+b.icon(ic)+'</span><h2>'+e(display)+'</h2></header><div class="year-subject-actions">'
            body+=b.link(outline_url(year,name),b.icon('paper')+'<span>Course Outline</span>'+b.icon('chevron'),'year-course-link '+('mint' if tone=='mint' else 'peach'))
            if subject['count']:body+=b.link(path+'notes/#'+subject['slug'],b.icon('paper')+'<span>Topic-wise Notes</span>'+b.icon('chevron'),'year-notes-link')
            else:body+='<span class="year-notes-unavailable">'+b.icon('paper')+'<span>Notes coming soon</span></span>'
            body+='</div>'
            if name=='Veterinary Biochemistry':body+='<p class="year-outline-note">Biochemistry is included in the 1st Year outline PDF.</p>'
            body+='<h3 class="year-books-heading">'+b.icon('book')+'<span>Books</span></h3>'+subject_books(b,own)+'</section>'
            if i==0:body+='<p class="year-margin-note">'+e(copy[str(year)])+'</p>'
        body+='</div><details class="syllabus year-roadmap-details" id="road-map"><summary>'+e(label)+' Road Map '+b.icon('map')+'</summary><ol class="topic-list">'+''.join('<li>'+e(step)+'</li>' for step in CONTENT['roadmaps'][str(year)]['steps'])+'</ol>'+b.link(outline_url(year),'Full '+label+' Course Outline (PDF) '+b.icon('paper'),'year-full-outline')
        body+=''.join(roadmap(b,subject['name'],subject['slug']) for subject in y['subjects'])+'</details><p class="source-note">Books are reading recommendations; tap a row for guidance. Year grouping may vary by university. Check your syllabus.</p></div>'
        b.write_page(path,label+' BVSc Notes, Books & Course Outline',desc,body,[(label+' Course Outline',outline_url(year)),(label+' Road Map',path+'#road-map')]+[(subject['name'],path+'#'+subject['slug']) for subject in y['subjects']]);notes_page(b,y)

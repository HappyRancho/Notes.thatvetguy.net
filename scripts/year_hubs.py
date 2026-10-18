"""Four year hubs: books, a direct notes destination and a roadmap per subject."""
from html import escape as e
from pathlib import Path
import json,re
from library import slug,natural
ROOT=Path(__file__).resolve().parent.parent

def subject_books(b,books):
    if not books:return '<p class="year-book-empty">No book recommendation listed yet. Check your department’s prescribed practical manual.</p>'
    return '<ul class="year-book-list">'+''.join('<li><span class="rx-row-icon yellow" aria-hidden="true">'+b.icon('book')+'</span><div><strong>'+e(r['title'])+'</strong><span>'+e(r['author'])+'</span></div></li>' for r in books)+'</ul>'

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
    books=json.loads((ROOT/'data/book-recommendations.json').read_text())['books'];copy=json.loads((ROOT/'data/year-hub-microcopy.json').read_text())
    from homepage import subject_icon,CONTENT
    for y in b.LIBRARY['years']:
        year=y['year'];label=b.DATA['labels'][str(year)];path=f'/bvsc/year-{year}/'
        desc=f'{label} BVSc & AH books, topic-wise notes and study roadmaps, organised by subject. Start with your subject and get straight to the reading.'
        body=b.article_intro(label+' Books & Notes',desc,[('BVSc','/bvsc/')])
        body+='<p class="collection-meta">'+str(len(y['subjects']))+' subjects · '+str(y['count'])+' notes</p><p class="year-prescribed-note">Books are reading recommendations. Choose your department’s prescribed edition.</p><span id="books" class="anchor-alias"></span><div class="year-subject-sections">'
        for i,s in enumerate(y['subjects']):
            own=[r for r in books if r['year']==year and r['subject']==s['name']];ic,tone=subject_icon(s['name'])
            body+='<section class="year-subject-section" id="'+s['slug']+'"><header><span class="rx-row-icon '+tone+'" aria-hidden="true">'+b.icon(ic)+'</span><div><h2>'+e(s['name'])+'</h2><p>'+str(s['count'])+' '+('note' if s['count']==1 else 'notes')+'</p></div></header>'
            note_copy=str(s['count'])+' notes · browse by unit' if s['count'] else 'Collection in preparation'
            feature='<span class="year-notes-symbol" aria-hidden="true">'+b.icon('paper')+'</span><span class="year-notes-copy"><strong>Topic-wise notes</strong><small>'+note_copy+'</small></span>'+b.icon('arrow')
            body+='<div class="year-subject-notes">'+b.link(path+'notes/#'+s['slug'],feature,'year-notes-link')+'</div><h3>Recommended books</h3>'+subject_books(b,own)+roadmap(b,s['name'],s['slug'])+'</section>'
            if i==0:body+='<p class="year-margin-note">'+e(copy[str(year)])+'</p>'
        body+='</div><details class="syllabus" id="road-map"><summary>'+e(label)+' Road Map '+b.icon('map')+'</summary><ol class="topic-list">'+''.join('<li>'+e(step)+'</li>' for step in CONTENT['roadmaps'][str(year)]['steps'])+'</ol></details><p class="source-note">Year grouping may vary by university. Check your syllabus.</p></div>'
        b.write_page(path,label+' BVSc Books, Notes & Roadmaps',desc,body,[(s['name'],path+'#'+s['slug']) for s in y['subjects']]);notes_page(b,y)

"""Four year hubs: books, a direct notes destination and a roadmap per subject."""
from html import escape as e
from pathlib import Path
import json,re
from library import slug,natural,normal
ROOT=Path(__file__).resolve().parent.parent

def subject_books(b,books):
    if not books:return '<p class="year-book-empty">No book listed for this subject yet. Check your department’s prescribed reading.</p>'
    return '<ul class="year-book-list">'+''.join('<li data-row-search="'+e(normal(r['title']+' '+(r.get('author') or '')),quote=True)+'">'+b.link(r['page'],'<span class="rx-row-icon sky" aria-hidden="true">'+b.icon('book')+'</span><span class="year-book-copy"><strong>'+e(r['title'])+'</strong><span>'+e((r.get('author')+' · ' if r.get('author') else '')+r['access'])+'</span></span>'+b.icon('chevron'),'year-book-link')+'</li>' for r in books)+'</ul>'

def notes_page(b,y):
    from subject_pages import legacy_notes
    legacy_notes(b,y)

def index(b):
    from homepage import subject_icon
    from book_catalogue import books as book_registry
    books=book_registry()
    desc='BVSc & AH notes, TANUVAS material and recommended books, organised by professional year. Choose a year or open a subject directly.'
    body=b.article_intro('BVSc Notes & Books',desc)+'<div class="bvsc-year-sections">';items=[]
    for y in b.LIBRARY['years']:
        year=y['year'];label=b.DATA['labels'][str(year)];path=f'/bvsc/year-{year}/';tone=['yellow','peach','sky','mint'][year-1]
        body+='<section class="bvsc-year-section" id="year-'+str(year)+'"><header class="bvsc-year-heading"><span class="bvsc-year-number '+tone+'" aria-hidden="true">'+str(year)+'</span><div><h2>'+e(label)+'</h2><p>'+str(len(y['subjects']))+' subjects · '+str(y['count'])+' notes</p></div>'+b.link(path,'View year '+b.icon('arrow'),'bvsc-year-link')+'</header><div class="bvsc-subject-grid">'
        for subject in y['subjects']:
            ic,icon_tone=subject_icon(subject['name']);nbooks=sum({'year':year,'name':subject['name']} in r['subjects'] for r in books)
            meta=(str(nbooks)+' '+('book' if nbooks==1 else 'books')+' · ' if nbooks else '')+str(subject['count'])+' '+('note' if subject['count']==1 else 'notes')
            if not nbooks and not subject['count']:meta='Roadmap available'
            url=path+subject['slug']+'/';items.append((subject['name']+' · '+label,url))
            body+=b.link(url,'<span class="rx-row-icon '+icon_tone+'" aria-hidden="true">'+b.icon(ic)+'</span>'+b.icon('chevron')+'<h3>'+e(subject['name'])+'</h3><p>'+e(meta)+'</p>','bvsc-subject-tile')
        body+='</div></section>'
    body+='</div><p class="source-note bvsc-syllabus-note">Year grouping may vary by university. Check your syllabus.</p></div>'
    b.write_page('/bvsc/','BVSc Notes & Books',desc,body,items)

def render(b):
    from course_outlines import outline_url
    from subject_pages import year_nav,subject_tile,render as render_subject
    from homepage import CONTENT
    from book_catalogue import books as book_registry
    books=book_registry()
    for y in b.LIBRARY['years']:
        year=y['year'];label=b.DATA['labels'][str(year)];path=f'/bvsc/year-{year}/'
        desc=f'{label} BVSc & AH notes, TANUVAS material and recommended books. Pick a subject to start.'
        body=b.article_intro(label+' Notes & Books',desc,[('BVSc','/bvsc/')]).replace('container reading-page','container reading-page year-page year-directory',1)
        body+=year_nav(b,year)+'<div class="year-essentials">'
        body+=b.link(path+'roadmap/','<span class="rx-row-icon yellow">'+b.icon('map')+'</span><span><strong>'+label+' Roadmap</strong><small>Plan your year</small></span>'+b.icon('chevron'),'year-essential year-roadmap-cta').replace('<a ','<a id="road-map" ',1)
        body+=b.link(outline_url(year),'<span class="rx-row-icon peach">'+b.icon('paper')+'</span><span><strong>Course Outline</strong><small>Read the year syllabus</small></span>'+b.icon('chevron'),'year-essential year-outline-cta')+'</div>'
        body+='<section class="year-directory-section" id="books"><header><h2>Choose a subject</h2><p>'+str(len(y['subjects']))+' subjects · '+str(y['count'])+' resources</p></header><ul class="academic-subject-list">'+''.join(subject_tile(b,year,s,books) for s in y['subjects'])+'</ul></section>'
        body+='<p class="source-note">Year grouping may vary by university. Check your syllabus.</p></div>'
        b.write_page(path,label+' BVSc Notes, TANUVAS Material & Books',desc,body,[(s['name'],path+s['slug']+'/') for s in y['subjects']])
        for subject in y['subjects']:render_subject(b,year,subject,books)
        notes_page(b,y)
    from roadmaps import render as render_roadmaps
    render_roadmaps(b)

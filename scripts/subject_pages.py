"""One canonical subject page for books, topic notes and TANUVAS collections."""
from html import escape as e
import re
from library import slug,natural,normal
from course_outlines import outline_url

def url(year,subject):return f'/bvsc/year-{year}/'+slug(subject)+'/'

def year_nav(b,selected):
    return '<nav class="academic-year-nav" aria-label="Professional years">'+''.join('<a href="/bvsc/year-'+str(n)+'/"'+(' aria-current="page"' if n==selected else '')+'>'+b.DATA['labels'][str(n)]+'</a>' for n in range(1,5))+'</nav>'

def subject_tile(b,year,subject,books):
    from homepage import subject_icon
    name=subject['name'];ic,tone=subject_icon(name);rows=[b.CATALOGUE[r] for r in subject['resourceIds']];tanuvas=sum('tanuvas' in r['collections'] for r in rows);topics=len(rows)-tanuvas
    own=[r for r in books if r['year']==year and r['subject']==name]
    meta=(str(topics)+' topic '+('note' if topics==1 else 'notes'))+((' · '+str(tanuvas)+' TANUVAS') if tanuvas else '') if rows else 'Notes coming soon · course outline available'
    body='<span class="rx-row-icon '+tone+'" aria-hidden="true">'+b.icon(ic)+'</span><span class="academic-subject-copy"><strong>'+e(name)+'</strong><small>'+e(meta)+'</small>'+('<span>'+str(len(own))+' recommended '+('book' if len(own)==1 else 'books')+'</span>' if own else '')+'</span>'+b.icon('chevron')
    # The whole subject row is a single target; no nested buttons or duplicate links.
    return '<li id="'+subject['slug']+'">'+b.link(url(year,name),body,'academic-subject-card')+'</li>'

def groups(b,rows,subject,category):
    from library_views import group,empty
    if not rows:return '<p class="subject-source-note">No separate TANUVAS collection is listed for this subject yet.</p>' if category=='tanuvas' else empty(b,'Topic-wise notes coming soon')
    units=sorted({r['unit'] for r in rows},key=lambda u:(int(m[1]) if (m:=re.match(r'Units?\s+(\d+)',u,re.I)) else 100000,natural(u)))
    return ''.join(group(b,unit,[r for r in rows if r['unit']==unit],subject['slug']+('-tanuvas-' if category=='tanuvas' else '-')+slug(unit),i==0,level=3,filterkey=category) for i,unit in enumerate(units))

def render(b,year,subject,books):
    from year_hubs import subject_books
    from library_views import controls
    name=subject['name'];label=b.DATA['labels'][str(year)];path=url(year,name);guide=b.SUBJECTS[name];rows=[b.CATALOGUE[r] for r in subject['resourceIds']]
    tanuvas=[r for r in rows if 'tanuvas' in r['collections']];topics=[r for r in rows if 'tanuvas' not in r['collections']];own=[r for r in books if r['year']==year and r['subject']==name]
    description=guide['summary'].split('. ',1)[0]+'. '+f'Find {label} BVSc & AH topic-wise notes, TANUVAS material where available, course outlines and recommended reading in one place.'
    intro=f'Topic-wise notes and TANUVAS material for {label} BVSc & AH. Books and course outlines, all in one place.'
    body=b.article_intro(name,intro,[('BVSc','/bvsc/'),(label,f'/bvsc/year-{year}/')]).replace('container reading-page','container reading-page subject-page',1)
    body+='<nav class="subject-jump-links" aria-label="Subject resources">'+b.link('#notes',b.icon('paper')+'<span>Topic-wise Notes<small>'+str(len(topics))+' '+('resource' if len(topics)==1 else 'resources')+'</small></span>'+b.icon('arrow'),'subject-topic-jump')+b.link('#tanuvas',b.icon('book')+'<span>TANUVAS Notes<small>'+str(len(tanuvas))+' '+('resource' if len(tanuvas)==1 else 'resources')+'</small></span>'+b.icon('arrow'),'subject-tanuvas-jump')+'</nav>'
    body+='<div class="subject-outline-links">'+b.link(outline_url(year,name),b.icon('paper')+'Course Outline')+b.link('#books',b.icon('book')+'Recommended Books')+'</div>'
    if name=='Veterinary Biochemistry':body+='<p class="source-note">Biochemistry appears in the 1st Year outline PDF; it is grouped in 2nd Year here. Check your university’s syllabus.</p>'
    body+='<div class="filter-collection subject-notes-collection" data-filter-subjects>'+controls(b,[('topic','Topic-wise'),('tanuvas','TANUVAS')],subject['slug'],True)
    for ident,title,records,category,tone in [('notes','Topic-wise Notes',topics,'topic','sky'),('tanuvas','TANUVAS Notes',tanuvas,'tanuvas','mint')]:
        body+='<section class="subject-notes-block '+tone+'" data-subject-section id="'+ident+'"><header><span class="rx-row-icon '+tone+'">'+b.icon('paper' if ident=='notes' else 'book')+'</span><h2>'+title+'</h2><span class="subject-resource-count">'+str(len(records))+'</span></header>'
        if ident=='tanuvas' and records:body+='<p class="subject-source-note">Collection labels follow VetBVSc’s source pages. Older course codes may differ from your current syllabus.</p>'
        body+=groups(b,records,subject,category)+'</section>'
    body+='<p class="filter-empty" hidden>No notes match. '+b.link('/request-resource/','Request a resource')+'</p></div>'
    body+='<section class="subject-reading-section" id="books"><header><span class="rx-row-icon yellow">'+b.icon('book')+'</span><h2>Recommended Books</h2></header>'+subject_books(b,own)+'</section>'
    body+='<details class="subject-study-guide"><summary>What to cover '+b.icon('chevron')+'</summary><p>'+e(guide['summary'])+'</p><ul>'+''.join('<li>'+e(t)+'</li>' for t in guide['topics'])+'</ul><p>'+e(guide['studyTip'])+'</p></details>'
    body+='<nav class="subject-bottom-nav" aria-label="More study material">'+b.link(f'/bvsc/year-{year}/','All '+label+' subjects '+b.icon('arrow'))+b.link(f'/bvsc/year-{year}/roadmap/','Year roadmap '+b.icon('map'))+'<button type="button" class="studied-button js-only" data-studied="'+subject['slug']+'" aria-pressed="false">'+b.icon('check')+'<span>Mark as studied</span></button></nav></div>'
    b.write_page(path,name+' Notes, TANUVAS Material & Books',description,body,[(r['title'],r['url']) for r in rows])

def legacy_notes(b,y):
    """Keep old year-note hashes useful without duplicating canonical file rows."""
    year=y['year'];label=b.DATA['labels'][str(year)];path=f'/bvsc/year-{year}/notes/'
    desc=f'Choose a {label} subject to read topic-wise notes and TANUVAS material. Each subject now has its own notes and books page.'
    body=b.article_intro(label+' Notes by Subject',desc,[('BVSc','/bvsc/'),(label,f'/bvsc/year-{year}/')])+'<div class="legacy-notes-gateway"><ul class="academic-subject-list">'
    for s in y['subjects']:
        target=url(year,s['name']);rows=[b.CATALOGUE[r] for r in s['resourceIds']]
        anchors={s['slug']:target+'#notes'}
        for r in rows:
            anchors['file-'+r['id']]=r['permalink']
            anchors.setdefault(s['slug']+'-'+slug(r['unit']),target+'#'+s['slug']+('-tanuvas-' if 'tanuvas' in r['collections'] else '-')+slug(r['unit']))
            for alias in r['duplicateIds']+[v['id'] for v in r['variants'][1:]]:anchors['file-'+alias]=r['permalink']
        body+='<li>'+''.join('<span class="anchor-alias" id="'+ident+'" data-destination="'+e(dest,quote=True)+'"></span>' for ident,dest in anchors.items())+b.link(target,'<span><strong>'+e(s['name'])+'</strong><small>'+str(s['count'])+' '+('resource' if s['count']==1 else 'resources')+'</small></span>'+b.icon('chevron'),'academic-subject-card')+'</li>'
    body+='</ul></div></div>'
    b.write_page(path,label+' Veterinary Notes by Subject',desc,body,noindex=True)

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
    own=[r for r in books if {'year':year,'name':name} in r['subjects']]
    meta=(str(topics)+' topic '+('note' if topics==1 else 'notes'))+((' · '+str(tanuvas)+' TANUVAS') if tanuvas else '') if rows else 'Notes coming soon · course outline available'
    body='<span class="rx-row-icon '+tone+'" aria-hidden="true">'+b.icon(ic)+'</span><span class="academic-subject-copy"><strong>'+e(name)+'</strong><small>'+e(meta)+'</small>'+('<span>'+str(len(own))+' '+('book' if len(own)==1 else 'books')+'</span>' if own else '')+'</span>'+b.icon('chevron')
    # The whole subject row is a single target; no nested buttons or duplicate links.
    return '<li id="'+subject['slug']+'">'+b.link(url(year,name),body,'academic-subject-card')+'</li>'

def unit_parts(unit):
    match=re.match(r'(Units?\s+\d+(?:[–—-]\d+)?)\s*[–—-]\s*(.*)',unit,re.I)
    return (match[1],match[2]) if match else ('',unit)

def groups(b,rows,subject,category):
    from library_views import chunks,empty,file_card
    if not rows:return empty(b,'Notes coming soon')
    units=sorted({r['unit'] for r in rows},key=lambda u:(int(m[1]) if (m:=re.match(r'Units?\s+(\d+)',u,re.I)) else 100000,natural(u)))
    if category=='tanuvas':
        # One Open action per file; a single-file course is not another accordion.
        seen=set()
        def course_row(builder,record):
            unit=record['unit'];alias='' if unit in seen else '<span class="anchor-alias" id="'+subject['slug']+'-tanuvas-'+slug(unit)+'"></span>'
            seen.add(unit)
            return alias+file_card(builder,record)
        return chunks(b,sorted(rows,key=lambda r:natural(r['title'])),course_row)
    result=[]
    for i,unit in enumerate(units):
        own=[r for r in rows if r['unit']==unit];code,title=unit_parts(unit);ident=subject['slug']+'-'+slug(unit)
        heading=('<span class="reader-unit-label">'+e(code)+'</span> ' if code else '')+'<span>'+e(title)+'</span>'
        result.append('<details class="resource-group reader-unit" id="'+ident+'" data-group="topic"'+(' open' if i==0 else '')+'><summary><h3>'+heading+'</h3><span class="group-count">'+str(len(own))+'<span class="sr-only"> notes</span></span>'+b.icon('chevron')+'</summary><div class="group-body">'+chunks(b,own)+'</div></details>')
    return ''.join(result)

def render(b,year,subject,books):
    from year_hubs import subject_books
    from library_views import empty
    name=subject['name'];label=b.DATA['labels'][str(year)];path=url(year,name);guide=b.SUBJECTS[name];rows=[b.CATALOGUE[r] for r in subject['resourceIds']]
    tanuvas=[r for r in rows if 'tanuvas' in r['collections']];topics=[r for r in rows if 'tanuvas' not in r['collections']];own=[r for r in books if {'year':year,'name':name} in r['subjects']]
    description=guide['summary'].split('. ',1)[0]+'. '+f'Find {label} BVSc & AH topic-wise notes, TANUVAS material where available, course outlines and recommended reading in one place.'
    intro=f'Topic-wise notes, TANUVAS material and recommended reading for {label} BVSc & AH. Choose a collection below.'
    body=b.article_intro(name,intro,[('BVSc','/bvsc/'),(label,f'/bvsc/year-{year}/')]).replace('container reading-page','container reading-page subject-page',1)
    body+='<div class="subject-meta"><span>'+label+' · '+str(len(rows))+' resources</span><div class="subject-outline-links">'+b.link(outline_url(year,name),b.icon('paper')+'Course Outline')+'</div></div>'
    body+='<div class="subject-reader" data-subject-reader><nav class="reader-tabs" aria-label="Subject collections">'+''.join(b.link('#'+ident,title,'reader-tab'+(' is-selected' if ident=='notes' else '')).replace('<a ','<a id="reader-tab-'+ident+'" data-reader-tab="'+ident+'" ',1) for ident,title in [('notes','Topic-wise'),('tanuvas','TANUVAS'),('books','Books')])+'</nav>'
    body+='<div class="reader-search js-only"'+(' hidden' if len(topics)<12 else '')+'><label class="sr-only" for="'+subject['slug']+'-query">Find a resource in the selected collection</label><div class="inline-search">'+b.icon('search')+'<input id="'+subject['slug']+'-query" class="collection-query" type="search" placeholder="Find a topic or note…" autocomplete="off"></div><span class="reader-search-status sr-only" role="status"></span></div>'
    for ident,title,records,category in [('notes','Topic-wise Notes',topics,'topic'),('tanuvas','TANUVAS Notes',tanuvas,'tanuvas')]:
        units=len({r['unit'] for r in records});meta=(str(units)+' '+('unit' if units==1 else 'units')+' · ' if ident=='notes' and records else '')+str(len(records))+' '+('note' if len(records)==1 else 'notes')
        body+='<section class="reader-panel" data-subject-panel data-selected="'+str(ident=='notes').lower()+'" id="'+ident+'"><header class="reader-panel-heading"><h2>'+title+'</h2><p>'+meta+'</p></header>'+groups(b,records,subject,category)
        if ident=='tanuvas' and records:body+='<details class="reader-source-note"><summary>About these notes '+b.icon('chevron')+'</summary><p>TANUVAS material linked through VetBVSc. Course codes come from the source collection and may differ from your current syllabus. Credit remains with the original authors.</p></details>'
        body+='</section>'
    body+='<section class="reader-panel" data-subject-panel data-selected="false" id="books"><header class="reader-panel-heading"><h2>Books &amp; Recommended Reading</h2><p>'+str(len(own))+' '+('book' if len(own)==1 else 'books')+'</p></header>'+('<p class="reader-book-note">Open a book for its details, cover and available download.</p>' if own else '')+subject_books(b,own)+b.link('/books/','Browse all books '+b.icon('arrow'),'book-library-link')+'</section>'
    body+='<div class="reader-empty filter-empty" hidden><strong>No notes found.</strong><p>Try a shorter title or another collection.</p>'+b.link('/request-resource/','Request a resource '+b.icon('arrow'),'button secondary')+'</div></div>'
    body+='<details class="subject-study-guide"><summary>Course focus & study tips '+b.icon('chevron')+'</summary><p>'+e(guide['summary'])+'</p><ul>'+''.join('<li>'+e(t)+'</li>' for t in guide['topics'])+'</ul><p>'+e(guide['studyTip'])+'</p>'
    if name=='Veterinary Biochemistry':body+='<p>Biochemistry appears in the 1st Year outline PDF; it is grouped in 2nd Year here. Check your university’s syllabus.</p>'
    body+='</details><nav class="subject-bottom-nav" aria-label="More study material">'+b.link(f'/bvsc/year-{year}/','All '+label+' subjects '+b.icon('arrow'))+b.link(f'/bvsc/year-{year}/roadmap/','Year roadmap '+b.icon('map'))+'<button type="button" class="studied-button js-only" data-studied="'+subject['slug']+'" aria-pressed="false">'+b.icon('check')+'<span>Mark as studied</span></button></nav></div>'
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

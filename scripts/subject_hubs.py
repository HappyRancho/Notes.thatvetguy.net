"""Subject-only Notes and Books hubs following the approved Rx Notes sketch."""
from html import escape as e
from library import normal
from subject_pages import url,groups
from syllabus_pages import checklist_url
from practical_catalogue import vault_url

def note_tile(b,ident,title,detail,ic,tone,available):
    content='<span class="rx-row-icon '+tone+'">'+b.icon(ic)+'</span><strong>'+title+'</strong><small>'+detail+'</small>'
    if not available:return '<div class="subject-note-option is-unavailable" aria-disabled="true">'+content+'<span class="subject-soon">Coming soon</span></div>'
    return b.link('#'+ident,content+b.icon('chevron'),'subject-note-option').replace('<a ','<a data-note-option="'+ident+'" aria-controls="'+ident+'" aria-expanded="false" ',1)

def book_card(b,book):
    cover=book.get('cover');label='Reference cover' if cover and cover['kind']=='reference-cover' else 'Source preview' if cover else 'Cover unavailable'
    art='<img src="'+cover['path']+'" width="'+str(cover['width'])+'" height="'+str(cover['height'])+'" alt="" loading="lazy" decoding="async">' if cover else b.icon('book')
    content='<span class="subject-book-art" aria-hidden="true">'+art+'</span><span class="subject-book-art-label">'+label+'</span><strong>'+e(book['title'])+'</strong>'+('<small>'+e(book['author'])+'</small>' if book.get('author') else '')+'<span class="subject-book-access">'+('Reading guide' if not book['primaryUrl'] else 'View book')+b.icon('chevron')+'</span>'
    return '<article class="subject-book-card" data-row-search="'+e(normal(book['title']+' '+(book.get('author') or '')),quote=True)+'">'+b.link(book['page'],content,'year-book-link')+'</article>'

def render(b,year,subject,books):
    name=subject['name'];label=b.DATA['labels'][str(year)];path=url(year,name);guide=b.SUBJECTS[name];rows=[b.CATALOGUE[r] for r in subject['resourceIds']]
    tanuvas=[r for r in rows if 'tanuvas' in r['collections']];topics=[r for r in rows if 'tanuvas' not in r['collections']];own=[r for r in books if {'year':year,'name':name} in r['subjects']]
    description=f'{name} for {label} BVSc & AH: a unit-wise syllabus checklist, topic-wise notes, TANUVAS notes and subject books with available downloads.'
    intro=guide['summary'].split('. ',1)[0]+'.'
    body=b.article_intro(name,intro,[('BVSc','/bvsc/'),(label,f'/bvsc/year-{year}/')]).replace('container reading-page','container reading-page subject-page subject-hub',1)
    syllabus=b.link(checklist_url(year,name),'<span class="rx-row-icon sky">'+b.icon('check')+'</span><span><strong>Syllabus Checklist</strong><small>Unit by unit. One tick at a time.</small></span>'+b.icon('chevron'),'subject-syllabus-link')
    body=body.replace('</header>',syllabus+'</header>',1)
    body+='<section class="subject-reader subject-notes-card" data-subject-reader aria-labelledby="notes-title"><header class="subject-card-heading"><span class="subject-rx" aria-hidden="true">℞</span><h2 id="notes-title">Notes</h2><span>'+str(len(rows))+' '+('note' if len(rows)==1 else 'notes')+'</span></header><div class="subject-notes-options">'
    body+=note_tile(b,'notes','Topic-wise Notes',str(len(topics))+' '+('note' if len(topics)==1 else 'notes'),'paper','sky',bool(topics))
    body+=note_tile(b,'tanuvas','Unit-wise Notes','TANUVAS · '+str(len(tanuvas))+' '+('collection' if len(tanuvas)==1 else 'collections'),'book','mint',bool(tanuvas))+'</div>'
    body+=b.link(vault_url(year,name),'<span class="rx-row-icon peach">'+b.icon('flask')+'</span><span><strong>Practical Vault</strong><small>Manuals, slides &amp; practical collections</small></span>'+b.icon('chevron'),'subject-practical-link')
    body+='<div class="reader-search js-only" hidden><label class="sr-only" for="'+subject['slug']+'-query">Find a note in the selected collection</label><div class="inline-search">'+b.icon('search')+'<input id="'+subject['slug']+'-query" class="collection-query" type="search" placeholder="Find a topic or note…" autocomplete="off"></div><span class="reader-search-status sr-only" role="status"></span></div>'
    for ident,title,records,category in [('notes','Topic-wise Notes',topics,'topic'),('tanuvas','TANUVAS Notes',tanuvas,'tanuvas')]:
        body+='<details class="reader-panel" data-subject-panel data-selected="false" id="'+ident+'"><summary class="reader-panel-heading"><h3>'+title+'</h3><span>'+str(len(records))+' '+('note' if len(records)==1 else 'notes')+'</span>'+b.icon('chevron')+'</summary>'+groups(b,records,subject,category,level=4)
        if ident=='tanuvas' and records:body+='<p class="reader-source-note">Course codes follow the source collection and may differ from your current syllabus. Credit remains with the original authors.</p>'
        body+='</details>'
    body+='<div class="reader-empty filter-empty" hidden><strong>No notes found.</strong><p>Try a shorter title or another collection.</p>'+b.link('/request-resource/','Request a resource '+b.icon('arrow'),'button secondary')+'</div></section>'
    body+='<section class="subject-books-card" id="books" aria-labelledby="subject-books-title"><header class="subject-card-heading"><span class="subject-rx" aria-hidden="true">℞</span><h2 id="subject-books-title">Books</h2><span>'+str(len(own))+' '+('book' if len(own)==1 else 'books')+'</span></header>'
    if own:
        if len(own)>12:body+='<div class="subject-books-search js-only"><label for="subject-book-query" class="sr-only">Find a book or author</label><input id="subject-book-query" type="search" placeholder="Find a book or author…" autocomplete="off"><span class="sr-only" role="status" id="subject-book-status"></span></div>'
        body+='<div class="subject-book-grid">'+''.join(book_card(b,book) for book in own[:6])+'</div>'
        if len(own)>6:body+='<details class="subject-more-books"><summary>Show '+str(len(own)-6)+' more '+('book' if len(own)-6==1 else 'books')+b.icon('chevron')+'</summary><div class="subject-book-grid">'+''.join(book_card(b,book) for book in own[6:])+'</div></details>'
        body+='<p class="subject-books-empty" hidden>No books match that title or author.</p>'
    else:body+='<p class="subject-book-unavailable">No book listed for this subject yet.</p>'+b.link('/request-resource/','Request a book '+b.icon('arrow'),'book-library-link')
    body+='</section><details class="subject-study-guide"><summary>Course focus &amp; study tips '+b.icon('chevron')+'</summary><p>'+e(guide['summary'])+'</p><ul>'+''.join('<li>'+e(t)+'</li>' for t in guide['topics'])+'</ul><p>'+e(guide['studyTip'])+'</p></details>'
    body+='<nav class="subject-bottom-nav" aria-label="More study material">'+b.link(f'/bvsc/year-{year}/','All '+label+' subjects '+b.icon('arrow'))+'<button type="button" class="studied-button js-only" data-studied="'+subject['slug']+'" aria-pressed="false">'+b.icon('check')+'<span>Mark as studied</span></button></nav></div>'
    b.write_page(path,name+' Notes, TANUVAS Material & Books',description,body,[(r['title'],r['url']) for r in rows])

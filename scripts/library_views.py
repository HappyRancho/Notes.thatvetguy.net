"""One job per page: years, subjects, then bounded file groups."""
from html import escape as e
from collections import Counter
from library import KINDS,natural,slug,normal
from site_shell import year_tiles

def count(n,word='resource'):return f'{n:,} {word}'+('' if n==1 else 's')
def keep_complete_resource(r):
    """Keep subject-level material in the public subject reader.

    Topic slide decks and mixed PPT/PDF lesson folders remain in the source
    catalogue, but are intentionally omitted from the clean subject view.
    """
    path=(r.get('path') or '').lower().replace('_',' ')
    if r.get('kind')=='presentation':return False
    if r.get('format') in ('PDF','PPT'):
        folders={part.strip() for part in path.split('/')}
        if folders.intersection({'ppt','ppts','lecture slides','ppt & pdf','ppt and pdf'}):return False
        if 'slide' in (r.get('title') or '').lower():return False
    return True
def size_label(n):
    if n is None:return 'Size unavailable'
    return f'{n/1_000_000:.1f} MB' if n>=1_000_000 else f'{n/1000:.0f} KB'
def empty(b,text='Coming soon'):
    return '<div class="empty-state"><strong>'+e(text)+'</strong><p>'+e(b.MICROCOPY['empty'][0])+'</p>'+b.link('/request-resource/','Request a resource '+b.icon('arrow'),'button secondary')+'</div>'
def matching(b,category):return [r for r in b.RECORDS if category in r['collections'] and keep_complete_resource(r)]
def file_card(b,r):
    rid=r['id'];title=e(r['title']);original=e(r['name'],quote=True)
    formats=''.join(b.link(v['url'],e(v['extension'])+' '+b.icon('external'),'format-link') for v in r['variants'])
    download=''.join(b.link(v['download'],'Download '+e(v['format']),'text-link') for v in r['variants'] if v['download'])
    updated='<time datetime="'+e(r['updated'],quote=True)+'">'+e(r['updated'][:10])+'</time>' if r['updated'] else 'Unknown'
    credit='<p>Source credit: '+e(r['sourceCredit'])+'</p>' if r['sourceCredit'] else ''
    new='<span class="new-sticker">NEW</span>' if r['new'] else ''
    aliases=''.join('<span id="file-'+a+'" class="anchor-alias"></span>' for a in r['duplicateIds']+[v['id'] for v in r['variants'][1:]])
    return aliases+'<article class="file-row" id="file-'+rid+'" data-resource-id="'+rid+'" data-row-search="'+e(normal(r['title']+' '+r['path']),quote=True)+'"><span class="format-icon format-'+r['format'].lower()+'" aria-hidden="true">'+e(r['format'])+'</span><div class="file-title"><span title="'+original+'">'+title+'</span>'+new+'<small>'+size_label(r['size'])+'</small></div>'+b.link(r['url'],'<span class="open-label">Open</span>'+b.icon('external')+'<span class="sr-only"> '+title+'</span>','file-open')+'<button class="icon-button save-button js-only" type="button" data-bookmark="'+rid+'" aria-label="Save '+e(r['title'],quote=True)+'" aria-pressed="false">'+b.icon('book')+'</button><details class="file-details"><summary aria-label="Details and report for '+e(r['title'],quote=True)+'">'+b.icon('menu')+'</summary><div class="file-detail-body"><p>Updated '+updated+' · '+size_label(r['size'])+'</p><div class="format-links">'+formats+'</div>'+credit+'<div class="detail-links">'+download+b.link('/request-resource/?file='+rid+'#report','Report an error / takedown','text-link')+'</div></div></details></article>'
def teaser(b,r):
    return '<div class="teaser" data-row-search="'+e(normal(r['title']+' '+(r['subject'] or '')+' '+r['path']),quote=True)+'">'+b.link(r['permalink'],'<span class="format-icon" aria-hidden="true">'+e(r['format'])+'</span><span><strong>'+e(r['title'])+'</strong><small>'+e(r['subject'] or 'Year '+str(r['year'])+' extras')+' · '+e(r['type'])+'</small></span>'+b.icon('arrow'))+'</div>'
def chunks(b,rows,render=file_card,limit=30):
    if not rows:return ''
    html='<div class="file-list">'+''.join(render(b,r) for r in rows[:limit])+'</div>'
    if len(rows)>limit:html+='<details class="page-chunk"><summary>Show '+str(min(30,len(rows)-limit))+' more <span>'+str(len(rows)-limit)+' remaining</span></summary>'+chunks(b,rows[limit:],render,30)+'</details>'
    return html
def controls(b,kinds,ident='file',subjects=False):
    filters=[('all','All')]+[(k,t) for k,t in kinds]
    return '<div class="library-controls js-only"><label class="sr-only" for="'+ident+'-query">Search this collection</label><div class="inline-search">'+b.icon('search')+'<input id="'+ident+'-query" class="collection-query" type="search" placeholder="Search this '+('collection' if subjects else 'subject')+'…" autocomplete="off"></div><div class="filter-chips" aria-label="Filter resources">'+''.join('<button type="button" data-filter="'+k+'" aria-pressed="'+('true' if k=='all' else 'false')+'">'+t+'</button>' for k,t in filters)+'</div><p class="filter-status sr-only" role="status"></p></div>'
def group(b,title,rows,ident,opened=False,render=file_card,level=2,filterkey=None):
    return '<details class="resource-group" id="'+ident+'" data-group="'+(filterkey or ident)+'"'+(' open' if opened else '')+'><summary><h'+str(level)+'>'+e(title)+'</h'+str(level)+'><span class="group-count">'+str(len(rows))+'</span>'+b.icon('arrow')+'</summary><div class="group-body">'+chunks(b,rows,render)+'</div></details>'
def subject_page(b,y,s):
    year=y['year'];name=s['name'];path='/bvsc/year-'+str(year)+'/'+s['slug']+'/'
    rows=[b.CATALOGUE[r] for r in s['resourceIds'] if r in b.CATALOGUE and keep_complete_resource(b.CATALOGUE[r])];summary=b.SUBJECTS[name]['summary']
    intro=name+' notes, books and revision material for BVSc & AH. Choose a topic below, or search within this subject.'
    body=b.article_intro(name,intro,[('BVSc','/bvsc/'),(b.DATA['labels'][str(year)],'/bvsc/year-'+str(year)+'/')])
    body+='<div class="subject-toolbar"><p>'+count(len(rows))+' · '+b.DATA['labels'][str(year)]+'</p><button type="button" class="studied-button js-only" data-studied="'+s['slug']+'" aria-pressed="false">'+b.icon('check')+'<span>Mark as studied</span></button></div>'
    body+='<div class="filter-collection">'+controls(b,[(k,v) for k,v in KINDS.items() if k not in ['images','presentation'] and any(r['kind']==k for r in rows)])
    first=True
    for kind,title in KINDS.items():
        if kind=='presentation':continue
        own=[r for r in rows if r['kind']==kind]
        if not own:continue
        body+=group(b,title,own,slug(title),first,filterkey='other' if kind=='images' else kind);first=False
    if not rows:body+=empty(b)
    body+='<p class="filter-empty" hidden>No resources match. '+b.link('/request-resource/','Request a resource')+'</p></div>'
    body+='<details class="syllabus"><summary>What to revise in this subject '+b.icon('arrow')+'</summary><p>'+e(summary)+'</p><ul>'+''.join('<li>'+e(t)+'</li>' for t in b.SUBJECTS[name]['topics'])+'</ul><p>'+e(b.SUBJECTS[name]['studyTip'])+'</p></details>'
    body+='<section class="related-section"><h2>Keep the connections.</h2><div class="related-links">'+''.join(b.link('/bvsc/'+slug(n)+'/',e(n)+b.icon('arrow')) for n in b.SUBJECTS[name]['related'])+'</div></section></div>'
    b.write_page(path,name+' · '+b.DATA['labels'][str(year)],summary,body,[(r['title'],r['url']) for r in rows])
def overview(b):
    desc=b.geo.META['/bvsc/']['summary'];body=b.article_intro('BVSc Notes & Books',desc)+year_tiles(b)+'<p class="source-note">Year grouping may vary by university. Check your syllabus. Counts combine alternate formats and photo sets into single resources.</p></div>'
    b.write_page('/bvsc/','BVSc Notes & Books',desc,body,[(b.DATA['labels'][str(y['year'])],'/bvsc/year-'+str(y['year'])+'/') for y in b.LIBRARY['years']])
    for y in b.LIBRARY['years']:
        year=y['year'];path='/bvsc/year-'+str(year)+'/'
        desc=f'Notes, books and practical material for {b.DATA["labels"][str(year)]} BVSc & AH. Choose a subject to find your next read.'
        body=b.article_intro(b.DATA['labels'][str(year)]+' Resources',desc,[('BVSc','/bvsc/')])
        body+='<p class="collection-meta">'+str(len(y['subjects']))+' subjects · '+count(y['count'])+'</p><div class="subject-grid year-'+str(year)+'">'
        for s in y['subjects']:
            chips=' · '.join(KINDS[k]+' '+str(v) for k,v in s['groups'].items())
            from homepage import subject_icon
            ic,tone=subject_icon(s['name'])
            content='<span class="rx-row-icon '+tone+'">'+b.icon(ic)+'</span><span><h2>'+e(s['name'])+'</h2><p class="kind-counts">'+(count(s['count'])+' · notes &amp; books' if chips else 'Coming soon')+'</p></span>'+b.icon('chevron')
            body+=b.link(path+s['slug']+'/',content,'subject-card') if s['count'] else '<article class="subject-card unavailable" aria-label="'+e(s['name'])+' — coming soon">'+content+'</article>'
            subject_page(b,y,s)
        body+='</div>'
        if y['extras']:
            body+='<section class="extras-section" id="extras"><h2>A few extras.</h2><p>These resources don’t yet have a confirmed subject.</p>'+group(b,'Extras', [b.CATALOGUE[r] for r in y['extras']], 'year-extras',False,level=3)+'</section>'
        from homepage import CONTENT
        body+='<details class="syllabus" id="road-map"><summary>'+e(b.DATA['labels'][str(year)])+' Road Map '+b.icon('map')+'</summary><ol class="topic-list">'+''.join('<li>'+e(step)+'</li>' for step in CONTENT['roadmaps'][str(year)]['steps'])+'</ol></details>'
        body+='<p class="source-note">Year grouping may vary by university. Check your syllabus.</p></div>'
        b.write_page(path,b.DATA['labels'][str(year)]+' BVSc Notes & Books',desc,body,[(s['name'],path+s['slug']+'/') for s in y['subjects']])
def guides(b):
    for name,m in b.SUBJECTS.items():
        path='/bvsc/'+slug(name)+'/';owner='/bvsc/year-'+str(m['year'])+'/'+slug(name)+'/'
        body=b.article_intro(name,m['summary'],[('BVSc','/bvsc/')])+b.link(owner,'Read '+e(name)+' resources '+b.icon('arrow'),'button')+'<section class="content-section"><h2>Your revision outline</h2><ul class="topic-list">'+''.join('<li>'+e(t)+'</li>' for t in m['topics'])+'</ul><p>'+e(m['studyTip'])+'</p></section></div>'
        b.write_page(path,name,m['summary'],body,[(name+' resources',owner)])
def collections(b):
    from homepage import tabs,panel
    desc=b.geo.META['/objective/']['summary'];body=b.article_intro('Objective Resources',desc)
    rows=matching(b,'objective-questions');subjects=sorted({r['subject'] for r in rows if r['subject']})
    books=matching(b,'objective-books')
    book_body='<section id="books"><h2>Objective Books</h2>'+chunks(b,books,teaser)+'</section>'
    bank_body='<section class="pyq-state" id="icar-pyq"><div><h2>ICAR PYQ Question Bank</h2><p>Coming soon. Know a paper we should add?</p></div>'+b.link('/request-resource/?collection=icar-pyq','Request a paper '+b.icon('arrow'),'text-link')+'</section>'
    bank_body+='<section id="subject-wise"><h2>Subject-wise Objective Questions</h2><div class="filter-collection">'+controls(b,[(slug(s),s.replace('Veterinary ','')) for s in subjects],'objective',True)
    for i,s in enumerate(subjects):bank_body+=group(b,s,[r for r in rows if r['subject']==s],slug(s),i==0,teaser,3)
    bank_body+='<p class="filter-empty" hidden>No resources match. '+b.link('/request-resource/','Request a resource')+'</p></div></section>'
    body+='<section class="content-section" data-home-tabs>'+tabs('objective-page',[('Objective Notes','/objective/#books'),('Question Banks','/objective/#subject-wise')])+panel('objective-page',0,book_body)+panel('objective-page',1,bank_body)+'</section></div>'
    b.write_page('/objective/','Objective Resources',desc,body,[(r['title'],r['permalink']) for r in rows+books])
    desc=b.geo.META['/clinical/']['summary'];body=b.article_intro('Clinical Resources',desc)+'<p class="clinical-callout" role="note">For study, not prescribing. Verify the species, dose and current clinical guidance before treating a patient.</p>'+b.section_aside('clinical')
    body+='<section class="content-section" id="handbooks"><h2>Handbooks</h2>'+chunks(b,matching(b,'handbooks'),teaser)+'</section>'
    rows=[r for r in matching(b,'drug-index') if keep_complete_resource(r)];pharm='/bvsc/year-3/veterinary-pharmacology-and-toxicology/'
    body+='<section class="content-section" id="drug-index"><h2>Drug & Pharmacology notes</h2><p>Start with these topics, then explore the full subject.</p><div class="file-list">'+''.join(teaser(b,r) for r in rows[:12])+'</div>'+b.link(pharm,'See all Pharmacology resources '+b.icon('arrow'),'button secondary')+'</section>'
    body+='<section class="content-section" id="other-resources"><h2>Go straight to the subject.</h2><div class="clinical-subjects">'
    for y,name in [(2,'Veterinary Pathology'),(4,'Veterinary Medicine'),(4,'Veterinary Surgery and Radiology'),(3,'Veterinary Pharmacology and Toxicology')]:body+=b.link('/bvsc/year-'+str(y)+'/'+slug(name)+'/',b.icon('cross')+'<span>'+name+'</span>'+b.icon('arrow'),'subject-shortcut')
    body+='</div></section></div>'
    b.write_page('/clinical/','Clinical Resources',desc,body,[(r['title'],r['permalink']) for r in matching(b,'handbooks')+rows[:12]])
def tools(b):
    body=b.article_intro('Tips & Tools for Vet Study',b.geo.META['/study-tools/']['summary'])
    guides=[('ai-guide','Use of AI for Vet Study',[('Start with your outline','Ask AI to organise a topic list or suggest a presentation structure. Compare the result with your syllabus and original notes.'),('Check before you learn','Verify veterinary facts and citations. A fluent answer can still be wrong; AI output is not a prescribing reference.'),('Make the explanation yours','Explain the topic without looking at the answer. Rewrite it in your own words and credit your sources.')]),('free-apps','Useful Free Apps',[('Zotero','Keep reading references together. Check each citation against its original source.'),('LibreOffice','Prepare notes, tables and presentations. Keep an editable copy as well as a PDF.'),('Your PDF reader','Use bookmarks, annotations and text search. Keep essential reading in a clearly named offline folder.')]),('useful-tools','Useful Study Tools',[('A document scanner','Scan only material you have permission to copy. Check every page for legibility before sharing.'),('A simple folder system','Try Year / Subject / Notes or Books. A useful filename saves a surprising amount of searching.'),('A reference checklist','Record the author, edition, species and date where relevant. A saved file still needs context.')])]
    from homepage import CONTENT,tabs,panel,row
    tool_rows='<span id="tools" class="anchor-alias"></span>'
    for i,(key,title,steps) in enumerate(guides):
        ic,tone=[('spark','purple'),('phone','mint'),('book','peach')][i]
        tool_rows+='<details class="guide-section" id="'+key+'"'+(' open' if i==0 else '')+'><summary><span class="rx-row-icon '+tone+'">'+b.icon(ic)+'</span><h2>'+title+'</h2>'+b.icon('chevron')+'</summary><div class="group-body"><ol class="guide-steps">'+''.join('<li><h3>'+e(t)+'</h3><p>'+e(d)+'</p></li>' for t,d in steps)+'</ol></div></details>'
    tip_rows='<section id="tips"><h2 class="sr-only">Year Roadmaps</h2><div class="rx-row-drawer">'+''.join(row(CONTENT['tips'][y-1]['title'],'/bvsc/year-'+str(y)+'/#road-map','map',['yellow','peach','sky','mint'][y-1]) for y in range(1,5))+'</div></section>'
    body+='<section class="content-section" data-home-tabs>'+tabs('study-page',[('Tools','/study-tools/#tools'),('Tips','/study-tools/#tips')])+panel('study-page',0,tool_rows)+panel('study-page',1,tip_rows)+'</section></div>'
    b.write_page('/study-tools/','Tips & Tools for Vet Study',b.geo.META['/study-tools/']['summary'],body,[(t,b.ROUTES[k]) for k,t,_ in guides])

def other(b):
    body=b.article_intro('About Notes.ThatVetGuy',b.geo.META['/about/']['summary'])+'<section class="content-section prose"><h2>A useful place to start.</h2><p>Pick your professional year, find a subject and get to the reading. Notes.ThatVetGuy brings notes, books and practical material together for veterinary students.</p><h2>People behind the pages</h2><p>Site guidance and summaries are by Dr. Chirag Patidar, BVSc & AH, MVSc. Linked materials retain their original authorship. Inclusion does not imply medical review or ownership.</p><h2>Help the next student</h2><p>A missing topic, a broken file or a credit that needs correcting: tell us so the library can get better.</p>'+b.link('/request-resource/','Request or report a resource '+b.icon('arrow'),'button secondary')+'</section></div>'
    b.write_page('/about/','About Notes.ThatVetGuy',b.geo.META['/about/']['summary'],body)
    body=b.article_intro('Can’t find what you need?',b.geo.META['/request-resource/']['summary'])+b.section_aside('request')+'<section class="content-section prose"><h2>Tell us what would help.</h2><p>Include the topic, subject, year and edition if relevant.</p><label for="request-file-id">File ID, if reporting a file</label><input id="request-file-id" class="request-input" name="file" type="text" autocomplete="off"><p id="request-context" role="status"></p>'+b.link('mailto:contact@thatvetguy.net?subject=Resource%20request','Email your request '+b.icon('arrow'),'button request-email')+'<p><!--email_off-->You can also copy <strong>contact@thatvetguy.net</strong> into your email app.<!--/email_off--></p></section>'
    for ident,title,text in [('contact','Contact','Send your question to contact@thatvetguy.net.'),('contribute','Contribute','Send the title, subject and original source credit. Share only material you have permission to contribute.'),('report','Report an error / takedown','Include the file ID or page URL, the issue and your contact details. For a takedown request, explain your connection to the material.')]:body+='<section class="content-section prose" id="'+ident+'"><h2>'+title+'</h2><p><!--email_off-->'+text+'<!--/email_off--></p></section>'
    b.write_page('/request-resource/','Request a Resource',b.geo.META['/request-resource/']['summary'],body+'</div>')
    body=b.article_intro('Find your next read.',b.geo.META['/search/']['summary'])+b.search_form(True)+'<div id="page-results"></div><section class="content-section preset-results"><h2>Start with a topic.</h2><nav class="preset-links" aria-label="Suggested searches">'+''.join(b.link('/search/#preset-'+a,t,'filter-link') for a,t in [('pharmacology','Pharmacology'),('haemonchus','Haemonchus'),('nsaids','NSAIDs'),('surgery-books','Surgery books')])+'</nav>'
    from assets_index import find_preset
    search_records=[r for r in b.RECORDS if keep_complete_resource(r)]
    for a,t in [('pharmacology','Pharmacology'),('haemonchus','Haemonchus'),('nsaids','NSAIDs'),('surgery-books','Surgery books')]:
        rows=find_preset(t,search_records);body+=group(b,t,rows,'preset-'+a,False,teaser,3) if rows else '<details class="resource-group" id="preset-'+a+'"><summary><h3>'+t+'</h3><span class="group-count">0</span></summary>'+empty(b,'No resources for this topic yet')+'</details>'
    b.write_page('/search/','Search Veterinary Resources',b.geo.META['/search/']['summary'],body+'</section></div>',noindex=True)
def render(b):overview(b);guides(b);collections(b);tools(b);other(b)

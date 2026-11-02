"""Approved prescription-paper homepage. All controls and copy are semantic HTML.

The three supplied JPEGs are only used as clipped illustration sources, never as
page backgrounds. Their original pixels keep the approved bag and syringe intact.
"""
import json
from html import escape as e
from pathlib import Path
from urllib.parse import quote
from ui import icon, link, share_strip

ROOT=Path(__file__).resolve().parent.parent
CONTENT=json.loads((ROOT/'data/homepage.json').read_text())

def art(name,box,cls='',source=None):
    x,y,w,h=box
    loading='eager' if name=='prescription' else 'lazy'
    asset=source or name
    ext='webp' if asset in ('clinical','community') else 'jpg'
    return f'<span class="rx-art {cls}" style="aspect-ratio:{w}/{h};--art-w:{720/w*100:.5f}%;--art-x:{-x/w*100:.5f}%;--art-y:{-y/h*100:.5f}%" aria-hidden="true"><img src="/assets/home/{asset}.{ext}" width="720" height="1280" alt="" loading="{loading}" decoding="async"></span>'

def burst():return '<span class="rx-burst" aria-hidden="true"><i></i><i></i><i></i></span>'

def header(path='/', home=True):
    syringe='<span class="rx-letter-t"><span class="rx-glyph-t">t</span><span class="rx-syringe"><img src="/assets/home/syringe.webp" width="23" height="129" alt="" loading="eager" decoding="async"></span></span>'
    logo='<span class="rx-wordmark" aria-hidden="true"><span class="rx-symbol">R<sub>x</sub></span> <span class="rx-notes">No'+syringe+'es</span> <span class="rx-by">by <b>thatvetguy</b></span></span>'
    promise=('<h1 id="academic-resources">' if home else '<div class="rx-promise-title">')+'Free Veterinary<br>Academic Resources'+('</h1>' if home else '</div>')
    return '<a class="skip-link" href="#main">Skip to content</a><header class="rx-header container"><div class="rx-paper"><span class="rx-tape" aria-hidden="true"></span><a href="/" class="rx-brand" aria-label="Rx Notes by ThatVetGuy — Home">'+logo+'</a><div class="rx-promise">'+promise+'<p>Thoughtfully organised for <mark>future vets.</mark></p></div><span class="rx-vet-emblem" aria-hidden="true"><svg viewBox="0 0 40 48" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M18 11C12 3 7 7 2 3c0 9 5 14 15 13M22 11C28 3 33 7 38 3c0 9-5 14-15 13" fill="#bde9dc" stroke="#17664d" stroke-width="1.8"/><path d="m5 9 9 4m21-4-9 4M20 8v37" stroke="#101b43" stroke-width="2.2"/><circle cx="20" cy="5" r="2.5" fill="#0769ce"/><path d="M14 16c-9 4 1 9 9 12s5 8-5 11m8-23c9 4-1 9-9 12s-5 8 5 11" stroke="#17664d" stroke-width="2.4"/><path d="m9 27 11 18 11-18" stroke="#0769ce" stroke-width="2.4"/></svg></span><span class="rx-paper-paw" aria-hidden="true">'+icon('paw')+'</span></div></header>'

def search():
    return '<div class="rx-search-wrap"><div class="search-area"><form class="search-form" action="/search/" method="get" role="search"><label for="resource-search" class="sr-only">Search veterinary resources</label><div class="search-field">'+icon('search')+'<input id="resource-search" type="search" name="q" placeholder="Search notes, books, PYQs, drugs…" autocomplete="off" enterkeyhint="search"><button class="icon-button search-submit" type="submit" aria-label="Search">'+icon('arrow')+'</button></div><div id="search-suggestions" class="search-suggestions" hidden><p class="search-loading" hidden>Searching…</p><ul id="suggestion-list" class="suggestion-list"></ul></div></form><p id="search-status" class="sr-only" role="status"></p></div></div>'

def heading(title,subtitle,ic,tone,extra=''):
    return '<header class="rx-section-heading"><span class="rx-heading-icon '+tone+'">'+icon(ic)+burst()+'</span><div><h2>'+title+'</h2><p class="rx-hand">'+subtitle+'</p></div>'+extra+'</header>'

def tabs(ident,labels):
    return '<div class="rx-tabs" role="tablist" aria-label="'+e(ident.replace('-',' ').title())+'">'+''.join('<a href="'+u+'" role="tab" id="'+ident+'-tab-'+str(i)+'" aria-controls="'+ident+'-panel-'+str(i)+'" aria-selected="'+str(i==0).lower()+'" tabindex="'+('0' if i==0 else '-1')+'">'+t+'</a>' for i,(t,u) in enumerate(labels))+'</div>'

def panel(ident,i,body):
    return '<div class="rx-panel" id="'+ident+'-panel-'+str(i)+'" role="tabpanel" aria-labelledby="'+ident+'-tab-'+str(i)+'"'+(' hidden' if i else '')+'>'+body+'</div>'

def row(title,url,ic,tone,status=None):
    from book_catalogue import by_url
    book=by_url(url)
    if book:url=book['page']
    content='<span class="rx-row-icon '+tone+'">'+icon(ic)+'</span><span class="rx-row-label">'+e(title)+(('<small class="rx-availability">'+e(status)+'</small>') if status else '')+'</span>'+icon('chevron')
    return link(url,content,'rx-row')

def missing(title,ic,tone):
    return row(title,'/request-resource/?resource='+quote(title),ic,tone,'Coming soon · Request')

def subject_icon(name):
    n=name.lower()
    for key,ic,tone in [('anatomy','bone','peach'),('physiology','heart','pink'),('production management','leaf','mint'),('biochemistry','flask','purple'),('microbiology','microbe','mint'),('pathology','microscope','pink'),('genetics','dna','purple'),('nutrition','leaf','mint'),('pharmacology','pill','sky'),('parasitology','microbe','purple'),('public health','shield','mint'),('products','milk','peach'),('extension','people','sky'),('surgery','cross','pink'),('gynaecology','heart','peach'),('medicine','stethoscope','sky')]:
        if key in n:return ic,tone
    return 'book','mint'

def roadmap_art(year):
    """One illustrated route, with a distinct learning symbol for each year."""
    symbols={
      1:'<path d="M43 24q-5-6-9 0-4 5 2 8l13 13q3 6 8 2 6-4 0-9L43 24Z" fill="#fff2d7"/><path d="m38 31 13 13"/>',
      2:'<path d="M36 18h16m-12 0v14L30 49q-3 6 4 6h26q7 0 4-6L48 32V18" fill="#fff"/><path d="M36 42h21l7 10H32Z" fill="#aadccc" stroke="none"/><circle cx="44" cy="44" r="2" fill="#0769ce" stroke="none"/>',
      3:'<rect x="29" y="21" width="35" height="34" rx="6" fill="#fff"/><path d="M35 29h12m-12 7h10m-10 7h8"/><circle cx="57" cy="49" r="10" fill="#ffe38b"/><path d="m52 49 3 3 6-7"/>',
      4:'<path d="M32 22v10a10 10 0 0 0 20 0V22m-23 0h6m14 0h6M42 43v5a9 9 0 0 0 18 0v-8" stroke="#0769ce" stroke-width="3"/><circle cx="60" cy="35" r="6" fill="#fff"/>'
    }
    return '<span class="rx-road-art" aria-hidden="true"><svg viewBox="0 0 80 72" fill="none" stroke="#183654" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m5 13 20-6 26 6 22-6v53l-22 6-26-6-20 6Z" fill="#e7f4ff" stroke="#a2c8e0"/><path d="M25 7v53m26-47v53" stroke="#a2c8e0"/><path d="M12 54c28-2-9-35 25-31" stroke="#70b69e" stroke-dasharray="3 4"/>'+symbols[year]+'<circle cx="15" cy="14" r="11" fill="#0769ce" stroke="#fff"/><text x="15" y="18" text-anchor="middle" fill="white" stroke="none" font-family="sans-serif" font-size="12" font-weight="700">'+str(year)+'</text></svg></span>'

def academics(b):
    from course_outlines import outline_url
    ident='year';body=heading('BVSc &amp; AH Resources','Four years. Infinite syllabus. Character development included.','cap','mint','<span class="rx-section-paw" aria-hidden="true">'+icon('paw')+'</span>')
    body+=tabs(ident,[(b.DATA['labels'][str(y['year'])],'/bvsc/year-'+str(y['year'])+'/') for y in b.LIBRARY['years']])
    for i,y in enumerate(b.LIBRARY['years']):
        label=b.DATA['labels'][str(y['year'])];base='/bvsc/year-'+str(y['year'])+'/';subjects=''
        for s in y['subjects']:
            name=s['name'];ic,tone=subject_icon(name);name='Livestock Production & Management' if name=='Livestock Production Management' else name
            subjects+=row(name,base+s['slug']+'/',ic,tone,None if s['count'] else 'Course outline & study guide')
        roadmap='<aside class="rx-roadmap"><div class="rx-map-heading">'+roadmap_art(y['year'])+'<h3>'+label+'<br>Road Map</h3></div><p class="rx-hand">'+CONTENT['roadmaps'][str(y['year'])]['description']+'</p>'+'<div class="rx-roadmap-actions">'+link(base+'roadmap/','Road Map '+icon('arrow'),'rx-button rx-roadmap-button')+link(outline_url(y['year']),icon('paper')+'<span>Course Outline</span>','rx-course-outline')+'</div></aside>'
        footer='<div class="rx-year-footer"><span>'+icon('book')+'<span class="rx-hand">'+str(len(y['subjects']))+' subjects <span class="rx-footer-detail">· notes &amp; books</span></span></span>'+link(base,'Explore '+label+' '+icon('arrow'),'rx-explore')+'</div>'
        body+=panel(ident,i,'<div class="rx-year-drawer"><div class="rx-subjects">'+subjects+'</div>'+roadmap+'</div>'+footer)
    from resource_directories import shortcuts
    body+=shortcuts(b)
    return '<section class="rx-section rx-academics" id="notes" data-home-tabs>'+body+'</section>'

def objectives(b):
    ident='objective';body=heading('Objective &amp; Competition Resources',"MCQs repeat. Your confidence doesn’t.",'target','sky')+tabs(ident,[('Objective Notes','/objective/#books'),('Question Banks','/objective/#subject-wise')])
    for i,key in enumerate(['objective-notes','question-banks']):
        rows=''
        for r in [r for r in b.RECORDS if key in r['collections']]:
            from book_catalogue import by_resource
            book=by_resource(r['id']);cover=book['cover']
            artwork='<img src="'+e(cover['path'],quote=True)+'" width="'+str(cover['width'])+'" height="'+str(cover['height'])+'" alt="" loading="lazy" decoding="async">'
            content='<span class="rx-resource-cover" aria-hidden="true">'+artwork+'</span><span class="rx-row-label">'+e(r['title'])+'</span><span class="rx-row-open">View '+icon('arrow')+'</span>'
            rows+=link(book['page'],content,'rx-row rx-resource-row')
        body+=panel(ident,i,'<div class="rx-row-drawer">'+rows+'</div>')
    body+='<div class="rx-collection-footer">'+link('/objective/','Explore more '+icon('arrow'),'rx-explore')+'</div>'
    return '<section class="rx-section rx-objective" id="objective" data-home-tabs>'+body+'</section>'

def toolkit_art(kind):
    """Small, purpose-made illustrations; labels live in the adjacent link text."""
    paw='<ellipse cx="37" cy="36" rx="7" ry="6" fill="#0769ce" stroke="none"/><g fill="#0769ce" stroke="none"><circle cx="29" cy="28" r="3"/><circle cx="35" cy="24" r="3"/><circle cx="42" cy="25" r="3"/><circle cx="47" cy="30" r="3"/></g>'
    drawings={
        'apps':'<rect x="7" y="10" width="41" height="49" rx="10" fill="#bde9dc" stroke="none"/><rect x="20" y="5" width="34" height="52" rx="8" fill="white"/><path d="M31 11h12M33 51h8"/>'+paw+'<rect x="5" y="40" width="19" height="19" rx="6" fill="#ffe38b"/><path d="M11 49h7m-3.5-3.5v7"/>',
        'web':'<rect x="5" y="8" width="54" height="42" rx="8" fill="#fff"/><path d="M6 20h52"/><circle cx="13" cy="14" r="1.5" fill="#efb560" stroke="none"/><circle cx="19" cy="14" r="1.5" fill="#81cbb5" stroke="none"/><path d="M13 28h16m-16 6h12" stroke="#0769ce"/><path d="M31 35q-10-5-19-1v20q9-4 19 1 10-5 21-1V34q-11-4-21 1Z" fill="#bde9dc"/><path d="M31 35v20m-14-15h8m-8 5h8m13-5h8m-8 5h8"/>',
        'career':'<path d="M18 57V43q0-8 14-8t14-9V16" stroke="#0769ce" stroke-width="4"/><path d="m39 22 7-7 7 7" stroke="#0769ce"/><path d="m3 17 20-10 20 10-20 10Z" fill="#ffe38b"/><path d="M12 22v9q11 8 22 0v-9M5 18v13"/><circle cx="18" cy="54" r="7" fill="#bde9dc"/><path d="m15 54 2 2 4-4"/><circle cx="46" cy="43" r="9" fill="#ffe8d7"/><path d="M42 43h8m-4-4v8"/>',
        'jobs':'<rect x="7" y="20" width="50" height="35" rx="7" fill="#bde9dc"/><path d="M23 20v-6h18v6M8 32q24 12 48 0"/><rect x="27" y="32" width="10" height="9" rx="2" fill="#fff"/><circle cx="51" cy="14" r="9" fill="#ffe38b"/><path d="M51 10v8m-4-4h8"/>'
    }
    return '<span class="rx-tool-art" aria-hidden="true"><svg viewBox="0 0 64 64" fill="none" stroke="#183654" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'+drawings[kind]+'</svg></span>'

def tools():
    body=heading('Tools &amp; Tips','Study smart. Because suffering manually is outdated.','bulb','yellow')+tabs('tools',[('Tools','/study-tools/#tools'),('Tips','/study-tools/#tips')])
    for i,key in enumerate(['tools','tips']):
        if key=='tools':
            details=[('apps','Revision, reference & anatomy'),('web','Notes, cases & trusted sources'),('career','Find your path after BVSc')]
            rows=''.join(link(r['url'],toolkit_art(kind)+'<span class="rx-row-label">'+e(r['title'])+'<small>'+e(detail)+'</small></span>'+icon('chevron'),'rx-row rx-tool-row') for r,(kind,detail) in zip(CONTENT[key],details))
        else:
            rows=''.join(link(r['url'],roadmap_art(n)+'<span class="rx-row-label">'+e(r['title'])+'</span>'+icon('chevron'),'rx-row rx-roadmap-row') for n,r in enumerate(CONTENT[key],1))
        body+=panel('tools',i,'<div class="rx-row-drawer">'+rows+'</div>')
    return '<section class="rx-section rx-tools" id="study" data-home-tabs>'+body+'</section>'

def clinical():
    body='<header class="rx-clinical-heading"><div><h2>Clinical Resources</h2><svg class="rx-underline" viewBox="0 0 320 10" aria-hidden="true"><path d="M2 6Q12-2 22 6T42 6T62 6T82 6T102 6T122 6T142 6T162 6T182 6T202 6T222 6T242 6T262 6T282 6T302 6T318 6"/></svg></div><span>'+icon('stethoscope')+burst()+'</span><p class="rx-hand">Check the dose twice. The patient can’t leave a review.</p></header><div class="rx-clinical-grid">'
    for title,url,asset,tone in [('Handbooks','/clinical/handbooks/','handbook-case','mint'),('Drug Index','/clinical/drug-index/','drug-prescription','yellow')]:
        body+=link(url,'<h3>'+title+'</h3><img src="/assets/home/'+asset+'.svg" width="240" height="200" alt="" loading="lazy" decoding="async"><span class="rx-clinical-cta">Open '+icon('arrow')+'</span>','rx-clinical-card rx-clinical-icon-card '+tone)
    return '<section class="rx-section rx-clinical" id="clinical">'+body+'</div></section>'

def backbench():
    return '<section class="rx-section rx-backbench" id="backbench">'+heading('Backbenchers Corner','For when the exam is tomorrow and the motivation arrived today.','telegram','sky')+'<div class="rx-revision-card">'+art('community',(53,290,250,270),'rx-phone-art')+'<div><h3><mark>Last-minute revision notes</mark></h3><p>Short notes and high-yield topics for one more revision.</p>'+link('https://t.me/vetshortnotesbytvg','View Notes','rx-button')+'</div></div></section>'

def involved():
    body=heading('Get Involved','Find an opportunity. Help fill a gap.','people','sky')+'<div class="rx-community-grid">'
    for title,text,url,ic,tone in [('Vet Job Updates','Explore opportunities on Telegram.','https://t.me/jobupdatesbytvg','jobs','mint'),('Request Resources','Missing a note or book? Let us know.','/request-resource/','message','peach')]:
        artwork=toolkit_art('jobs') if ic=='jobs' else '<span class="rx-cta-icon">'+icon(ic)+'</span>'
        body+=link(url,artwork+'<div class="rx-community-copy"><h3>'+title+'</h3><p>'+text+'</p></div><span class="rx-cta-arrow">'+icon('arrow')+'</span>','rx-community-card '+tone)
    body+='</div><p class="rx-signoff">'+icon('paw')+'<span class="rx-hand">Students today. Better vets tomorrow.</span>'+icon('paw')+'</p>'
    return '<section class="rx-section rx-involved" id="community">'+body+'</section>'

def footer():
    return '<footer class="site-footer rx-footer"><div class="container"><nav aria-label="Footer">'+''.join(link(u,t) for u,t in [('/about/','About'),('/request-resource/#contact','Contact'),('/request-resource/#contribute','Contribute'),('/request-resource/','Request'),('/request-resource/#report','Report an error')])+'</nav><p class="footer-note">Free resources for future vets. Credit to the original authors. © 2026 ThatVetGuy.</p></div></footer>'

def render(b):
    content=academics(b)+objectives(b)+tools()+clinical()+backbench()+involved()
    body='<div class="container rx-home">'+search()+'<p class="rx-library-intro">Veterinary notes &amp; study material for BVSc &amp; AH. Browse by year, subject or resource.</p>'+'<div class="rx-content">'+content+'</div>'+share_strip('home')+'</div>'
    mirror='<h1>Free Veterinary Academic Resources</h1><p>Veterinary notes &amp; study material for BVSc &amp; AH. Browse by year, subject or resource.</p>'+content
    b.write_page('/','Free Veterinary Notes, Books & Study Resources | ThatVetGuy',b.geo.META['/']['summary'],body,home=True,mirror_body=mirror)

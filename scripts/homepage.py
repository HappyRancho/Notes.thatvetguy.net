"""Approved prescription-paper homepage. All controls and copy are semantic HTML.

The three supplied JPEGs are only used as clipped illustration sources, never as
page backgrounds. Their original pixels keep the approved bag and syringe intact.
"""
import json
from html import escape as e
from pathlib import Path
from urllib.parse import quote
from ui import icon, link

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
    syringe='<span class="rx-letter-t"><span class="rx-syringe"><img src="/assets/home/syringe.webp" width="23" height="129" alt="" loading="eager" decoding="async"></span></span>'
    logo='<span class="rx-wordmark" aria-hidden="true"><span class="rx-symbol">R<sub>x</sub></span><span class="rx-notes">No'+syringe+'es</span><span class="rx-by">by <b>thatvetguy</b></span></span>'
    nav=''.join('<a href="'+u+'" class="nav-link"'+(' aria-current="page"' if path.startswith(u) else '')+'>'+t+'</a>' for u,t in [('/bvsc/','Notes & Books'),('/objective/','Objective'),('/study-tools/','Study Tools'),('/clinical/','Clinical')])
    promise=('<h1 id="academic-resources">' if home else '<div class="rx-promise-title">')+'Free Veterinary<br>Academic Resources'+('</h1>' if home else '</div>')
    return '<a class="skip-link" href="#main">Skip to content</a><header class="rx-header container"><div class="rx-paper"><span class="rx-tape" aria-hidden="true"></span><a href="/" class="rx-brand" aria-label="Rx Notes by ThatVetGuy — Home">'+logo+'</a><div class="rx-promise">'+promise+'<p>Thoughtfully organised for <mark>future vets.</mark></p></div><button class="icon-button rx-menu js-only" type="button" data-dialog="more-sheet" aria-controls="more-sheet" aria-expanded="false" aria-label="Open menu">'+icon('menu')+'</button><span class="rx-paper-paw" aria-hidden="true">'+icon('paw')+'</span><nav class="rx-desktop-nav" aria-label="Main">'+nav+'</nav></div></header>'

def search():
    return '<div class="rx-search-wrap"><div class="search-area"><form class="search-form" action="/search/" method="get" role="search"><label for="resource-search" class="sr-only">Search veterinary resources</label><div class="search-field">'+icon('search')+'<input id="resource-search" type="search" name="q" placeholder="Search notes, books, PYQs, drugs…" autocomplete="off" enterkeyhint="search"><button class="icon-button search-submit" type="submit" aria-label="Search">'+icon('arrow')+'</button></div><div id="search-suggestions" class="search-suggestions" hidden><p class="search-loading" hidden>Searching…</p><ul id="suggestion-list" class="suggestion-list"></ul></div></form><p id="search-status" class="sr-only" role="status"></p></div><button type="button" class="icon-button rx-search-options js-only" data-dialog="search-options" aria-controls="search-options" aria-expanded="false" aria-label="Browse resource categories">'+icon('sliders')+'</button></div><dialog id="search-options" class="sheet" aria-labelledby="search-options-title"><div class="dialog-head"><div class="dialog-title" id="search-options-title">Find your resource</div><button class="icon-button" data-close aria-label="Close categories">'+icon('close')+'</button></div><nav class="more-links" aria-label="Resource categories">'+''.join(link(u,t+icon('arrow')) for u,t in [('/search/','Search all resources'),('/bvsc/','Notes & Books'),('/objective/','Objective & Question Banks'),('/clinical/','Clinical Resources')])+'</nav></dialog>'

def heading(title,subtitle,ic,tone,extra=''):
    return '<header class="rx-section-heading"><span class="rx-heading-icon '+tone+'">'+icon(ic)+burst()+'</span><div><h2>'+title+'</h2><p class="rx-hand">'+subtitle+'</p></div>'+extra+'</header>'

def tabs(ident,labels):
    return '<div class="rx-tabs" role="tablist" aria-label="'+e(ident.replace('-',' ').title())+'">'+''.join('<a href="'+u+'" role="tab" id="'+ident+'-tab-'+str(i)+'" aria-controls="'+ident+'-panel-'+str(i)+'" aria-selected="'+str(i==0).lower()+'" tabindex="'+('0' if i==0 else '-1')+'">'+t+'</a>' for i,(t,u) in enumerate(labels))+'</div>'

def panel(ident,i,body):
    return '<div class="rx-panel" id="'+ident+'-panel-'+str(i)+'" role="tabpanel" aria-labelledby="'+ident+'-tab-'+str(i)+'"'+(' hidden' if i else '')+'>'+body+'</div>'

def row(title,url,ic,tone,status=None):
    content='<span class="rx-row-icon '+tone+'">'+icon(ic)+'</span><span class="rx-row-label">'+e(title)+(('<small class="rx-availability">'+e(status)+'</small>') if status else '')+'</span>'+icon('chevron')
    return link(url,content,'rx-row')

def missing(title,ic,tone):
    return row(title,'/request-resource/?resource='+quote(title),ic,tone,'Coming soon · Request')

def subject_icon(name):
    n=name.lower()
    for key,ic,tone in [('anatomy','bone','peach'),('physiology','heart','pink'),('production management','leaf','mint'),('biochemistry','flask','purple'),('microbiology','microbe','mint'),('pathology','microscope','pink'),('genetics','dna','purple'),('nutrition','leaf','mint'),('pharmacology','pill','sky'),('parasitology','microbe','purple'),('public health','shield','mint'),('products','milk','peach'),('extension','people','sky'),('surgery','cross','pink'),('gynaecology','heart','peach'),('medicine','stethoscope','sky')]:
        if key in n:return ic,tone
    return 'book','mint'

def academics(b):
    ident='year';body=heading('BVSc &amp; AH Resources','Four years. Infinite syllabus. Character development included.','cap','mint','<span class="rx-section-paw" aria-hidden="true">'+icon('paw')+'</span>')
    body+=tabs(ident,[(b.DATA['labels'][str(y['year'])],'/bvsc/year-'+str(y['year'])+'/') for y in b.LIBRARY['years']])
    for i,y in enumerate(b.LIBRARY['years']):
        label=b.DATA['labels'][str(y['year'])];base='/bvsc/year-'+str(y['year'])+'/';subjects=''
        for s in y['subjects']:
            name=s['name'];ic,tone=subject_icon(name);name='Livestock Production & Management' if name=='Livestock Production Management' else name
            subjects+=row(name,base+s['slug']+'/',ic,tone) if s['count'] else '<div class="rx-row rx-unavailable"><span class="rx-row-icon '+tone+'">'+icon(ic)+'</span><span class="rx-row-label">'+e(name)+'<small>Coming soon</small></span></div>'
        roadmap='<aside class="rx-roadmap"><div class="rx-map-heading">'+icon('map')+burst()+'<h3>'+label+'<br>Road Map</h3></div><p class="rx-hand">'+CONTENT['roadmaps'][str(y['year'])]['description']+'</p>'+link(base+'#road-map','View Road Map '+icon('arrow'),'rx-button')+'</aside>'
        footer='<div class="rx-year-footer"><span>'+icon('book')+'<span class="rx-hand">'+str(len(y['subjects']))+' subjects <span class="rx-footer-detail">· notes &amp; books</span></span></span>'+link(base,'Explore '+label+' '+icon('arrow'),'rx-explore')+'</div>'
        body+=panel(ident,i,'<div class="rx-year-drawer"><div class="rx-subjects">'+subjects+'</div>'+roadmap+'</div>'+footer)
    return '<section class="rx-section rx-academics" id="notes" data-home-tabs>'+body+'</section>'

def objectives(b):
    ident='objective';body=heading('Objective &amp; Competition Resources',"MCQs repeat. Your confidence doesn’t.",'target','sky')+tabs(ident,[('Objective Notes','/objective/#books'),('Question Banks','/objective/#subject-wise')])
    for i,key in enumerate(['objective-notes','question-banks']):
        rows=''
        for r in [r for r in b.RECORDS if key in r['collections']]:
            content='<span class="rx-row-icon '+r['tone']+'">'+icon(r['icon'])+'</span><span class="rx-row-label">'+e(r['title'])+'</span><span class="rx-row-open">Open '+icon('external')+'</span>'
            rows+=link(r['url'],content,'rx-row rx-resource-row')
        body+=panel(ident,i,'<div class="rx-row-drawer">'+rows+'</div>')
    body+='<div class="rx-collection-footer">'+link('/objective/','Explore more '+icon('arrow'),'rx-explore')+'</div>'
    return '<section class="rx-section rx-objective" id="objective" data-home-tabs>'+body+'</section>'

def tools():
    body=heading('Tools &amp; Tips','Study smart. Because suffering manually is outdated.','bulb','yellow')+tabs('tools',[('Tools','/study-tools/#tools'),('Tips','/study-tools/#tips')])
    for i,key in enumerate(['tools','tips']):
        rows=''.join(row(r['title'],r['url'],r['icon'],r['tone']) if r.get('url') else missing(r['title'],r['icon'],r['tone']) for r in CONTENT[key])
        body+=panel('tools',i,'<div class="rx-row-drawer">'+rows+'</div>')
    return '<section class="rx-section rx-tools" id="study" data-home-tabs>'+body+'</section>'

def clinical():
    body='<header class="rx-clinical-heading"><div><h2>Clinical Resources</h2><svg class="rx-underline" viewBox="0 0 320 10" aria-hidden="true"><path d="M2 6Q12-2 22 6T42 6T62 6T82 6T102 6T122 6T142 6T162 6T182 6T202 6T222 6T242 6T262 6T282 6T302 6T318 6"/></svg></div><span>'+icon('stethoscope')+burst()+'</span><p class="rx-hand">Check the dose twice. The patient can’t leave a review.</p></header><div class="rx-clinical-grid">'
    for title,url,asset,tone in [('Handbooks Collection','/clinical/handbooks/','handbook-case','mint'),('Drug Index Collection','/clinical/drug-index/','drug-prescription','yellow')]:
        body+=link(url,'<h3>'+title+'</h3><img src="/assets/home/'+asset+'.svg" width="240" height="200" alt="" loading="lazy" decoding="async"><span class="rx-clinical-cta">Open '+icon('arrow')+'</span>','rx-clinical-card rx-clinical-icon-card '+tone)
    return '<section class="rx-section rx-clinical" id="clinical">'+body+'</div></section>'

def backbench():
    return '<section class="rx-section rx-backbench" id="backbench">'+heading('Backbenchers Corner','For when the exam is tomorrow and the motivation arrived today.','telegram','sky')+'<div class="rx-revision-card">'+art('community',(53,290,250,270),'rx-phone-art')+'<div><h3><mark>Concise Last Minute Revision Notes</mark></h3><p>Short notes, high-yield topics and more on our Telegram channel.</p>'+link('https://t.me/vetshortnotesbytvg','View Notes','rx-button')+'</div></div></section>'

def involved():
    body=heading('Get Involved','Because your next note shouldn’t depend on a forwarded PDF.','people','sky')+'<div class="rx-community-grid">'
    for title,text,url,ic,tone in [('Vet Job Updates','Join the Telegram group for opportunities.','https://t.me/jobupdatesbytvg','megaphone','mint'),('Request Resources','Can’t find a resource? Ask for it.','/request-resource/','message','peach')]:
        body+=link(url,'<span class="rx-cta-icon">'+icon(ic)+'</span><h3>'+title+'</h3><p>'+text+'</p><span class="rx-cta-arrow">'+icon('arrow')+'</span>','rx-community-card '+tone)
    body+='</div><p class="rx-signoff">'+icon('paw')+'<span class="rx-hand">Students today. Better vets tomorrow.</span>'+icon('paw')+'</p>'
    return '<section class="rx-section rx-involved" id="community">'+body+'</section>'

def footer():
    return '<footer class="site-footer rx-footer"><div class="container"><nav aria-label="Footer">'+''.join(link(u,t) for u,t in [('/about/','About'),('/request-resource/#contact','Contact'),('/request-resource/#contribute','Contribute'),('/request-resource/','Request'),('/request-resource/#report','Report an error')])+'</nav><div class="rx-footer-ecosystem"><nav aria-label="ThatVetGuy ecosystem">'+link('https://thatvetguy.net','ThatVetGuy')+'<span>Notes</span>'+link('https://blog.thatvetguy.net','Blog')+'</nav><button class="text-button js-only" data-dialog="personal-library">'+icon('book')+' Saved & recent</button></div><p class="footer-note">Notes open on Google Drive; collection resources open in Telegram. Credit remains with their original authors. © 2026 ThatVetGuy.</p></div></footer>'

def render(b):
    content=academics(b)+objectives(b)+tools()+clinical()+backbench()+involved()
    body='<div class="container rx-home">'+search()+'<div class="rx-content">'+content+'</div></div>'
    mirror='<h1>Free Veterinary Academic Resources</h1><p>Thoughtfully organised for future vets.</p>'+content
    b.write_page('/','Free Veterinary Notes, Books & Study Resources | ThatVetGuy',b.geo.META['/']['summary'],body,home=True,mirror_body=mirror)

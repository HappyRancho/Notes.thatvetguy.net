"""Shared navigation, search and compact homepage compositions."""
from html import escape as e
from ui import icon,link

def header(path):
    nav=''
    for url,title in [('/bvsc/','Notes & Books'),('/objective/','Objective'),('/study-tools/','Study Tools'),('/clinical/','Clinical')]:
        active=' aria-current="page"' if path.startswith(url) else ''
        nav+=f'<a class="nav-link" href="{url}"{active}>{title}</a>'
    return '<a class="skip-link" href="#main">Skip to content</a><header class="site-header"><div class="container header-inner">'+link('/',icon('paw')+'<span>Notes.<b>ThatVetGuy</b></span>','brand')+'<nav class="desktop-nav" aria-label="Main">'+nav+'</nav><div class="header-actions">'+link('/search/',icon('search')+'<span class="sr-only">Search resources</span>','icon-button header-search command-trigger')+'<button class="icon-button theme-toggle js-only" type="button" aria-label="Switch to dark theme" aria-pressed="false"><span aria-hidden="true">◐</span></button></div></div></header>'

def navigation(path):
    links=''
    for url,title,ic in [('/','Home','paw'),('/bvsc/','Notes','book'),('/objective/','Objective','check'),('/search/','Search','search')]:
        active=' aria-current="page"' if (path==url or url!="/" and path.startswith(url)) else ''
        links+=f'<a href="{url}"{active}>'+icon(ic)+'<span>'+title+'</span></a>'
    more=[('/about/','About'),('/request-resource/','Request Resource'),('/request-resource/#contribute','Contribute'),('/request-resource/#report','Report an error'),('https://t.me/vetshortnotesbytvg','Short notes on Telegram'),('https://t.me/jobupdatesbytvg','Job updates on Telegram')]
    return '<nav class="bottom-nav" aria-label="Mobile">'+links+'<button type="button" class="js-only" data-dialog="more-sheet" aria-controls="more-sheet" aria-expanded="false">'+icon('menu')+'<span>More</span></button><a class="nojs-only" href="/about/">About</a></nav><dialog id="more-sheet" class="sheet" aria-labelledby="more-title"><div class="dialog-head"><div id="more-title" class="dialog-title">A little more.</div><button class="icon-button" data-close aria-label="Close menu">'+icon('close')+'</button></div><nav class="more-links" aria-label="Community and information">'+''.join(link(u,t+icon('arrow')) for u,t in more)+'</nav></dialog>'

def palette():
    return '<dialog id="command-palette" class="sheet command-dialog" aria-labelledby="command-title"><div class="dialog-head"><div id="command-title" class="dialog-title">Find your next read.</div><button class="icon-button" data-close aria-label="Close search">'+icon('close')+'</button></div><label class="sr-only" for="command-search">Search all resources</label><input id="command-search" type="search" placeholder="Subject, note, book…" autocomplete="off"><p class="search-loading" hidden>Searching…</p><ul id="command-results" class="suggestion-list"></ul><p id="command-status" role="status"></p></dialog><dialog id="personal-library" class="sheet" aria-label="Saved and recently opened resources"><div class="dialog-head"><div class="dialog-title">Your study shelf</div><button class="icon-button" data-close aria-label="Close study shelf">'+icon('close')+'</button></div><div id="personal-content"></div></dialog>'

def footer(b):
    return '<footer class="site-footer"><div class="container"><div class="footer-top"><p class="footer-name">A little less searching.<br>A little more studying.</p><nav aria-label="Footer">'+''.join(link(u,t) for u,t in [('/about/','About'),('/request-resource/#contact','Contact'),('/request-resource/#contribute','Contribute'),('/request-resource/','Request'),('/request-resource/#report','Report an error')])+'</nav></div><div class="footer-bottom"><nav aria-label="ThatVetGuy ecosystem">'+link('https://thatvetguy.net','ThatVetGuy')+'<span>Notes</span>'+link('https://blog.thatvetguy.net','Blog')+'</nav><button class="text-button js-only" data-dialog="personal-library">'+icon('book')+' Saved & recent</button></div><p class="footer-note">Files open on Google Drive. Credit remains with their original authors. © 2026 ThatVetGuy.</p>'+b.section_aside('footer')+'</div></footer>'

def search(b,page=False):
    return '<div class="search-area"><form class="search-form" action="/search/" method="get" role="search"><label for="resource-search" class="sr-only">Search veterinary resources</label><div class="search-field">'+icon('search')+'<input id="resource-search" type="search" name="q" placeholder="Search notes, books, topics…" autocomplete="off" enterkeyhint="search"><kbd class="search-shortcut" aria-hidden="true">/</kbd><button class="icon-button search-submit" aria-label="Search" type="submit">'+icon('arrow')+'</button></div><div id="search-suggestions" class="search-suggestions" hidden><p class="search-loading" hidden>Searching…</p><ul id="suggestion-list" class="suggestion-list"></ul></div></form><p id="search-status" role="status" class="'+('search-count' if page else 'sr-only')+'"></p></div>'

def year_tiles(b):
    tiles=''
    for y in b.LIBRARY['years']:
        n=y['year'];subjects=len(y['subjects']);count=y['count']
        tiles+=link('/bvsc/year-'+str(n)+'/',f'<span class="year-top"><span class="year-caption">BVSc & AH</span>{icon("arrow")}</span><strong class="year-numeral">{n}<span>{["st","nd","rd","th"][n-1]} year</span></strong><span class="year-meta">{subjects} subjects <span aria-hidden="true">·</span> {count:,} resources</span>',f'sticker year-tile year-{n}')
    return '<div class="year-grid">'+tiles+'</div>'

def home(b):
    subjects=sum(len(y['subjects']) for y in b.LIBRARY['years']);resources=len(b.RECORDS);years=len(b.LIBRARY['years'])
    stats=''.join(f'<li><strong data-count="{n}">{n:,}</strong><span>{title}</span></li>' for n,title in [(resources,'resources'),(subjects,'subjects'),(years,'years')])
    body='<section class="hero container"><p class="eyebrow">THE VET STUDENT’S OPEN SHELF</p><h1>Vet school notes,<br>sorted. <mark>Finally.</mark></h1><p class="hero-copy">Free BVSc & AH notes, books, PYQs and clinical references, organised by year.</p>'+search(b)+b.section_aside('search')+'<ul class="live-stats" aria-label="Library at a glance">'+stats+'</ul></section>'
    body+='<section class="section container" id="notes"><div class="section-heading"><div><p class="eyebrow">BVSc NOTES & BOOKS</p><h2>Pick your year.</h2></div><span class="section-caption">Your syllabus. Your starting point.</span></div>'+year_tiles(b)+b.section_aside('bvsc')+'</section>'
    body+='<section class="section container" id="study"><div class="section-heading"><div><p class="eyebrow">A LITTLE HELP GOES A LONG WAY</p><h2>More ways to study.</h2></div></div><div class="study-bento">'
    for cls,ic,url,title,desc in [('objective-tile','check','/objective/','Objective Resources','Subject-wise questions, objective books & past papers.'),('tools-tile','spark','/study-tools/','Study Tools','AI guides, free apps & useful study habits.'),('clinical-tile','cross','/clinical/','Clinical Resources','Handbooks & pharmacology notes, within reach.')]:
        body+=link(url,'<span class="icon-chip">'+icon(ic)+'</span><div><h3>'+title+'</h3><p>'+desc+'</p></div>'+icon('arrow'), 'sticker bento-tile '+cls)
    body+='</div></section>'
    body+='<section class="section container" id="community"><div class="section-heading"><div><p class="eyebrow">OUTSIDE THE TEXTBOOK</p><h2>Your corner of vet school.</h2></div></div><div class="telegram-duo"><article class="sticker backbench" id="backbench"><span class="small-label">'+icon('telegram')+' SHORT NOTES</span><h3>Backbenchers<br>Corner.</h3><p>Less to read.<br>More to remember.</p>'+link('https://t.me/vetshortnotesbytvg','<span>Open Short Notes</span>','button')+'</article><article class="sticker jobs" id="telegram-updates"><span class="small-label">'+icon('telegram')+' JOB UPDATES</span><h3>Your next<br>chapter.</h3><p>Veterinary opportunities, without the hunt.</p>'+link('https://t.me/jobupdatesbytvg','<span>Follow Job Updates</span>','button')+'</article></div>'+b.section_aside('backbench')+'</section>'
    body+='<section class="container request-strip" id="request"><h2>Can’t find it?</h2><p>A note, book or topic. Just ask.</p>'+link('/request-resource/','Request a resource '+icon('arrow'),'text-link')+'</section>'
    divider='<svg class="ecg-divider" viewBox="0 0 1120 12" preserveAspectRatio="none" aria-hidden="true"><path d="M0 6H540l4-4 5 8 5-4h566" vector-effect="non-scaling-stroke"/></svg>'
    body=body.replace('<div class="section-heading">',divider+'<div class="section-heading">')
    b.write_page('/','Free Veterinary Notes, Books & Study Resources | ThatVetGuy',b.geo.META['/']['summary'],body,home=True)

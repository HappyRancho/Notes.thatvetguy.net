#!/usr/bin/env python3
"""Build the dependency-free site. Edit data/resources.json, then run python3 scripts/build.py."""
from pathlib import Path
import json
import hashlib
import re
from html import escape
import os,sys
from library import build_library
LIBRARY=build_library(refresh=bool(os.getenv("DRIVE_API_KEY")))
from resources import RECORDS, CATALOGUE, unique
import library_pages
import geo
TOKENS=json.loads((Path(__file__).resolve().parent.parent/'data/design-tokens.json').read_text())

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / 'data/site-content.json').read_text())
DATA['years']={str(y['year']):[s['name'] for s in y['subjects'] if s['name']!='Unsorted'] for y in LIBRARY['years']}
SUBJECTS = json.loads((ROOT / 'data/subjects.json').read_text())
MICROCOPY = json.loads((ROOT / 'data/microcopy.json').read_text())
ASIDES = {k:MICROCOPY[k][0] for k in ['backbench','tools']}
BASE = 'https://notes.thatvetguy.net'
VERSION = hashlib.sha256(b''.join((ROOT/path).read_bytes() for path in ['assets/site.css','assets/theme.js','assets/logic.js','assets/site.js','scripts/build.py','scripts/library_pages.py','data/resources.json','data/microcopy.json'])).hexdigest()[:12]
DESCRIPTION = 'Free BVSc & AH veterinary notes, books, ICAR PYQs, objective resources, drug references, clinical handbooks and useful tools for veterinary students.'
# Existing subject names are retained; the university syllabus remains authoritative.
ROUTES = {
    'icar-pyq': '/objective/#icar-pyq', 'objective-questions': '/objective/#subject-wise',
    'objective-books': '/objective/#books', 'ai-guide': '/study-tools/#ai-guide',
    'free-apps': '/study-tools/#free-apps', 'useful-tools': '/study-tools/#useful-tools',
    'handbooks': '/clinical/#handbooks', 'drug-index': '/clinical/#drug-index',
    'clinical-other': '/clinical/#other-resources', 'surgery-books': '/bvsc/#veterinary-surgery-and-radiology',
    'about': '/about/'
}
ICONS = {
    'arrow': '<path d="M4 12h15m-6-6 6 6-6 6"/>',
    'external': '<path d="M7 17 17 7M7 7h10v10"/>',
    'search': '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 4 4"/>',
    'menu': '<path d="M4 8h16M4 16h16"/>',
    'close': '<path d="m6 6 12 12M6 18 18 6"/>',
    'book': '<path d="M3 5c4-1 6-1 9 1 3-2 5-2 9-1v15c-4-1-6-1-9 1-3-2-5-2-9-1Z"/><path d="M12 6v15"/>',
    'paper': '<rect x="5" y="3" width="14" height="18" rx="2"/><path d="M9 8h6M9 12h6M9 16h3"/>',
    'check': '<rect x="4" y="4" width="16" height="16" rx="2"/><path d="m8 12 3 3 5-6"/>',
    'cross': '<path d="M9 3h6v6h6v6h-6v6H9v-6H3V9h6Z"/>',
    'pill': '<path d="m9 4 11 11a4.95 4.95 0 0 1-7 7L2 11a4.95 4.95 0 0 1 7-7ZM7 16l8-8"/>',
    'spark': '<path d="m12 3 2.5 6.5L21 12l-6.5 2.5L12 21l-2.5-6.5L3 12l6.5-2.5Z"/>',
    'phone': '<rect x="6" y="2" width="12" height="20" rx="3"/><path d="M10 18h4"/>',
    'tools': '<path d="m14 6 4-4 4 4-4 4M14 6l-3 3M3 21l8-8M5 3l16 16-2 2L3 5Z"/>',
    'paw': '<path d="M7 13c-4 4-3 8 1 7l4-1 4 1c4 1 5-3 1-7-3-4-7-4-10 0Z"/><ellipse cx="5" cy="8" rx="2" ry="3"/><ellipse cx="10" cy="5" rx="2" ry="3"/><ellipse cx="16" cy="5" rx="2" ry="3"/><ellipse cx="21" cy="9" rx="2" ry="3"/>',
}

def icon(name, cls=''):
    if name == 'telegram':
        return f'<svg class="icon-svg {cls}" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M21.6 3.2c.4-.2.9.2.8.7l-3.3 16c-.1.7-.6.8-1.1.5l-5.1-3.8-2.5 2.4c-.3.3-.6.5-1 .5l.4-5.3 9.6-8.7c.4-.4-.1-.6-.5-.3L7 12.6l-5-1.6c-.6-.2-.6-.6.1-.9Z"/></svg>'
    return f'<svg class="icon-svg {cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>'

def slug(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

def link(url, text, cls='', external=False):
    external = url.startswith(('https://','http://')) and not url.startswith(BASE+'/')
    extra = ' target="_blank" rel="noopener noreferrer"' if external else ''
    if external and icon('external') not in text:
        text=text.replace(icon('arrow'),icon('external')) if icon('arrow') in text else text+icon('external')
    return f'<a href="{escape(url, quote=True)}" class="{cls}"{extra}>{text}</a>'

def section_heading(title, text='', extra=''):
    return f'<div class="section-heading"><div><h2>{title}</h2>{f"<p>{text}</p>" if text else ""}</div>{extra}</div>'

def section_aside(key,variant=0):
    return f'<p class="section-aside microcopy">{escape(MICROCOPY[key][variant])}</p>'

def header(home=False):
    prefix = '' if home else '/'
    def nav_link(url,title):
        return link(url,title,'nav-link')
    groups = [
        ('Study', [('BVSc Notes & Books', '/bvsc/'), ('Objective Resources', '/objective/')]),
        ('Resources', [('Vet Study Tools', '/study-tools/'), ('Clinical Resources', '/clinical/')]),
        ('Community', [('Backbenchers Corner', prefix+'#backbench'), ('Job Updates', prefix+'#telegram-updates'), ('Request Resource', '/request-resource/')]),
        ('ThatVetGuy', [('About', '/about/')])
    ]
    nav = ''.join(f'<section class="menu-group"><p class="menu-group-title">{name}</p>'+''.join(link(url, escape(title)+icon('arrow')) for title,url in items)+'</section>' for name,items in groups)
    return f'''<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header" id="top"><div class="container header-inner">
{link('/', '<span class="brand-icon">'+icon('book')+'</span><span>Notes.<b>ThatVetGuy</b></span>', 'brand', False)}
<nav class="desktop-nav" aria-label="Main navigation">{nav_link('/bvsc/','Notes & Books')}{nav_link('/objective/','Objective')}{nav_link('/study-tools/','Study Tools')}{nav_link('/clinical/','Clinical')}</nav>
<div class="header-actions">{link('/search/',icon('search')+'<span class="sr-only">Search resources</span>','icon-button header-search command-trigger')}<button type="button" class="icon-button theme-toggle js-only" aria-label="Switch colour theme" aria-pressed="false"><span aria-hidden="true">◐</span></button><button class="icon-button menu-button" type="button" aria-label="Open navigation" aria-controls="mobile-menu" aria-expanded="false">{icon('menu')}</button></div>
</div></header>
<noscript><div class="container nojs-nav" aria-label="Browse the library">{link('/bvsc/','Notes & Books')}{link('/objective/','Objective')}{link('/study-tools/','Study Tools')}{link('/clinical/','Clinical')}</div></noscript>
<dialog id="mobile-menu" class="menu-dialog" aria-labelledby="menu-title"><div class="menu-head"><div id="menu-title" class="menu-title">Explore.</div><button type="button" class="icon-button menu-close" aria-label="Close navigation">{icon('close')}</button></div><div class="menu-body">{link('/search/', icon('search')+'<span>Find a resource</span>'+icon('arrow'), 'menu-search search-jump')}<nav aria-label="Mobile navigation">{nav}</nav></div></dialog>'''

def footer():
    return f'''<footer class="site-footer"><div class="container footer-top"><div><p class="footer-name">ThatVetGuy ecosystem</p><p>Free veterinary notes, books & study resources.</p></div><nav aria-label="ThatVetGuy ecosystem">{link('https://thatvetguy.net','<span>ThatVetGuy<small>thatvetguy.net</small></span>'+icon('external'))}{link('/','<span>Notes<small>notes.thatvetguy.net</small></span>'+icon('arrow'))}{link('https://blog.thatvetguy.net','<span>Blog<small>blog.thatvetguy.net</small></span>'+icon('external'))}</nav></div><div class="container footer-bottom"><span>© 2026 ThatVetGuy</span><nav aria-label="Footer">{link('/about/','About')}{link('/request-resource/#contact','Contact')}{link('/request-resource/#contribute','Contribute')}{link('/request-resource/','Request Resource')}{link('/request-resource/#report','Report an Error')}</nav></div>{section_aside("footer")}<details class="container personal-library js-only"><summary>On this device · saved & recently opened</summary><p id="storage-status" role="status"></p><h2>Saved resources</h2><ul id="saved-resources"></ul><h2>Recently opened</h2><ul id="recent-resources"></ul><button type="button" id="clear-recent" class="button secondary">Clear recent history</button></details></footer>'''

def year_progress(y,names):
    ids=' '.join(slug(n) for n in names)
    return f'<div class="year-progress js-only" data-progress-year="{y}" data-subjects="{ids}"><label for="progress-{y}">Subjects marked studied: <span>0 of {len(names)}</span></label><progress id="progress-{y}" value="0" max="{len(names)}">0 of {len(names)}</progress></div>'

def bottom_navigation(path):
    items=[('/','Home','book'),('/bvsc/','Notes','book'),('/objective/','Objective','check'),('/search/','Search','search')]
    links=''.join(f'<a href="{url}"'+(' aria-current="page"' if path==url else '')+'>'+icon(ic)+'<span>'+title+'</span></a>' for url,title,ic in items)
    return '<nav class="bottom-nav" aria-label="Mobile shortcuts">'+links+'<button type="button" class="menu-button js-only" aria-label="Open more navigation" aria-controls="mobile-menu" aria-expanded="false">'+icon('menu')+'<span>More</span></button></nav>'

def command_palette():
    return '<dialog class="command-dialog" id="command-palette" aria-labelledby="command-title"><div class="menu-head"><div class="menu-title" id="command-title">Find a resource</div><button type="button" class="icon-button command-close" aria-label="Close search">'+icon('close')+'</button></div><div class="command-content"><label for="command-search" class="sr-only">Search all veterinary resources</label><input id="command-search" type="search" placeholder="Subject, note, book or drug…" autocomplete="off"><p class="search-loading" hidden>Loading the resource index…</p><ul id="command-results"></ul><p id="command-status" role="status" aria-live="polite"></p></div></dialog>'


PAGES = []
def write_page(path,title,description,body,items=None,home=False,noindex=False):
    description=geo.META.get(path,{}).get('summary',description)
    body=geo.heading_ids(geo.external_links(body)+geo.faq_html(path))
    geo.register(path,title,description,body,DATA['lastChecked'])
    social_image=geo.social(path)
    page_title = title if home else title+' | Notes.ThatVetGuy'
    canonical = BASE+path
    html=f'''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="site-build" content="{VERSION}"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(page_title)}</title><meta name="description" content="{escape(description,quote=True)}">
<meta name="theme-color" content="#fffaf2" media="(prefers-color-scheme: light)"><meta name="theme-color" content="#14110d" media="(prefers-color-scheme: dark)"><script src="/assets/theme.js?v={VERSION}"></script><meta name="robots" content="{'noindex,follow' if noindex else 'index,follow,max-image-preview:large'}">
<link rel="canonical" href="{canonical}"><link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<meta property="og:type" content="website"><meta property="og:site_name" content="Notes.ThatVetGuy"><meta property="og:title" content="{escape(page_title,quote=True)}"><meta property="og:description" content="{escape(description,quote=True)}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{BASE}{social_image}"><meta property="og:image:alt" content="Notes.ThatVetGuy — free academic resources for future vets"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{escape(page_title,quote=True)}"><meta name="twitter:description" content="{escape(description,quote=True)}"><meta name="twitter:image" content="{BASE}{social_image}">
<link rel="stylesheet" href="/assets/site.css?v={VERSION}">
<link rel="preload" href="/assets/fonts/notes-serif-latin.woff" as="font" type="font/woff" crossorigin>
<script type="application/ld+json">{geo.structured(path,title,description,items,home,body,RECORDS,DATA['lastChecked'])}</script>
<script src="/assets/logic.js?v={VERSION}" defer></script><script src="/assets/site.js?v={VERSION}" defer></script>
</head><body>{header(home)}<main id="main">{body}<div class="container page-checked">Last checked: <time datetime="{DATA['lastChecked']}">{DATA['lastChecked']}</time></div></main>{footer()}{bottom_navigation(path)}{command_palette()}</body></html>'''
    for nav_path in ['/bvsc/','/objective/','/study-tools/','/clinical/']:
        if path == nav_path or (nav_path=='/bvsc/' and path.startswith(nav_path)):
            html=html.replace(f'href="{nav_path}" class="nav-link"',f'href="{nav_path}" class="nav-link" aria-current="page"')
    html=re.sub(r'<a href="'+re.escape(path)+r'" class=""', '<a href="'+path+'" class="active-link" aria-current="page"', html)
    destination = ROOT / ('index.html' if home else path.strip('/')+'/index.html')
    destination.parent.mkdir(parents=True,exist_ok=True);destination.write_text(html+'\n')
    if not noindex:PAGES.append((path,title,description))

def search_form(page=False):
    return f'''<div class="search-area" id="search"><form class="search-form" action="/search/" method="get" role="search"><label for="resource-search" class="sr-only">Search veterinary resources</label><div class="search-field">{icon('search')}<input id="resource-search" name="q" type="search" placeholder="Search notes, books, drugs, handbooks…" autocomplete="off" enterkeyhint="search" aria-describedby="search-help"><button type="submit" class="search-submit" aria-label="Search">{icon('arrow')}</button></div><div class="search-suggestions" id="search-suggestions" hidden><p class="suggestion-label">Suggested resources</p><p class="search-loading" hidden>Searching the library…</p><ul id="suggestion-list"></ul><p id="search-empty" class="search-empty" hidden>No match yet. {link('/request-resource/','Request a resource →')}</p></div></form><p class="search-examples" id="search-help">Try {link('/search/#preset-pharmacology','Pharmacology')}{link('/search/#preset-haemonchus','Haemonchus')}{link('/search/#preset-nsaids','NSAIDs')}{link('/search/#preset-surgery-books','Surgery books')}</p>{section_aside('search')}<p id="search-status" class="{"search-count" if page else "sr-only"}" role="status" aria-live="polite"></p></div>'''

def homepage():
    tabs=''.join(f'<a href="#year-{y}" class="year-tab" id="tab-{y}" data-year="{y}">{DATA["labels"][y]}</a>' for y in DATA['years'])
    panels=''
    for y,names in DATA['years'].items():
        rows=''.join(link('/bvsc/year-'+y+'/'+slug(name)+'/',f'<span class="subject-number">{i+1:02}</span><span>{escape(name)}</span>'+icon('arrow'),'subject-link') for i,name in enumerate(names))
        panels+=f'''<section class="year-panel" id="year-{y}" aria-labelledby="tab-{y}"><p class="year-summary">{DATA['descriptions'][y]}</p><div class="subject-list">{rows}</div><div class="year-footer"><span>{len(names)} subjects · notes & books</span>{link('/bvsc/year-'+y+'/','Explore '+DATA['labels'][y]+icon('arrow'),'text-link')}</div></section>'''
    objective=''
    for i,(key,title,desc,ic) in enumerate([
        ('icar-pyq','ICAR PYQ Question Bank','Start with past papers. Find the patterns, focus your revision.','paper'),
        ('objective-questions','Subject-wise Objective Questions','Practice the topics that matter most.','check'),
        ('objective-books','Objective Books','A focused shelf of trusted exam books.','book')]):
        count=len(library_pages.matching(sys.modules[__name__],key))
        desc=str(count)+' files from the Drive library' if count else 'Coming soon · Request Resource'
        destination=ROUTES[key] if count else '/request-resource/?collection='+key
        objective+=link(destination,f'<span class="row-icon">{icon(ic)}</span><div class="objective-copy"><h3>{title}</h3><p>{desc}</p></div>'+icon('arrow'),'objective-item')
    tools=''
    for key,title,desc,ic in [('free-apps','Useful Free Apps','Useful tools without unnecessary subscriptions.','phone'),('useful-tools','Useful Study Tools','Small, thoughtful tools for a smoother study day.','tools')]:
        tools+=link(ROUTES[key],icon(ic)+f'<div><h3>{title}</h3><p>{desc}</p></div>'+icon('arrow'),'tool-row')
    clinical=''
    for key,title,desc,ic in [('handbooks','Handbooks','','book'),('drug-index','Drug & Analgesic References','','pill'),('clinical-other','Other Clinical Resources','','cross')]:
        count=len(library_pages.matching(sys.modules[__name__],key))
        desc=str(count)+' files from the Drive library' if count else 'Coming soon · Request Resource'
        destination=ROUTES[key] if count else '/request-resource/?collection='+key
        clinical+=link(destination,icon(ic)+f'<div><h3>{title}</h3><p>{desc}</p></div>'+icon('arrow'),'clinical-row')
    body=f'''<section class="intro container"><div class="intro-heading"><div><h1>Free academic resources, thoughtfully made for future vets.</h1><p class="intro-description">Everything useful for veterinary study, organised in one place.</p></div></div>{search_form()}<div class="quick-tiles">{link('/bvsc/',icon('book')+'Notes')}{link('/objective/#icar-pyq',icon('paper')+'PYQs')}{link('/study-tools/',icon('tools')+'Tools')}{link('/clinical/',icon('cross')+'Clinical')}</div></section>
<section class="section container" id="notes">{section_heading('BVSc Notes <em>& Books</em>','Subject-wise study material organised by professional year.',link('/bvsc/','All subjects '+icon('arrow'),'text-link section-link'))}<div class="academic-library"><div class="year-tabs" aria-label="Choose a professional year">{tabs}<span class="tab-indicator" aria-hidden="true"></span></div><div class="year-panels">{panels}</div></div>{section_aside("bvsc")}</section>
<section class="section container objective-section" id="objective"><div class="section-panel panel-objective">{section_heading('Objective Resources','PYQs, subject-wise objective material and important veterinary objective books.')}{section_aside('objective')}<div class="objective-list">{objective}</div></div></section>

<section class="section container" id="tools"><div class="section-panel panel-tools">{section_heading('Tips & Tools <em>for Vet Study</em>','Thoughtful tools and practical guides for the everyday work of learning.')}<div class="study-layout">{link(ROUTES['ai-guide'],'<span class="kicker">A practical guide</span><h3>Use of AI <br>for Vet Study</h3><p>Practical ways to use AI for notes, research and presentations.</p>'+section_aside('tools')+'<span class="button">Read the guide '+icon('arrow')+'</span><span class="ai-mark" aria-hidden="true">'+icon('spark')+'</span>','ai-guide')}<div class="tool-rows">{tools}</div></div></div></section>
<section class="section container" id="clinical"><div class="section-panel panel-clinical"><div class="clinical-layout"><div class="clinical-heading"><h2>Clinical <em>Resources</em></h2><p>A place for trusted handbooks and practical references. Keep the essentials close.</p></div><div class="clinical-list">{clinical}</div></div>{section_aside("clinical")}</div></section>
<section class="section container" id="backbench"><div class="revision-note"><div class="revision-heading"><p class="kicker">For the night before</p><h2>Backbenchers <em>Corner</em></h2><p class="revision-motto">Less to read. More to remember.</p>{section_aside("backbench")}</div><div class="revision-body"><span class="note-tag">Keep this one handy</span><p>A collection of <strong>concise veterinary short notes</strong> for objective questions and short answers.</p>{link('https://t.me/vetshortnotesbytvg','Open Short Notes '+icon('arrow'),'button',True)}<span class="telegram-caption">{icon('telegram')} The short-notes collection on Telegram</span></div><span class="revision-paw" aria-hidden="true">{icon('paw')}</span></div></section>
<section class="section container" id="telegram-updates"><div class="jobs-strip section-panel panel-jobs"><span class="telegram-symbol">{icon('telegram')}</span><div><p class="kicker">Beyond the classroom</p><h2>Veterinary opportunities, <br>without the hunt.</h2><p>Government, private, internship and veterinary job updates — gathered in one place.</p>{link('https://t.me/jobupdatesbytvg',icon('telegram')+'Follow Job Updates '+icon('external'),'jobs-link',True)}{section_aside('jobs')}</div></div></section>
<section class="container request-section" id="request"><div><h2>Can’t find what you need?</h2><p>Request a note, book, PYQ or useful resource. Help shape the library.</p></div>{link('/request-resource/','Request Resource '+icon('arrow'),'button secondary')}{section_aside('request')}</section>'''
    items=[('BVSc Notes & Books','/bvsc/'),('Objective Resources','/objective/'),('Tips & Tools for Vet Study','/study-tools/'),('Clinical Resources','/clinical/'),('Backbenchers Corner','https://t.me/vetshortnotesbytvg'),('Veterinary Job Updates','https://t.me/jobupdatesbytvg')]
    write_page('/','Free Veterinary Notes, Books & Study Resources | ThatVetGuy',DESCRIPTION,body,items,True)

def article_intro(title, description):
    description=next((m['summary'] for p,m in geo.META.items() if p!='/' and ((p=='/bvsc/' and title=='BVSc Notes & Books') or (p=='/objective/' and title=='Objective Resources') or (p=='/study-tools/' and title=='Tips & Tools for Vet Study') or (p=='/clinical/' and title=='Clinical Resources') or (p=='/about/' and title=='About Notes.ThatVetGuy') or (p=='/search/' and title=='Search veterinary resources') or (p=='/request-resource/' and title=='Can’t find what you need?'))),description)
    return '<div class="container reading-page"><nav class="breadcrumbs" aria-label="Breadcrumb">'+link('/','Home')+'<span aria-hidden="true">/</span><span>'+escape(title)+'</span></nav><header class="reading-header"><h1>'+escape(title)+'</h1><p>'+escape(description)+'</p></header>'

def inside_pages():
    library_pages.render(sys.modules[__name__])

def not_found():
    body=article_intro('Page not found','This address does not lead to a page in the veterinary library. Search the notes or return to your professional year.')+section_aside('404')+link('/search/','Search resources','button secondary')+link('/bvsc/','Browse BVSc notes','button secondary')+'</div>'
    geo.META['/404/']={'faq':[['Where should I go instead?','Use search or browse the four professional years to find a subject.']]}
    write_page('/404/','Page not found','Find your way back to Notes.ThatVetGuy.',body,noindex=True)
    (ROOT/'404.html').write_text((ROOT/'404/index.html').read_text())

def discovery_files():
    catalogue=[]
    for r in RECORDS:
        catalogue.append({k:r.get(k) for k in ['id','title','subject','year','type','format','group','source','sourceCredit','path','url','permalink']})
    for y,names in DATA['years'].items():
        for name in names:catalogue.append({'id':slug(name),'title':name,'subject':DATA['labels'][y],'year':int(y),'type':'Subject','source':'Notes.ThatVetGuy','description':SUBJECTS[name]['summary'],'url':'/bvsc/year-'+y+'/'+slug(name)+'/','path':name,'keywords':name})
    geo.discovery(DATA['lastChecked'],catalogue)
    (ROOT/'build-info.json').write_text(json.dumps({'build':VERSION,'files':len(RECORDS),'manifestSource':LIBRARY['source'],'lastInspected':LIBRARY['lastInspected']})+'\n')
    for stale in (ROOT/'bvsc').glob('year-*/**/index.html'):
        route='/'+str(stale.parent.relative_to(ROOT))+'/'
        if route not in geo.PAGES:
            stale.unlink();stale.with_suffix('.md').unlink(missing_ok=True)
    (ROOT/'.nojekyll').touch()

if __name__=='__main__':
    homepage();inside_pages();not_found();discovery_files()
    print(f'Built {len(geo.PAGES)} routes from {len(RECORDS)} verified Drive files, with search and machine mirrors.')

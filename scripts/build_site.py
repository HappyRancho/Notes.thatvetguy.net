"""Static renderer. Source data stays independent of presentation."""
from pathlib import Path
from html import escape
import hashlib,json,re,sys,os
from library import build_library,slug
from library_views import keep_complete_resource
from ui import icon,link
import geo,site_shell,library_pages,homepage,breadcrumbs
ROOT=Path(__file__).resolve().parent.parent
LIBRARY=build_library(refresh=bool(os.getenv('DRIVE_API_KEY')))
for _year in LIBRARY['years']:
    _visible=0
    for _subject in _year['subjects']:
        _rows=[r for r in LIBRARY['files'] if r['id'] in _subject['resourceIds'] and keep_complete_resource(r)]
        _subject['count']=len(_rows)
        _subject['groups']={k:sum(r['kind']==k for r in _rows) for k in set(r['kind'] for r in _rows)}
        _visible+=len(_rows)
    _year['count']=_visible
RECORDS=LIBRARY['files'];CATALOGUE={r['id']:r for r in RECORDS}
DATA=json.loads((ROOT/'data/site-content.json').read_text())
SUBJECTS=json.loads((ROOT/'data/subjects.json').read_text())
MICROCOPY=json.loads((ROOT/'data/microcopy.json').read_text())
DATA['lastChecked']=LIBRARY['lastInspected']
BASE='https://notes.thatvetguy.net'
ROUTES={'ai-guide':'/study-tools/veterinary-careers/','free-apps':'/study-tools/vet-apps/','useful-tools':'/study-tools/online-resources/','icar-pyq':'/objective/#icar-pyq','objective-questions':'/objective/#subject-wise','objective-books':'/objective/#books','handbooks':'/clinical/handbooks/','drug-index':'/clinical/drug-index/','clinical-other':'/#clinical'}
# One cacheable request for the shared Rx styles, in their original cascade order.
(ROOT/'assets/rx-core.css').write_text('\n'.join((ROOT/'assets'/name).read_text() for name in ['site.css','rx-pages.css','homepage.css']))
(ROOT/'assets/rx-tools.css').write_text((ROOT/'assets/rx-core.css').read_text()+'\n'+(ROOT/'assets/study-tools.css').read_text())
VERSION=hashlib.sha256(b''.join(p.read_bytes() for p in sorted([* (ROOT/'scripts').glob('*.py'),*(ROOT/'assets').glob('*.css'),*(ROOT/'assets').glob('*.js'),ROOT/'data/resources.json',ROOT/'data/study-tools.json',ROOT/'data/career-guidance.json']))).hexdigest()[:12]
def section_aside(key,variant=0):return '<p class="margin-note"><span aria-hidden="true">↳</span> '+escape(MICROCOPY[key][variant])+'</p>'
def article_intro(title,description,crumbs=None):
    crumbs=crumbs or []
    breadcrumb=link('/','Home')+''.join('<span aria-hidden="true">/</span>'+link(u,escape(n)) for n,u in crumbs)
    from homepage import subject_icon
    ic,tone=subject_icon(title)
    if title.startswith('BVSc'):ic,tone='cap','mint'
    elif 'Objective' in title:ic,tone='target','sky'
    elif 'Clinical' in title:ic,tone='stethoscope','mint'
    elif 'Tools' in title:ic,tone='bulb','yellow'
    elif 'find' in title.lower():ic,tone='search','sky'
    return '<div class="container reading-page"><nav class="breadcrumbs" aria-label="Breadcrumb">'+breadcrumb+'<span aria-hidden="true">/</span><span>'+escape(title)+'</span></nav><header class="reading-header rx-section"><div class="rx-page-title"><span class="rx-row-icon '+tone+'">'+icon(ic)+'</span><h1>'+escape(title)+'</h1></div><p>'+escape(description)+'</p></header>'

def search_form(page=False):return site_shell.search(sys.modules[__name__],page)
def write_page(path,title,description,body,items=None,home=False,noindex=False,mirror_body=None):
    if not home:
        trail=breadcrumbs.render(breadcrumbs.trail(path,title,geo.PAGES))
        if not re.search(r'<nav class="breadcrumbs"[^>]*>.*?</nav>',body,flags=re.S):
            raise ValueError('Missing breadcrumb insertion point: '+path)
        body=re.sub(r'<nav class="breadcrumbs"[^>]*>.*?</nav>',lambda _:trail,body,count=1,flags=re.S)
    body=geo.heading_ids(geo.external_links(body)+geo.faq_html(path));date=DATA['lastChecked']
    search_meta=geo.SEARCH_META.get(path,{})
    description=search_meta.get('description',description)
    page_title=search_meta.get('title',title if home else title+' | Notes.ThatVetGuy')
    modified=geo.page_modified(path,page_title,description,body)
    geo.register(path,title,description,mirror_body if mirror_body is not None else body,modified,DATA['lastChecked'],noindex=noindex);social=geo.social(path)
    schema=geo.structured(path,title,description,items,home,body,RECORDS,modified)
    light,dark=('#eaf8ff','#112433')
    fast_shell=home or path=='/search/' or path.startswith('/study-tools/')
    core_style='rx-tools.css' if path.startswith('/study-tools/') else ('rx-core.css' if fast_shell else 'site.css')
    theme_boot='<script>'+ (ROOT/'assets/theme.js').read_text().strip()+'</script>' if fast_shell else f'<script src="/assets/theme.js?v={VERSION}"></script>'
    extra_assets='' if fast_shell else f'<link rel="stylesheet" href="/assets/rx-pages.css?v={VERSION}"><link rel="stylesheet" href="/assets/homepage.css?v={VERSION}">'
    if path in ['/objective/','/clinical/drug-index/','/clinical/handbooks/']:extra_assets+=f'<link rel="stylesheet" href="/assets/collections.css?v={VERSION}">'
    if path=='/bvsc/' or re.fullmatch(r'/bvsc/year-[1-4]/(?:notes/)?',path):extra_assets+=f'<link rel="stylesheet" href="/assets/year-hubs.css?v={VERSION}">'
    if re.fullmatch(r'/bvsc/year-[1-4]/',path):extra_assets+=f'<link rel="stylesheet" href="/assets/year-pages.css?v={VERSION}">'
    if re.fullmatch(r'/bvsc/year-[1-4]/roadmap/',path):extra_assets+=f'<link rel="stylesheet" href="/assets/roadmaps.css?v={VERSION}">'
    if path.startswith('/study-tools/'):
        extra_assets+=f'<script src="/assets/study-tools.js?v={VERSION}" defer></script>'
    if path=='/search/':extra_assets+=f'<link rel="stylesheet" href="/assets/search-page.css?v={VERSION}">'
    if path.startswith('/books/'):extra_assets+=f'<link rel="stylesheet" href="/assets/books.css?v={VERSION}">'
    if path.startswith('/bvsc/'):extra_assets+=f'<link rel="stylesheet" href="/assets/academic-pages.css?v={VERSION}">'
    extra_assets+=f'<script src="/assets/homepage.js?v={VERSION}" defer></script>'
    if 'subject-hub' in body or 'data-syllabus=' in body or 'practical-vault' in body:extra_assets+=f'<link rel="stylesheet" href="/assets/subject-hub.css?v={VERSION}">'
    if 'data-syllabus=' in body:extra_assets+=f'<script src="/assets/syllabus-checklist.js?v={VERSION}" defer></script>'
    reader_script=f'<script src="/assets/subject-reader.js?v={VERSION}" defer></script>' if 'data-subject-reader' in body else ''
    preload='balsamiq'
    page_header=homepage.header(path,home)
    page_footer=homepage.footer()
    font_preload= '<link rel="preload" href="/assets/fonts/inter-latin.woff2" as="font" type="font/woff2" crossorigin>'
    if fast_shell:
        font_preload+='<link rel="preload" href="/assets/fonts/caveat-latin.woff2" as="font" type="font/woff2" crossorigin>'
    if re.fullmatch(r'/bvsc/year-[1-4]/',path):font_preload+='<link rel="preload" href="/assets/fonts/caveat-latin.woff2" as="font" type="font/woff2" crossorigin>'
    if re.fullmatch(r'/bvsc/year-[1-4]/roadmap/',path):font_preload+='<link rel="preload" href="/assets/fonts/caveat-latin.woff2" as="font" type="font/woff2" crossorigin>'
    page_search=''
    html=f'''<!doctype html><html lang="en" data-ui="rx"><head>
<meta charset="utf-8"><meta name="site-build" content="{VERSION}"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(page_title)}</title><meta name="description" content="{escape(description,quote=True)}">
<meta name="theme-color" content="{light}" media="(prefers-color-scheme: light)"><meta name="theme-color" content="{dark}" media="(prefers-color-scheme: dark)">
<link rel="preload" href="/assets/fonts/{preload}-latin.woff2" as="font" type="font/woff2" crossorigin>{font_preload}
{theme_boot}<meta name="robots" content="{'noindex,follow' if noindex else 'index,follow,max-image-preview:large'}">
<link rel="canonical" href="{BASE+path}"><link rel="alternate" type="text/markdown" href="{BASE+path}index.md" title="Markdown version"><link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<meta property="og:type" content="website"><meta property="og:site_name" content="Notes.ThatVetGuy"><meta property="og:title" content="{escape(page_title,quote=True)}"><meta property="og:description" content="{escape(description,quote=True)}"><meta property="og:url" content="{BASE+path}"><meta property="og:image" content="{BASE+social}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="{escape(title,quote=True)} — Rx Notes by ThatVetGuy">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{escape(page_title,quote=True)}"><meta name="twitter:description" content="{escape(description,quote=True)}"><meta name="twitter:image" content="{BASE+social}">
<link rel="stylesheet" href="/assets/{core_style}?v={VERSION}">{extra_assets}
<script type="application/ld+json">{schema}</script><script src="/assets/logic.js?v={VERSION}" defer></script><script src="/assets/site.js?v={VERSION}" defer></script><script src="/assets/motion.js?v={VERSION}" defer></script>{reader_script}
</head><body class="mockup-home{' rx-inner' if not home else ''}{' rx-academic' if path.startswith('/bvsc/') else ''}">{page_header}<main id="main">{page_search}{body}</main>{page_footer}{site_shell.navigation(path)}{site_shell.palette()}</body></html>'''
    dest=ROOT/path.strip('/')/'index.html';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(html+'\n')
def discovery():
    index=[]
    # Keep the public catalogue aligned with subject pages: topic slide decks and
    # presentation exports remain accounted for in the source manifest, but are
    # not discoverable as complete subject material.
    for r in RECORDS:
        if not keep_complete_resource(r):
            continue
        item={k:r.get(k) for k in ['id','title','subject','year','type','format','kind','group','path','permalink','keywords']};item['fileIds']=r.get('searchFileIds') or (r['photoIds'] or [v['id'] for v in r['variants']])+r['duplicateIds'];item['url']=r['permalink'];item['subject']=item['subject'] or 'Year '+str(r['year'])+' extras';index.append(item)
    from book_catalogue import books as book_registry
    for book in book_registry():
        if not book.get('resourceId') and book.get('primaryUrl'):index.append(dict(id='book-guide-'+book['id'],title=book['title'],subject=', '.join(s['name'] for s in book['subjects']),year=book['subjects'][0]['year'] if book['subjects'] else None,type='Book',format='Guide',kind='books',group='Books',path='Books/'+book['title'],permalink=book['page'],url=book['page'],fileIds=[],keywords=[book['title'],book.get('author') or '', 'Books']))
    from syllabus_pages import DATA as SYLLABI,checklist_url
    for subject in SYLLABI['subjects']:
        route=checklist_url(subject['year'],subject['subject']);index.append(dict(id='syllabus-'+subject['slug'],title=subject['subject']+' Syllabus Checklist',subject=subject['subject'],year=subject['year'],type='Syllabus',format='Checklist',kind='other',group='Syllabus',path='Syllabus/'+subject['subject'],permalink=route,url=route,fileIds=[],keywords=[subject['subject'],'syllabus','course outline','checklist']))
    from study_tools import GUIDES,route as tool_route
    for guide in GUIDES:
        u=tool_route(guide);index.append(dict(id='study-guide-'+guide['id'],title=guide['title'],subject='Study Tools',year=None,type='Guide',format='Guide',kind='other',group='Study Tools',path='Study Tools/'+guide['title'],permalink=u,url=u,fileIds=[],keywords=[guide['title'],guide['description'],'study tools']))
    geo.discovery(DATA['lastChecked'],index)
    (ROOT/'build-info.json').write_text(json.dumps({'build':VERSION,'resources':len(RECORDS),'rawFiles':LIBRARY['stats']['rawFiles'],'lastInspected':LIBRARY['lastInspected']})+'\n')
    for stale in (ROOT/'bvsc').rglob('index.html'):
        route='/'+str(stale.parent.relative_to(ROOT))+'/'
        if route not in geo.PAGES:stale.unlink();stale.with_suffix('.md').unlink(missing_ok=True)
    for stale in (ROOT/'books').rglob('index.html'):
        route='/'+str(stale.parent.relative_to(ROOT))+'/'
        if route not in geo.PAGES:stale.unlink();stale.with_suffix('.md').unlink(missing_ok=True)
    # Clinical collections remain available; the old landing page returns to the home section.
    for retired in ['clinical/index.html','clinical/index.md']:(ROOT/retired).unlink(missing_ok=True)
    # Retired overview/subject URLs retain useful destinations, including file hashes.
    redirects=ROOT/'_redirects';text=redirects.read_text() if redirects.exists() else ''
    lines=[line for line in text.splitlines() if not line.startswith(('/bvsc/','/clinical/ '))]
    for y in LIBRARY['years']:
        base='/bvsc/year-'+str(y['year'])+'/'
        lines.append(base+'books/ '+base+'#books 301')
        for subject in y['subjects']:
            ss=subject['slug']
            lines.append('/bvsc/'+ss+'/ '+base+ss+'/ 301')
    lines.append('/clinical/ /#clinical 301')
    for y in [2,4]:lines.append('/bvsc/year-'+str(y)+'/unsorted/ /bvsc/year-'+str(y)+'/ 301')
    redirects.write_text('\n'.join(lines)+'\n');(ROOT/'.nojekyll').touch()
def run():
    b=sys.modules[__name__];homepage.render(b);library_pages.render(b)
    from book_pages import render as render_books
    render_books(b)
    from syllabus_pages import render as render_syllabi
    render_syllabi(b)
    from practical_pages import render as render_practicals
    render_practicals(b)
    body=article_intro(MICROCOPY['404'][0],'Try a subject or search for the resource you need.')+link('/bvsc/','Back to the notes '+icon('arrow'),'button')+'</div>'
    write_page('/404/','Page not found','Find your way back to veterinary notes, books and study resources.',body,noindex=True)
    (ROOT/'404.html').write_text((ROOT/'404/index.html').read_text());discovery()
    print(f'Built {len(geo.PAGES)} pages, {len(RECORDS)} resource rows; source links organised by year, subject and unit.')
if __name__=='__main__':run()

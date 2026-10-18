"""Static renderer. Source data stays independent of presentation."""
from pathlib import Path
from html import escape
import hashlib,json,re,sys,os
from library import build_library,slug
from library_views import keep_complete_resource
from ui import icon,link
import geo,site_shell,library_pages,homepage
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
ROUTES={'ai-guide':'/study-tools/#ai-guide','free-apps':'/study-tools/#free-apps','useful-tools':'/study-tools/#useful-tools','icar-pyq':'/objective/#icar-pyq','objective-questions':'/objective/#subject-wise','objective-books':'/objective/#books','handbooks':'/clinical/#handbooks','drug-index':'/clinical/#drug-index','clinical-other':'/clinical/#other-resources'}
VERSION=hashlib.sha256(b''.join(p.read_bytes() for p in sorted([* (ROOT/'scripts').glob('*.py'),*(ROOT/'assets').glob('*.css'),*(ROOT/'assets').glob('*.js'),ROOT/'data/resources.json']))).hexdigest()[:12]
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
    body=geo.heading_ids(geo.external_links(body)+geo.faq_html(path));date=DATA['lastChecked']
    modified=LIBRARY['lastInspected']
    geo.register(path,title,description,mirror_body if mirror_body is not None else body,modified);social=geo.social(path);page_title=title if home else title+' | Notes.ThatVetGuy'
    schema=geo.structured(path,title,description,items,home,body,RECORDS,modified)
    light,dark=('#eaf8ff','#112433')
    extra_assets=f'<link rel="stylesheet" href="/assets/rx-pages.css?v={VERSION}"><link rel="stylesheet" href="/assets/homepage.css?v={VERSION}">'
    if path in ['/objective/','/clinical/drug-index/']:extra_assets+=f'<link rel="stylesheet" href="/assets/collections.css?v={VERSION}">'
    if re.fullmatch(r'/bvsc/year-[1-4]/(?:notes/)?',path):extra_assets+=f'<link rel="stylesheet" href="/assets/year-hubs.css?v={VERSION}">'
    extra_assets+=f'<script src="/assets/homepage.js?v={VERSION}" defer></script>'
    preload='balsamiq'
    page_header=homepage.header(path,home)
    page_footer=homepage.footer()
    font_preload='' if home else '<link rel="preload" href="/assets/fonts/inter-latin.woff2" as="font" type="font/woff2" crossorigin>'
    page_search=''
    html=f'''<!doctype html><html lang="en" data-ui="rx"><head>
<meta charset="utf-8"><meta name="site-build" content="{VERSION}"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(page_title)}</title><meta name="description" content="{escape(description,quote=True)}">
<meta name="theme-color" content="{light}" media="(prefers-color-scheme: light)"><meta name="theme-color" content="{dark}" media="(prefers-color-scheme: dark)">
<script src="/assets/theme.js?v={VERSION}"></script><meta name="robots" content="{'noindex,follow' if noindex else 'index,follow,max-image-preview:large'}">
<link rel="canonical" href="{BASE+path}"><link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<meta property="og:type" content="website"><meta property="og:site_name" content="Notes.ThatVetGuy"><meta property="og:title" content="{escape(page_title,quote=True)}"><meta property="og:description" content="{escape(description,quote=True)}"><meta property="og:url" content="{BASE+path}"><meta property="og:image" content="{BASE+social}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="Notes.ThatVetGuy — Vet school notes, sorted.">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{escape(page_title,quote=True)}"><meta name="twitter:description" content="{escape(description,quote=True)}"><meta name="twitter:image" content="{BASE+social}">
<link rel="stylesheet" href="/assets/site.css?v={VERSION}">{extra_assets}<link rel="preload" href="/assets/fonts/{preload}-latin.woff2" as="font" type="font/woff2" crossorigin>{font_preload}
<script type="application/ld+json">{schema}</script><script src="/assets/logic.js?v={VERSION}" defer></script><script src="/assets/site.js?v={VERSION}" defer></script><script src="/assets/motion.js?v={VERSION}" defer></script>
</head><body class="mockup-home{' rx-inner' if not home else ''}">{page_header}<main id="main">{page_search}{body}<div class="container page-checked">Last checked: <time datetime="{date}">{date}</time></div></main>{page_footer}{site_shell.navigation(path)}{site_shell.palette()}</body></html>'''
    dest=ROOT/path.strip('/')/'index.html';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(html+'\n')
def discovery():
    index=[]
    # Keep the public catalogue aligned with subject pages: topic slide decks and
    # presentation exports remain accounted for in the source manifest, but are
    # not discoverable as complete subject material.
    for r in RECORDS:
        if not keep_complete_resource(r):
            continue
        item={k:r.get(k) for k in ['id','title','subject','year','type','format','kind','group','path','permalink']};item['fileIds']=(r['photoIds'] or [v['id'] for v in r['variants']])+r['duplicateIds'];item['url']=r['permalink'];item['subject']=item['subject'] or 'Year '+str(r['year'])+' extras';index.append(item)
    geo.discovery(DATA['lastChecked'],index)
    (ROOT/'build-info.json').write_text(json.dumps({'build':VERSION,'resources':len(RECORDS),'rawFiles':LIBRARY['stats']['rawFiles'],'lastInspected':LIBRARY['lastInspected']})+'\n')
    for stale in (ROOT/'bvsc').rglob('index.html'):
        route='/'+str(stale.parent.relative_to(ROOT))+'/'
        if route not in geo.PAGES:stale.unlink();stale.with_suffix('.md').unlink(missing_ok=True)
    # Retired overview/subject URLs retain useful destinations, including file hashes.
    redirects=ROOT/'_redirects';text=redirects.read_text() if redirects.exists() else ''
    lines=[line for line in text.splitlines() if not line.startswith('/bvsc/')]
    for y in LIBRARY['years']:
        base='/bvsc/year-'+str(y['year'])+'/'
        lines.append(base+'books/ '+base+'#books 301')
        for subject in y['subjects']:
            ss=subject['slug']
            lines.extend(['/bvsc/'+ss+'/ '+base+'#'+ss+' 301',base+ss+'/ '+base+'notes/ 301'])
    for y in [2,4]:lines.append('/bvsc/year-'+str(y)+'/unsorted/ /bvsc/year-'+str(y)+'/ 301')
    redirects.write_text('\n'.join(lines)+'\n');(ROOT/'.nojekyll').touch()
def run():
    b=sys.modules[__name__];homepage.render(b);library_pages.render(b)
    body=article_intro(MICROCOPY['404'][0],'Try a subject or search for the resource you need.')+link('/bvsc/','Back to the notes '+icon('arrow'),'button')+'</div>'
    write_page('/404/','Page not found','Find your way back to veterinary notes, books and study resources.',body,noindex=True)
    (ROOT/'404.html').write_text((ROOT/'404/index.html').read_text());discovery()
    print(f'Built {len(geo.PAGES)} pages, {len(RECORDS)} resource rows; source links organised by year, subject and unit.')
if __name__=='__main__':run()

"""Shared navigation, search and compact homepage compositions."""
from html import escape as e
from ui import icon,link

def header(path):
    nav=''
    for url,title in [('/bvsc/','Notes & Books'),('/objective/','Objective'),('/study-tools/','Study Tools'),('/#clinical','Clinical')]:
        active=' aria-current="page"' if (path.startswith(url) or url=='/#clinical' and path.startswith('/clinical/')) else ''
        nav+=f'<a class="nav-link" href="{url}"{active}>{title}</a>'
    return '<a class="skip-link" href="#main">Skip to content</a><header class="site-header"><div class="container header-inner">'+link('/',icon('paw')+'<span>Notes.<b>ThatVetGuy</b></span>','brand')+'<nav class="desktop-nav" aria-label="Main">'+nav+'</nav><div class="header-actions">'+link('/search/',icon('search')+'<span class="sr-only">Search resources</span>','icon-button header-search command-trigger')+'<button class="icon-button theme-toggle js-only" type="button" aria-label="Switch to dark theme" aria-pressed="false"><span aria-hidden="true">◐</span></button></div></div></header>'

def navigation(path):
    links=''
    home=path=='/'
    for url,title,ic in [('/','Home','home'),('/bvsc/','Notes','paper'),('/objective/','Objective','cap'),('/search/','Search','search')]:
        active=' aria-current="page"' if (path==url or url!="/" and path.startswith(url)) else ''
        links+=f'<a href="{url}"{active}>'+icon(ic)+'<span>'+title+'</span></a>'
    def tile(url, title, detail, glyph, tone):
        return link(url, '<span class="menu-icon">'+icon(glyph)+'</span><span><strong>'+title+'</strong><small>'+detail+'</small></span>'+icon('chevron'), 'menu-tile '+tone)
    def group(title, content):
        return '<section class="menu-group"><h3>'+title+'</h3><div class="menu-grid">'+content+'</div></section>'
    study=tile('/bvsc/','Notes &amp; Books','All four BVSc years','book','menu-sky')+tile('/objective/','Objective','Notes &amp; question banks','cap','menu-yellow')+tile('/study-tools/','Year roadmaps','Plan your studies','map','menu-mint menu-wide')
    clinical=tile('/clinical/drug-index/','Drug Index','Quick references','pill','menu-sky')+tile('/clinical/handbooks/','Handbooks','Clinical reading','stethoscope','menu-mint')
    study_tools=tile('/study-tools/vet-apps/','Vet Apps','For students','phone','menu-sky')+tile('/study-tools/online-resources/','Notes Websites','Find trusted sources','chain','menu-lilac')+tile('/study-tools/veterinary-careers/','Explore Vet Career Options','Find your path after BVSc','map','menu-peach menu-wide')
    support=[('/about/','About Rx Notes','paw'),('/request-resource/','Request a resource','message'),('/request-resource/#contribute','Contribute','people'),('/request-resource/#report','Report an error','shield'),('https://t.me/vetshortnotesbytvg','Short notes channel','paper'),('https://t.me/jobupdatesbytvg','Vet job updates','megaphone')]
    community='<details class="menu-support"><summary>'+icon('people')+'<span>Community &amp; support</span>'+icon('chevron')+'</summary><div class="menu-support-links">'+''.join(link(u,icon(g)+'<span>'+t+'</span>'+icon('arrow')) for u,t,g in support)+'</div></details>'
    theme='<div class="rx-theme-option"><span>Appearance <small>Light / dark</small></span><button class="icon-button theme-toggle js-only" type="button" aria-label="Switch to dark theme" aria-pressed="false"><span aria-hidden="true">◐</span></button></div>'
    menu='<nav class="menu-content" aria-label="Resources and information">'+link('/search/',icon('search')+'<span>Find a note, book or resource</span>'+icon('arrow'),'menu-search')+group('Study &amp; revise',study)+group('Clinical references',clinical)+group('Student toolkit',study_tools)+community+'</nav>'
    return '<nav class="bottom-nav" aria-label="Mobile">'+links+'<button type="button" class="js-only" data-dialog="more-sheet" aria-controls="more-sheet" aria-expanded="false">'+icon('menu')+'<span>More</span></button><a class="nojs-only" href="/about/">About</a></nav><dialog id="more-sheet" class="sheet" aria-labelledby="more-title"><div class="dialog-head"><div><h2 id="more-title" class="dialog-title">Explore Rx Notes</h2><p class="menu-intro">Your next useful resource, a tap away.</p></div><button class="icon-button" data-close aria-label="Close menu">'+icon('close')+'</button></div>'+menu+theme+'</dialog>'

def palette():
    return '<dialog id="command-palette" class="sheet command-dialog" aria-labelledby="command-title"><div class="dialog-head"><div id="command-title" class="dialog-title">Find your next read.</div><button class="icon-button" data-close aria-label="Close search">'+icon('close')+'</button></div><label class="sr-only" for="command-search">Search all resources</label><input id="command-search" type="search" placeholder="Subject, note, book…" autocomplete="off"><p class="search-loading" hidden>Searching…</p><ul id="command-results" class="suggestion-list"></ul><p id="command-status" role="status"></p></dialog>'

def footer(b):
    from homepage import footer as rx_footer
    return rx_footer()

def search(b,page=False):
    return '<div class="search-area"><form class="search-form" action="/search/" method="get" role="search"><label for="resource-search" class="sr-only">Search veterinary resources</label><div class="search-field">'+icon('search')+'<input id="resource-search" type="search" name="q" placeholder="Search notes, books, topics…" autocomplete="off" enterkeyhint="search"><kbd class="search-shortcut" aria-hidden="true">/</kbd><button class="icon-button search-submit" aria-label="Search" type="submit">'+icon('arrow')+'</button></div><div id="search-suggestions" class="search-suggestions" hidden><p class="search-loading" hidden>Searching…</p><ul id="suggestion-list" class="suggestion-list"></ul></div></form><p id="search-status" role="status" class="'+('search-count' if page else 'sr-only')+'"></p></div>'

def year_tiles(b):
    tiles=''
    for y,tone in zip(b.LIBRARY['years'],['yellow','peach','sky','mint']):
        n=y['year'];label=b.DATA['labels'][str(n)]
        tiles+=link('/bvsc/year-'+str(n)+'/', '<span class="year-top"><span class="rx-row-icon '+tone+'">'+str(n)+'</span>'+icon('chevron')+'</span><strong class="year-numeral">'+label+'</strong><span class="year-meta">'+str(len(y['subjects']))+' subjects · '+format(y['count'],',')+' resources</span>', 'year-tile')
    return '<div class="year-grid">'+tiles+'</div>'

def home(b):
    from homepage import render
    render(b)

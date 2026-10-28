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
    more=[('/about/','About'),('/request-resource/','Request Resource'),('/request-resource/#contribute','Contribute'),('/request-resource/#report','Report an error'),('https://t.me/vetshortnotesbytvg','Short notes on Telegram'),('https://t.me/jobupdatesbytvg','Job updates on Telegram')]
    more=[('/study-tools/vet-apps/','Vet Apps for Students'),('/study-tools/online-resources/','Top Vet Notes Websites'),('/study-tools/veterinary-careers/','Explore Vet Career Options'),('/clinical/drug-index/','Drug Index'),('/clinical/handbooks/','Handbooks'),('/study-tools/','Tools & Year Roadmaps')]+more
    theme='<div class="rx-theme-option"><span>Light / dark appearance</span><button class="icon-button theme-toggle js-only" type="button" aria-label="Switch to dark theme" aria-pressed="false"><span aria-hidden="true">◐</span></button></div>'
    return '<nav class="bottom-nav" aria-label="Mobile">'+links+'<button type="button" class="js-only" data-dialog="more-sheet" aria-controls="more-sheet" aria-expanded="false">'+icon('menu')+'<span>More</span></button><a class="nojs-only" href="/about/">About</a></nav><dialog id="more-sheet" class="sheet" aria-labelledby="more-title"><div class="dialog-head"><div id="more-title" class="dialog-title">A little more.</div><button class="icon-button" data-close aria-label="Close menu">'+icon('close')+'</button></div><nav class="more-links" aria-label="Community and information">'+''.join(link(u,t+icon('arrow')) for u,t in more)+'<button type="button" class="more-shelf-button js-only" data-dialog="personal-library" aria-controls="personal-library" aria-expanded="false">'+icon('book')+'<span>Saved &amp; recent</span>'+icon('arrow')+'</button></nav>'+theme+'</dialog>'

def palette():
    return '<dialog id="command-palette" class="sheet command-dialog" aria-labelledby="command-title"><div class="dialog-head"><div id="command-title" class="dialog-title">Find your next read.</div><button class="icon-button" data-close aria-label="Close search">'+icon('close')+'</button></div><label class="sr-only" for="command-search">Search all resources</label><input id="command-search" type="search" placeholder="Subject, note, book…" autocomplete="off"><p class="search-loading" hidden>Searching…</p><ul id="command-results" class="suggestion-list"></ul><p id="command-status" role="status"></p></dialog><dialog id="personal-library" class="sheet" aria-label="Saved and recently opened resources"><div class="dialog-head"><div class="dialog-title">Your study shelf</div><button class="icon-button" data-close aria-label="Close study shelf">'+icon('close')+'</button></div><div id="personal-content"></div></dialog>'

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

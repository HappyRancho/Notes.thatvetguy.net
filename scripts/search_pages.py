"""Search starts with real catalogue entries; presets remain usable without JS."""
from html import escape as e
from library_views import keep_complete_resource,teaser
from assets_index import find_preset

def render(b):
    rows=[r for r in b.RECORDS if keep_complete_resource(r)]
    body=b.article_intro('Find your next read.','Search veterinary notes, books, practical folders and syllabus checklists. Start with a subject or the title you need.').replace('container reading-page','container reading-page resource-search-page',1)
    body+='<section class="search-workspace" aria-label="Resource search">'+b.search_form(True)+'<div class="search-type-filters js-only" aria-label="Search resource types">'+''.join('<button type="button" data-search-kind="'+k+'" aria-pressed="'+str(i==0).lower()+'">'+t+'</button>' for i,(k,t) in enumerate([('all','All'),('notes','Notes'),('books','Books'),('practical','Practicals'),('syllabus','Syllabus')]))+'</div><div id="page-results" aria-busy="false"></div><section class="preset-results"><header><h2>A place to start</h2><p>Choose a subject. These collections already have resources.</p></header><nav class="preset-links" aria-label="Suggested searches">'
    presets=[(key,title,find_preset(title,rows)) for key,title in [('anatomy','Anatomy'),('pharmacology','Pharmacology'),('parasitology','Parasitology'),('surgery-books','Surgery books')]]
    body+=''.join(b.link('#preset-'+key,e(title),'filter-link') for key,title,own in presets if own)+'</nav>'
    for key,title,own in presets:
        if not own:continue
        body+='<details class="search-preset" id="preset-'+key+'"><summary><h3>'+e(title)+'</h3><span>'+str(len(own))+'</span>'+b.icon('chevron')+'</summary><div>'+''.join(teaser(b,r) for r in own[:3])+b.link('/search/?q='+__import__('urllib.parse',fromlist=['quote']).quote(title),'Search all '+e(title.lower())+' '+b.icon('arrow'),'js-only search-all')+'</div></details>'
    body+='</section></section><p class="search-help">Can’t find it? '+b.link('/request-resource/','Request a resource '+b.icon('arrow'))+'</p></div>'
    b.write_page('/search/','Search Veterinary Resources',b.geo.META['/search/']['summary'],body,noindex=True)

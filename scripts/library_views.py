"""One job per page: years, subjects, then bounded file groups."""
from html import escape as e
from collections import Counter
import re
from library import KINDS,natural,slug,normal
from site_shell import year_tiles

def count(n,word='resource'):return f'{n:,} {word}'+('' if n==1 else 's')
def keep_complete_resource(r):
    return r.get('public',True)
def size_label(n):
    if n is None:return ''
    return f'{n/1_000_000:.1f} MB' if n>=1_000_000 else f'{n/1000:.0f} KB'
def empty(b,text='Coming soon'):
    return '<div class="empty-state"><strong>'+e(text)+'</strong><p>'+e(b.MICROCOPY['empty'][0])+'</p>'+b.link('/request-resource/','Request a resource '+b.icon('arrow'),'button secondary')+'</div>'
def matching(b,category):return [r for r in b.RECORDS if category in r['collections'] and keep_complete_resource(r)]
def file_card(b,r):
    title=e(r['title']);rid=r['id'];description='<p class="resource-description">'+e(r['description'])+'</p>' if r['source']=='Telegram' else ''
    credit='<small class="resource-source">'+e(r.get('sourceCredit') or r['source'])+'</small>' if r.get('sourceCredit') else ''
    aliases=''.join('<span id="file-'+a+'" class="anchor-alias"></span>' for a in r['duplicateIds']+[v['id'] for v in r['variants'][1:]])
    return aliases+'<article class="file-row'+(' collection-resource' if description else '')+'" id="file-'+rid+'" data-resource-id="'+rid+'" data-kind="'+r['kind']+'" data-row-search="'+e(normal(r['title']+' '+r['path']),quote=True)+'"><span class="format-icon format-'+r['format'].lower()+'" aria-hidden="true">'+e(r['format'])+'</span><div class="file-title"><span title="'+e(r['name'],quote=True)+'">'+title+'</span>'+description+credit+'</div>'+b.link(r['url'],'<span class="open-label">Open</span>'+b.icon('external')+'<span class="sr-only"> '+title+'</span>','file-open')+'</article>'
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
def overview(b):
    from year_hubs import index,render
    index(b);render(b)

def collections(b):
    from homepage import tabs,panel
    from collection_cards import intro,cards
    desc=b.geo.META['/objective/']['summary'];body=intro(b,'Objective & Competition Resources',desc)
    books=matching(b,'objective-notes');banks=matching(b,'question-banks')
    book_body='<section id="books"><h2 class="sr-only">Objective Notes</h2>'+cards(b,books)+'</section>'
    bank_body='<section id="subject-wise"><h2 class="sr-only">Question Banks</h2>'+cards(b,banks)+'</section>'
    body+='<p class="source-note">Choose a collection below. Open a book for its details and Telegram download link.</p><section class="content-section rx-collection-page" data-home-tabs>'+tabs('objective-page',[(b.icon('book')+'<span>Objective Notes</span>','/objective/#books'),(b.icon('paper')+'<span>Question Banks</span>','/objective/#subject-wise')])+panel('objective-page',0,book_body)+panel('objective-page',1,bank_body)+'</section>'
    body+='<span id="icar-pyq" class="anchor-alias"></span></div>'
    b.write_page('/objective/','Objective & Competition Resources',desc,body,[(r['title'],r['page']) for r in books+banks])

def tools(b):
    from study_tools import render
    render(b)

def other(b):
    body=b.article_intro('About Notes.ThatVetGuy',b.geo.META['/about/']['summary'])+'<section class="content-section prose"><h2>A useful place to start.</h2><p>Pick your professional year, find a subject and get to the reading. Notes.ThatVetGuy brings notes, books and practical material together for veterinary students.</p><h2>People behind the pages</h2><p>Site guidance and summaries are by Dr. Chirag Patidar, BVSc & AH, MVSc. Linked materials retain their original authorship. Inclusion does not imply medical review or ownership.</p><h2>Help the next student</h2><p>A missing topic, a broken file or a credit that needs correcting: tell us so the library can get better.</p>'+b.link('/request-resource/','Request or report a resource '+b.icon('arrow'),'button secondary')+'</section></div>'
    b.write_page('/about/','About Notes.ThatVetGuy',b.geo.META['/about/']['summary'],body)
    body=b.article_intro('Can’t find what you need?',b.geo.META['/request-resource/']['summary'])+b.section_aside('request')+'<section class="content-section prose"><h2>Tell us what would help.</h2><p>Include the topic, subject, year and edition if relevant.</p><label for="request-file-id">File ID, if reporting a file</label><input id="request-file-id" class="request-input" name="file" type="text" autocomplete="off"><p id="request-context" role="status"></p>'+b.link('mailto:contact@thatvetguy.net?subject=Resource%20request','Email your request '+b.icon('arrow'),'button request-email')+'<p><!--email_off-->You can also copy <strong>contact@thatvetguy.net</strong> into your email app.<!--/email_off--></p></section>'
    for ident,title,text in [('contact','Contact','Send your question to contact@thatvetguy.net.'),('contribute','Contribute','Send the title, subject and original source credit. Share only material you have permission to contribute.'),('report','Report an error / takedown','Include the file ID or page URL, the issue and your contact details. For a takedown request, explain your connection to the material.')]:body+='<section class="content-section prose" id="'+ident+'"><h2>'+title+'</h2><p><!--email_off-->'+text+'<!--/email_off--></p></section>'
    b.write_page('/request-resource/','Request a Resource',b.geo.META['/request-resource/']['summary'],body+'</div>')
    from search_pages import render as search_render
    search_render(b)

def render(b):
    overview(b);collections(b);tools(b);other(b)
    from book_guides import render as book_render
    book_render(b)

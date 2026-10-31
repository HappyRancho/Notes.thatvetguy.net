"""Shared Rx collection headings and numbered, single-action book cards."""
from html import escape as e

def intro(b,title,description,crumbs=None,clinical=False,handbooks=False):
    html=b.article_intro(title,description,crumbs)
    variant=' rx-handbook-collection' if handbooks else ' rx-drug-collection' if clinical else ' rx-objective-collection'
    html=html.replace('container reading-page','container reading-page rx-collections'+variant,1)
    if handbooks:
        html=html.replace('</header>','<svg class="rx-collection-art" viewBox="20 94 244 158" width="244" height="158" aria-hidden="true" focusable="false"><defs><clipPath id="handbook-art-clip"><path d="M90 97 234 109 238 115 236 142 255 146 259 153 252 173 260 194 255 217 257 226 208 250 67 226 61 218 65 187 72 173 73 153 70 145 68 135 72 115 77 106Z"/><path d="m42 101 7-2 10 17-7 6Zm-17 20 20 3-1 10-20-4Zm3 18 18-4 3 10-19 7Z"/></clipPath></defs><image href="/assets/collections/handbook-reference.png" width="312" height="295" clip-path="url(#handbook-art-clip)"/></svg></header>',1)
    if clinical:
        warning='<svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m12 3 10 18H2Z"/><path d="M12 9v5m0 3h.01"/></svg>'
        html=html.replace('</header>','<div class="clinical-callout" role="note">'+warning+'<p>For study, not prescribing. Verify the species, dose and current clinical guidance before treating a patient.</p></div></header>',1)
    return html

def cards(b,rows,clinical=False):
    result=[];tones=['mint','pink','peach','purple','pink','mint']
    for i,r in enumerate(rows,1):
        from book_catalogue import by_resource
        book=by_resource(r['id'])
        artwork='<img src="'+e(book['cover']['path'],quote=True)+'" width="'+str(book['cover']['width'])+'" height="'+str(book['cover']['height'])+'" alt="" loading="lazy" decoding="async">'
        title=e(r['title']);rid=e(r['id'],quote=True);tone=tones[(i-1)%len(tones)]
        source=r.get('sourceCredit')
        credit='<p class="rx-book-source">'+b.icon('people')+'<span>'+e(source)+'</span></p>' if source and r.get('collection')!='handbooks' else ''
        result.append('<article class="file-row rx-book-card" id="file-'+rid+'" data-book-id="'+rid+'"><span class="rx-book-number" aria-label="Resource '+str(i)+'">#'+str(i)+'</span><span class="rx-book-icon '+tone+'" aria-hidden="true">'+artwork+'</span><div class="rx-book-content"><div class="rx-book-title"><h3 title="'+e(r['name'],quote=True)+'">'+title+'</h3></div><p class="rx-book-description">'+e(r['description'])+'</p>'+credit+'</div>'+b.link(book['page'],b.icon('book')+'<span class="open-label">Open Book</span>'+b.icon('arrow')+'<span class="sr-only">: '+title+'</span>','file-open rx-book-open')+'</article>')
    return '<div class="file-list rx-book-grid">'+''.join(result)+'</div>'

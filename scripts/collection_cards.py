"""Numbered book cards used only by Objective and Drug Index collections."""
from html import escape as e

def intro(b,title,description,crumbs=None,clinical=False):
    html=b.article_intro(title,description,crumbs)
    html=html.replace('container reading-page','container reading-page rx-collections'+(' rx-drug-collection' if clinical else ' rx-objective-collection'),1)
    if clinical:
        warning='<svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m12 3 10 18H2Z"/><path d="M12 9v5m0 3h.01"/></svg>'
        html=html.replace('</header>','<div class="clinical-callout" role="note">'+warning+'<p>For study, not prescribing. Verify the species, dose and current clinical guidance before treating a patient.</p></div></header>',1)
    return html

def cards(b,rows,clinical=False):
    result=[];tones=['peach','mint','pink','purple','sky']
    for i,r in enumerate(rows,1):
        title=e(r['title']);rid=e(r['id'],quote=True);tone=tones[(i-1)%len(tones)] if clinical else 'yellow'
        source=r.get('sourceCredit') or r.get('source')
        credit='<p class="rx-book-source">'+b.icon('people')+'<span>'+e(source)+'</span></p>' if source else ''
        result.append('<article class="file-row rx-book-card" id="file-'+rid+'" data-resource-id="'+rid+'"><span class="rx-book-number" aria-label="Resource '+str(i)+'">#'+str(i)+'</span><span class="rx-book-icon '+tone+'" aria-hidden="true">'+b.icon('book')+'</span><div class="rx-book-content"><h3 title="'+e(r['name'],quote=True)+'">'+title+'</h3><p class="rx-book-description">'+e(r['description'])+'</p>'+credit+'</div>'+b.link(r['url'],'<span class="open-label">Open Book</span>'+b.icon('external')+'<span class="sr-only">: '+title+'</span>','file-open rx-book-open')+'</article>')
    return '<div class="file-list rx-book-grid">'+''.join(result)+'</div>'

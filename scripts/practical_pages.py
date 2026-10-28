"""Organised Practical Vault pages using real files and complete album links."""
from html import escape as e
from library import slug,normal,natural
from practical_catalogue import vault_url,source_data
from syllabus_pages import checklist_url
def practical_card(b,r):
    from library_views import size_label
    metadata='Photo folder' if r['photoIds'] else r['format']+(' · '+size_label(r['size']) if r['size'] is not None else '')
    rid=r['id'];aliases=''.join('<span class="anchor-alias" id="file-'+v['id']+'"></span>' for v in r['variants'] if v['id']!=rid)
    return aliases+'<article class="file-row practical-file-row" id="file-'+rid+'" data-resource-id="'+rid+'" data-kind="'+r['kind']+'" data-row-search="'+e(normal(r['title']+' '+r['path']),quote=True)+'"><span class="format-icon" aria-hidden="true">'+r['format']+'</span><div class="file-title"><span title="'+e(r['name'],quote=True)+'">'+e(r['title'])+'</span><small class="practical-file-meta">'+e(metadata)+'</small><p class="practical-file-description">'+e(r['description'])+'</p></div>'+b.link(r['url'],'<span class="open-label">Open</span>'+b.icon('external')+'<span class="sr-only"> '+e(r['title'])+'</span>','file-open')+'</article>'
def render(b):
    from library_views import chunks,empty
    for y in b.LIBRARY['years']:
        for subject in y['subjects']:
            year=y['year'];name=subject['name'];parent=f'/bvsc/year-{year}/'+subject['slug']+'/';path=vault_url(year,name);label=b.DATA['labels'][str(year)];rows=[r for r in b.RECORDS if 'practical-vault' in r['collections'] and r['year']==year and r['subject']==name]
            desc=f'{name} Practical Vault for {label} BVSc & AH. Find practical documents, slides and photo collections where available, with links to the original subject folders.'
            intro=f'Practical material for {label} {name}, organised by source folder. Choose a collection to prepare for your next lab.' if rows else f'Practical material for {label} {name}. Use the practical syllabus checklist while resources are being added.'
            body=b.article_intro(name+' Practical Vault',intro,[('BVSc','/bvsc/'),(label,f'/bvsc/year-{year}/'),(name,parent)]).replace('container reading-page','container reading-page practical-vault',1)
            docs=sum(r['kind']!='images' for r in rows);albums=sum(r['kind']=='images' for r in rows)
            if rows:body+='<p class="practical-vault-meta">'+str(docs)+' '+('document' if docs==1 else 'documents')+(' · '+str(albums)+' photo '+('collection' if albums==1 else 'collections') if albums else '')+' · Source collection: Vetverse</p>'
            body+=b.link(checklist_url(year,name)+'#practical',b.icon('check')+'Practical syllabus checklist '+b.icon('arrow'),'practical-checklist-link')
            if not rows:body+=empty(b,'Practical material coming soon')
            else:
                body+='<div class="filter-collection practical-files">'
                if len(rows)>12:body+='<div class="library-controls js-only"><label class="sr-only" for="practical-query">Find practical material</label><div class="inline-search">'+b.icon('search')+'<input id="practical-query" class="collection-query" type="search" placeholder="Find a manual, slide or topic…" autocomplete="off"></div><div class="filter-chips" aria-label="Practical resource types">'+''.join('<button type="button" data-filter="'+key+'" aria-pressed="'+str(i==0).lower()+'">'+title+'</button>' for i,(key,title) in enumerate([('all','All'),('practical','Documents'),('presentation','Slides'),('images','Photos')]))+'</div><p class="filter-status sr-only" role="status"></p></div>'
                else:body+='<input class="collection-query" type="hidden" value=""><p class="filter-status sr-only" role="status"></p>'
                groups=sorted({r['group'] for r in rows},key=lambda g:(0 if 'manual' in g.lower() else 1,natural(g)))
                for i,group in enumerate(groups):
                    own=[r for r in rows if r['group']==group];body+='<details class="resource-group practical-group" id="'+slug(group)+'"'+(' open' if i==0 else '')+'><summary><h2>'+e(group)+'</h2><span class="group-count">'+str(len(own))+'</span>'+b.icon('chevron')+'</summary><div class="group-body">'+chunks(b,own,practical_card,12)+'</div></details>'
                body+='<div class="filter-empty" hidden><p>No practical resources match. Try a shorter title or another type.</p></div></div><p class="practical-source-note">Files open in the original collection. Photo sets open as folders so the whole collection remains available.</p>'
            body+='<p class="practical-teaching-note">Use these materials alongside your department’s practical teaching and supervision.</p>'+b.link(parent,'Back to '+e(name)+' '+b.icon('arrow'),'syllabus-back')+'</div>'
            b.write_page(path,name+' Practical Vault — '+label+' BVSc & AH',desc,body,[(r['title'],r['url']) for r in rows])

"""Folder-first practical preparation, with source-backed assessment guidance."""
from html import escape as e
from library import natural
from practical_catalogue import vault_url,source_data
from syllabus_pages import checklist_url,DATA as SYLLABI

def render(b):
    source=source_data()
    for y in b.LIBRARY['years']:
        for subject in y['subjects']:
            year=y['year'];name=subject['name'];parent=f'/bvsc/year-{year}/'+subject['slug']+'/';path=vault_url(year,name);label=b.DATA['labels'][str(year)]
            rows=[r for r in b.RECORDS if 'practical-folders' in r['collections'] and r['year']==year and r['subject']==name]
            rows.sort(key=lambda r:(r['folderId']!=r['practicalRoot'],natural(r['path'])))
            desc=f'{name} practical folders, practical syllabus and assessment guidance for {label} BVSc & AH. Prepare for labs and practical examinations in one place.'
            body=b.article_intro(name+' Practical Vault','Your lab material, together. Open a practical folder or check what your syllabus expects.',[('BVSc','/bvsc/'),(label,f'/bvsc/year-{year}/'),(name,parent)]).replace('container reading-page','container reading-page practical-vault',1)
            body+='<section class="vault-collections"><header class="vault-section-heading"><span class="rx-row-icon sky">'+b.icon('book')+'</span><div><h2>Practical collections</h2><p>Original subject folders · Vetverse</p></div></header>'
            if not rows:body+='<p class="vault-empty">No practical folder is available for this subject yet. The syllabus checklist below is ready to use.</p>'
            for r in rows:
                root=r['folderId']==r['practicalRoot'];label_text='All practical material' if root else r['path'].split('Practicals/',1)[-1] if 'Practicals/' in r['path'] else r['group'];ic='flask' if root else 'book' if 'manual' in label_text.lower() else 'paper';tone='sky' if root else 'mint' if ic=='book' else 'peach'
                aliases=''.join('<span class="anchor-alias" id="file-'+fid+'"></span>' for fid in r['searchFileIds'] if fid!=r['folderId'])
                body+='<article class="vault-folder'+(' vault-folder-main' if root else '')+'" id="folder-'+r['folderId']+'" data-resource-id="'+r['id']+'">'+aliases+b.link(r['url'],'<span class="rx-row-icon '+tone+'">'+b.icon(ic)+'</span><span><strong>'+e(label_text)+'</strong><small>'+('Browse the complete collection' if root else 'Open folder in Google Drive')+'</small></span>'+b.icon('external'),'file-open')+'</article>'
            body+='</section>'
            syllabus=next(s for s in SYLLABI['subjects'] if s['subject']==name)
            units=[u for u in syllabus['units'] if u['kind']=='practical']
            body+='<section class="vault-preparation"><header class="vault-section-heading"><span class="rx-row-icon mint">'+b.icon('check')+'</span><div><h2>Before the practical</h2><p>Start with the syllabus. Then open your record.</p></div></header>'+b.link(checklist_url(year,name)+'#practical','<span><strong>Practical syllabus checklist</strong><small>'+str(len(units))+' '+('unit' if len(units)==1 else 'units / sections')+' · tick off your preparation</small></span>'+b.icon('arrow'),'practical-checklist-link')
            assessment=syllabus.get('assessment')
            if assessment:
                body+='<div class="vault-assessment"><h3>Assessment at a glance</h3><p>'+e(assessment['summary'])+'</p>'
                if assessment.get('papers'):body+='<dl>'+''.join('<div><dt>'+e(p['title'])+'</dt><dd>'+e(p['detail'])+'</dd></div>' for p in assessment['papers'])+'</dl>'
                body+='</div>'
            body+='<details class="vault-syllabus-topics"><summary>Assessment rules '+b.icon('chevron')+'</summary><ul><li>At least 75% attendance in theory and practical separately is required for examination eligibility.</li><li>Pass theory (internal and external combined) and practical separately with at least 50%.</li><li>Practical evaluation considers records or logbooks, demonstrated skills or written work, and viva voce.</li></ul></details>'
            body+='<details class="vault-syllabus-topics"><summary>Practical units &amp; skills '+b.icon('chevron')+'</summary><ul>'+''.join('<li>'+e(u['title'])+'</li>' for u in units)+'</ul></details><p class="vault-supervision">Follow your department’s current assessment instructions and practise clinical procedures under supervision.</p></section>'
            if assessment:body+='<p class="vault-source">Assessment source: '+b.link(syllabus['sourceUrl']+'#page='+str(assessment.get('sourcePage',syllabus['sourcePage'])),'VCI MSVE 2016 curriculum '+b.icon('external'))+'. Your university’s current rules take precedence.</p>'
            body+=b.link(parent,'Back to '+e(name)+' '+b.icon('arrow'),'syllabus-back')+'</div>'
            b.write_page(path,name+' Practical Vault — '+label+' BVSc & AH',desc,body,[(r['title'],r['url']) for r in rows])

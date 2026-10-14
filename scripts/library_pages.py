"""Render the Drive-backed library while preserving existing routes and guide content."""
from html import escape as e
from collections import Counter
from urllib.parse import quote
from library import GROUPS,natural,slug

def size_label(size):
 if size is None:return 'Size not provided'
 if size<1000:return str(size)+' B'
 if size<1_000_000:return f'{size/1000:.0f} KB'
 return f'{size/1_000_000:.1f} MB'
def empty(b,text='Coming soon'):
 return '<div class="empty-library"><p class="resource-badge">'+e(text)+'</p><p>'+e(b.MICROCOPY['empty'][0])+'</p>'+b.link('/request-resource/','Request Resource','button secondary')+'</div>'
def file_card(b,r):
 date=r.get('updated');date_html='<time datetime="'+e(date,quote=True)+'">'+e(date[:10])+'</time>' if date else 'Date not provided'
 credit='<p class="file-credit">Source credit: '+e(r['sourceCredit'])+'</p>' if r.get('sourceCredit') else ''
 download=b.link(r['download'],'Download <span class="sr-only">'+e(r['title'])+'</span>','button secondary') if r['download'] else ''
 return '<article class="resource-card file-card" id="file-'+r['id']+'" data-resource-id="'+r['id']+'"><div class="file-label"><span class="file-type">'+b.icon('paper')+e(r['format'])+'</span><span class="resource-badge">'+e(r['group'])+'</span></div><h3>'+e(r['title'])+'</h3><p class="file-meta">'+size_label(r['size'])+' · Updated '+date_html+'</p>'+credit+'<div class="card-actions">'+b.link(r['url'],'Open <span class="sr-only">'+e(r['title'])+' on Google Drive</span>','button')+download+'</div><div class="file-utilities"><button type="button" class="bookmark-button js-only" data-bookmark="'+r['id']+'" aria-pressed="false">Save resource</button>'+b.link('/request-resource/?file='+r['id']+'#report','Report an error / takedown','report-link')+'</div></article>'
def teaser(b,r):
 return '<li>'+b.link(r['permalink'],'<span>'+e(r['title'])+'<small>'+e(r['subject'])+' · '+e(r['format'])+'</small></span>'+b.icon('arrow'),'listing-row')+'</li>'
def matching(b,category):
 records=b.RECORDS
 def has(r,pattern):
  import re
  return bool(re.search(pattern,r['path'],re.I))
 if category=='icar-pyq':return [r for r in records if has(r,r'\b(?:pyqs?|icar)\b')]
 if category=='objective-books':return [r for r in records if has(r,r'\b(?:objectives?|mcqs?)\b') and r['group']=='Books']
 if category=='objective-questions':return [r for r in records if has(r,r'\b(?:objectives?|mcqs?)\b') and r['group']!='Books']
 if category=='handbooks':return [r for r in records if has(r,r'handbooks?')]
 if category=='drug-index':return [r for r in records if has(r,r'\bdrugs?\b') and not has(r,r'handbooks?')]
 if category=='clinical-other':return [r for r in records if has(r,r'clinical|pathology') and not has(r,r'handbooks?|\bdrugs?\b')]
 return []
def grouped_page(b,path,name,year,records,summary=None):
 b.geo.META[path]={'faq':[['Where do these files open?','Files open in the supplied Google Drive collection. Availability and access settings are controlled by the file owner.'],['Why is Download missing on some files?','A direct Download action is shown only when a binary file has a known size below 25 MB. Larger files and files with unknown sizes use the Drive viewer.']]}
 description=summary or f'Browse the indexed {name} files for {b.DATA["labels"][str(year)]} BVSc & AH students. Files are grouped by their source folders, with original names, sizes and update dates where provided.'
 body=b.article_intro(name,description)
 body=body.replace('<span>'+e(name)+'</span>',b.link('/bvsc/','BVSc')+' / '+b.link('/bvsc/year-'+str(year)+'/',b.DATA['labels'][str(year)])+' / <span>'+e(name)+'</span>',1)
 body+='<p class="resource-badge">'+str(len(records))+' files · '+b.DATA['labels'][str(year)]+'</p><nav class="page-index" aria-label="File groups">'+''.join(b.link('#'+slug(g),g+' ('+str(sum(r['group']==g for r in records))+')') for g in GROUPS)+'</nav>'
 if name!='Unsorted':body+='<button type="button" class="studied-button js-only" data-studied="'+slug(name)+'" aria-pressed="false">Mark as studied</button>'
 for group in GROUPS:
  rows=sorted([r for r in records if r['group']==group],key=lambda r:natural(r['title']))
  body+='<section class="content-section file-group" id="'+slug(group)+'"><h2>'+e(group)+' <span class="group-count">'+str(len(rows))+'</span></h2>'
  body+=('<div class="file-grid">'+''.join(file_card(b,r) for r in rows)+'</div>') if rows else empty(b,'No '+group.lower()+' indexed yet')
  body+='</section>'
 b.write_page(path,name+' · '+b.DATA['labels'][str(year)],description,body+'</div>',[(r['title'],r['url']) for r in records])
def overview(b):
 body=b.article_intro('BVSc Notes & Books',b.geo.META['/bvsc/']['summary'])+'<p class="source-note">Year grouping may vary by university. Check your syllabus.</p><nav class="page-index" aria-label="Choose year">'+''.join(b.link('#year-'+str(y['year']),b.DATA['labels'][str(y['year'])]) for y in b.LIBRARY['years'])+'</nav>'
 items=[]
 for y in b.LIBRARY['years']:
  year=str(y['year']);names=b.DATA['years'][year]
  body+='<section class="content-section year-group" id="year-'+year+'" data-year="'+year+'"><h2>'+b.DATA['labels'][year]+'</h2><p>'+str(y['count'])+' files · '+b.link('/bvsc/year-'+year+'/','Browse this year')+'</p>'+b.year_progress(year,names)+'<div class="subject-card-grid">'
  for subject in y['subjects']:
   name,ident=subject['name'],subject['slug'];path='/bvsc/year-'+year+'/'+ident+'/'
   ident=ident+'-'+year if ident=='unsorted' else ident
   rows=[b.CATALOGUE[r] for r in subject['resourceIds']];notes=sum(r['group']=='Notes' for r in rows);books=sum(r['group']=='Books' for r in rows)
   body+='<article class="resource-card subject-source" id="'+ident+'"><span class="resource-badge">'+str(len(rows))+' files · Google Drive</span><h3>'+b.link(path,e(name))+'</h3><div class="material-toggle" data-material-toggle><div class="material-tablist">'+b.link('#'+ident+'-notes','Notes','material-tab')+b.link('#'+ident+'-books','Books','material-tab')+'</div><div class="material-panel" id="'+ident+'-notes">'+b.link(path+'#notes',str(notes)+' notes · browse files','button secondary')+'</div><div class="material-panel" id="'+ident+'-books">'+b.link(path+'#books',str(books)+' books · browse files','button secondary')+'</div></div>'
   if name!='Unsorted':body+='<button type="button" class="studied-button js-only" data-studied="'+ident+'" aria-pressed="false">Mark as studied</button>'
   body+='</article>';items.append((name,path))
  body+='</div><div class="year-books" id="year-'+year+'-books">'+b.link('/bvsc/year-'+year+'/#books','Books for '+b.DATA['labels'][year],'button secondary')+'</div></section>'
 b.write_page('/bvsc/','BVSc Notes & Books',b.geo.META['/bvsc/']['summary'],body+'</div>',items)
 for y in b.LIBRARY['years']:
  year=y['year'];path='/bvsc/year-'+str(year)+'/'
  desc=f'Find {y["count"]} indexed files for {b.DATA["labels"][str(year)]} BVSc & AH study. Choose a subject to browse notes, books, practical manuals and other material.'
  b.geo.META[path]={'faq':[['How are subjects organised?','Subjects follow the existing four-year library structure. Your university syllabus remains the final reference for professional-year grouping.']]}
  body=b.article_intro(b.DATA['labels'][str(year)]+' BVSc Notes & Books',desc)+'<div class="year-group" data-year="'+str(year)+'">'+b.year_progress(str(year),b.DATA['years'][str(year)])+'<ul class="year-directory">'
  for subject in y['subjects']:
   owner=path+subject['slug']+'/'
   body+='<li>'+b.link(owner,'<span>'+e(subject['name'])+'<small>'+str(subject['count'])+' files</small></span>'+b.icon('arrow'),'listing-row')+'</li>'
   rows=[b.CATALOGUE[r] for r in subject['resourceIds']];grouped_page(b,owner,subject['name'],year,rows)
  body+='</ul><section class="content-section" id="books"><h2>Books by subject</h2><ul class="year-directory">'+''.join('<li>'+b.link(path+s['slug']+'/#books',e(s['name'])+' books','listing-row')+'</li>' for s in y['subjects'] if any(b.CATALOGUE[r]['group']=='Books' for r in s['resourceIds']))+'</ul></section></div></div>'
  b.write_page(path,b.DATA['labels'][str(year)]+' BVSc Notes & Books',desc,body,[(s['name'],path+s['slug']+'/') for s in y['subjects']])
def guides(b):
 for name,m in b.SUBJECTS.items():
  path='/bvsc/'+slug(name)+'/'
  year=m['year'];owner='/bvsc/year-'+str(year)+'/'+slug(name)+'/'
  summary=m['summary'];b.geo.META[path]={'faq':[['Where are the files for this subject?','Use the subject file collection linked on this page. Notes, books, practical manuals and other files are grouped by the original folder names.']]}
  body=b.article_intro(name,summary)+'<section class="content-section"><h2>Revision topic outline</h2><p>Use this overview alongside your university syllabus.</p><ul class="topic-list">'+''.join('<li>'+e(t)+'</li>' for t in m['topics'])+'</ul><p>'+e(m['studyTip'])+'</p>'+b.link(owner,'Browse '+e(name)+' files','button secondary')+'</section><section class="content-section"><h2>Related subjects</h2><ul class="related-subjects">'+''.join('<li>'+b.link('/bvsc/'+slug(n)+'/',e(n))+'</li>' for n in m['related'])+'</ul></section></div>'
  b.write_page(path,name,summary,body,[(name+' files',owner)])
def collections(b):
 for path,title,keys in [('/objective/','Objective Resources',['icar-pyq','objective-questions','objective-books']),('/clinical/','Clinical Resources',['handbooks','drug-index','clinical-other'])]:
  body=b.article_intro(title,b.geo.META[path]['summary'])+'<nav class="page-index" aria-label="On this page">'+''.join(b.link(b.ROUTES[k],b.DATA['collections'][k]['title']) for k in keys)+'</nav>'
  if path=='/clinical/':body+='<p class="source-note clinical-callout" role="note">Study references do not replace clinical judgement. Check the complete source, species and context before using drug information.</p>'+b.section_aside('clinical',1)
  items=[]
  for key in keys:
   data=b.DATA['collections'][key];anchor=b.ROUTES[key].split('#')[-1];rows=sorted(matching(b,key),key=lambda r:natural(r['title']))
   body+='<section class="content-section" id="'+anchor+'"><h2>'+e(data['title'])+'</h2><p>'+str(len(rows))+' matching files from the supplied Drive library.</p>'
   body+=('<ul class="resource-list">'+''.join(teaser(b,r) for r in rows)+'</ul>') if rows else empty(b)
   body+='</section>';items.append((data['title'],b.ROUTES[key]))
  b.write_page(path,title,b.geo.META[path]['summary'],body+'</div>',items)
def tools(b):
 body=b.article_intro('Tips & Tools for Vet Study',b.geo.META['/study-tools/']['summary'])+'<nav class="page-index" aria-label="On this page">'+''.join(b.link(b.ROUTES[k],b.DATA['collections'][k]['title']) for k in ['ai-guide','free-apps','useful-tools'])+'</nav>'
 guides=[('ai-guide','Use of AI for Vet Study',[('Start with your own outline','Ask AI to organise your topic list or suggest a revision structure. Compare the result with your syllabus and original notes.'),('Check before you learn','Verify veterinary facts, citations and drug information. A fluent answer can still be wrong; do not use AI output as a prescribing reference.'),('Turn reading into an explanation','Draft a presentation outline or ask for simpler wording, then rewrite it in your own words and credit your sources.')]),('free-apps','Useful Free Apps',[('Zotero','Keep reading references together and check every generated citation against the source.'),('LibreOffice','Prepare notes, tables and presentations without a subscription. Keep editable copies as well as PDFs.'),('A PDF reader','Use bookmarks and text search in a reader you already have. Keep a small, clearly named offline folder for essential material.')]),('useful-tools','Useful Study Tools',[('Your phone’s document scanner','Scan only material you have permission to copy. Check legibility and file size before sharing it.'),('A simple folder system','Use Year / Subject / Notes or Books, then meaningful file names. Search works better when files have useful titles.'),('A reference checklist','Record the author, edition, species and date when they matter. A saved file is a starting point, not a substitute for checking context.')])]
 for key,title,steps in guides:
  body+='<section class="content-section" id="'+b.ROUTES[key].split('#')[-1]+'"><h2>'+title+'</h2>'+ (b.section_aside('tools',0 if key=='ai-guide' else 1) if key!='useful-tools' else '')+'<ol class="guide-steps">'+''.join('<li><h3>'+e(t)+'</h3><p>'+e(d)+'</p></li>' for t,d in steps)+'</ol></section>'
 b.write_page('/study-tools/','Tips & Tools for Vet Study',b.geo.META['/study-tools/']['summary'],body+'</div>',[(t,b.ROUTES[k]) for k,t,_ in guides])
def other(b):
 body=b.article_intro('About Notes.ThatVetGuy',b.geo.META['/about/']['summary'])+'<section class="content-section"><h2>A useful place to start</h2><p>The library organises the supplied Google Drive files by professional year, subject and original folder group. File titles, sizes and dates come from the inspected source; known source credits are preserved.</p><h2>Original study guidance</h2><p>Revision outlines and on-site study guides are written for veterinary students. Linked files retain their original authorship; inclusion is not a claim of medical review or ownership.</p><h2>Help improve the library</h2><p>Request a resource or report an error or takedown through the request page.</p>'+b.link('/request-resource/','Request or report a resource','button secondary')+'</section></div>'
 b.write_page('/about/','About Notes.ThatVetGuy',b.geo.META['/about/']['summary'],body)
 body=b.article_intro('Can’t find what you need?',b.geo.META['/request-resource/']['summary'])+'<section class="content-section"><h2>Tell us what would help</h2><p>Include the title or topic, subject, year and edition if relevant.</p><label class="request-label" for="request-file-id">File ID, if reporting a file</label><input id="request-file-id" name="file" class="request-input" type="text" autocomplete="off"><p id="request-context" role="status"></p>'+b.link('mailto:contact@thatvetguy.net?subject=Resource%20request','Email your request','button request-email')+'<p class="source-note"><!--email_off-->You can also write directly to contact@thatvetguy.net. If your email app does not open, copy the address into your preferred email service.<!--/email_off--></p></section>'
 for ident,title,text in [('contact','Contact','Send your question to contact@thatvetguy.net.'),('contribute','Contribute a resource','Send the original title, subject and source credit. Share only material you have permission to contribute.'),('report','Report an error / takedown','Include the file ID or page URL, the issue and your preferred contact details. For a takedown request, explain your connection to the material so it can be reviewed.')]:body+='<section class="content-section" id="'+ident+'"><h2>'+title+'</h2><p><!--email_off-->'+text+'<!--/email_off--></p></section>'
 b.write_page('/request-resource/','Request a Resource',b.geo.META['/request-resource/']['summary'],body+'</div>')
 body=b.article_intro('Search veterinary resources',b.geo.META['/search/']['summary'])+b.search_form(True)+'<section class="content-section"><h2 id="results-heading">Browse the library</h2><div id="page-results"><p class="search-loading" hidden>Searching the library…</p></div><nav class="page-index" aria-label="Browse categories">'+''.join(b.link(p,t) for p,t in [('/bvsc/','Notes & Books'),('/objective/','Objective'),('/clinical/','Clinical')])+'</nav></section>'
 from assets_index import find_preset
 for anchor,label in [('pharmacology','Pharmacology'),('haemonchus','Haemonchus'),('nsaids','NSAIDs'),('surgery-books','Surgery books')]:
  rows=find_preset(label,b.RECORDS)
  body+='<section class="content-section preset-result" id="preset-'+anchor+'"><h2>'+label+'</h2><p>'+str(len(rows))+' matching files.</p>'+('<ul class="resource-list">'+''.join(teaser(b,r) for r in rows)+'</ul>' if rows else empty(b,'No matching files'))+'</section>'
 b.write_page('/search/','Search Veterinary Resources',b.geo.META['/search/']['summary'],body+'</div>',noindex=True)
def render(b):overview(b);guides(b);collections(b);tools(b);other(b)

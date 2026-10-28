"""Source-backed student guides in the existing Rx Notes shell."""
import json,re
import career_guidance as guidance
from pathlib import Path
from html import escape as e
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parent.parent
DATA=json.loads((ROOT/'data/study-tools.json').read_text())
GUIDES=[dict(id='vet-apps',title='Vet App Shelf',icon='phone',tone='sky',description='Free veterinary apps for revision and field learning, plus 3D species anatomy tools. Find what each app does and when to use it.'),dict(id='online-resources',title='Vet Web Finder',icon='chain',tone='mint',description='Find BVSc notes, clinical references, research tools and official veterinary sources, with clear advice on when each website helps.'),dict(id='veterinary-careers',title='Explore Career Options in Veterinary',icon='cap',tone='peach',description='Explore clinical, government, industry, research and public health careers after BVSc & AH in India, with practical next steps and official sources.')]
def route(g):return '/study-tools/'+(g['id'] if isinstance(g,dict) else g)+'/'
def section(b,title,subtitle='',icon='book',tone='sky',ident=''):
 return '<section class="tool-section rx-section"'+(' id="'+ident+'"' if ident else '')+'><div class="tool-section-title"><span class="rx-row-icon '+tone+'">'+b.icon(icon)+'</span><div><h2>'+e(title)+'</h2>'+('<p class="rx-hand">'+e(subtitle)+'</p>' if subtitle else '')+'</div></div>'
def intro(b,g,subtitle):
 descriptions={'vet-apps':'Free apps for revision and field learning, plus species anatomy tools. Find the right app for the job.','online-resources':'A curated reading list for BVSc notes, clinical cases, research and official guidance.','veterinary-careers':'Find a route after BVSc & AH. Compare the work, training and practical next steps.'}
 head=b.article_intro(g['title'],descriptions[g['id']],[('Tools & Tips','/study-tools/')])
 head=re.sub(r'<span class="rx-row-icon [^"]+">.*?</span>','<span class="rx-row-icon '+g['tone']+'">'+b.icon(g['icon'])+'</span>',head,count=1,flags=re.S)
 return head+'<div class="study-guide" data-guide="'+g['id']+'">'
def related(b,current):
 return '<nav class="tool-related" aria-label="More study tools">'+''.join(b.link(route(g),'<span class="rx-row-icon '+g['tone']+'">'+b.icon(g['icon'])+'</span><span>'+e(g['title'])+'</span>'+b.icon('arrow')) for g in GUIDES if g['id']!=current)+'</nav>'
def filters(categories,label):
 return '<div class="tool-filters js-only" data-tool-filters aria-label="'+label+'">'+''.join('<button type="button" data-tool-filter="'+e(c,quote=True)+'" aria-pressed="'+('true' if i==0 else 'false')+'">'+e(c)+'</button>' for i,c in enumerate(['All']+categories))+'</div>'
def sources(b,rows):
 return '<details class="tool-sources"><summary>Sources & how this guide was checked '+b.icon('chevron')+'</summary><div><p>Descriptions and next steps are our editorial guidance. Requirements and availability can change; the linked official notice or publisher listing takes priority. Reviewed '+DATA['reviewed']+'.</p><ul>'+''.join('<li>'+b.link(s['url'],e(s['title']))+'<p>'+e(s['note'])+'</p></li>' for s in rows)+'</ul></div></details>'
def hub(b):
 from homepage import CONTENT,tabs,panel,row
 desc='Choose veterinary apps, reliable online reading and career paths worth exploring. Practical guides for life during and after BVSc & AH.'
 body=b.article_intro('Tools & Tips for Vet Students',desc)+'<div class="study-guide"><section data-home-tabs class="tool-hub">'+tabs('study-page',[('Tools','/study-tools/#tools'),('Tips','/study-tools/#tips')])
 cards='<span id="tools" class="anchor-alias"></span>'
 for g,old in zip(GUIDES,['free-apps','useful-tools','ai-guide']):
  cards+='<span id="'+old+'" class="anchor-alias"></span>'+b.link(route(g),'<span class="rx-row-icon '+g['tone']+'">'+b.icon(g['icon'])+'</span><span><strong>'+e(g['title'])+'</strong><small>'+e(g['description'])+'</small></span>'+b.icon('chevron'),'tool-hub-card')
 tips='<section id="tips"><h2 class="sr-only">Year Roadmaps</h2><div class="rx-row-drawer">'+''.join(row(r['title'],r['url'],r['icon'],r['tone']) for r in CONTENT['tips'])+'</div></section>'
 body+=panel('study-page',0,cards)+panel('study-page',1,tips)+'</section></div></div>'
 b.write_page('/study-tools/','Tools & Tips for Vet Students',desc,body,[(g['title'],route(g)) for g in GUIDES])
def apps(b):
 g=GUIDES[0];body='<div class="container reading-page app-page"><nav class="breadcrumbs" aria-label="Breadcrumb">'+b.link('/','Home')+' / '+b.link('/study-tools/','Tools & Tips')+'</nav><div class="study-guide" data-guide="vet-apps"><header class="app-shelf-heading"><span class="rx-row-icon sky">'+b.icon('phone')+'</span><div><span class="tool-eyebrow">YOUR POCKET TOOLKIT</span><h1>Vet App Shelf</h1><p>Four free apps. Less searching, more studying.</p></div></header>' 
 body+='<section class="tool-section app-store" id="free-apps"><h2 class="sr-only">Free veterinary apps</h2><div class="app-list">'
 for a in [a for a in DATA['apps'] if a['free']]:
  body+='<article class="app-card" id="'+a['id']+'"><div class="app-top"><img src="'+a['icon']+'" width="64" height="64" alt="'+e(a['title'],quote=True)+' app icon" loading="lazy" decoding="async"><div><span class="tool-eyebrow">'+e(a['category'])+'</span><h3>'+e(a['title'])+'</h3><p class="tool-publisher">'+e(a['publisher'])+'</p></div>'+b.link(a['store'],'Get<span class="sr-only"> on Google Play</span>','button tool-play')+'</div><p>'+e(a['description'])+'</p><div class="tool-tags">'+''.join('<span>'+e(t)+'</span>' for t in a['uses'])+'</div></article>'
 body+='</div></section>'+section(b,'Anatomy in 3D','Explore one species at a time.','bone','mint','anatomy-apps')+'<div class="anatomy-app-grid">'
 for a in [a for a in DATA['apps'] if not a['free']]:
  body+='<article class="anatomy-app" id="'+a['id']+'"><img src="'+a['icon']+'" width="64" height="64" alt="'+e(a['title'],quote=True)+' app icon" loading="lazy" decoding="async"><h3>'+e(a['title'])+'</h3><span>3D anatomy</span></article>'
 body+='</div><div class="tool-pending" id="telegram-apps">'+b.icon('telegram')+'<div><h3>Anatomy app collection</h3>'
 body+=b.link(DATA['paidTelegramUrl'],'Open Telegram collection','button') if DATA.get('paidTelegramUrl') else '<p>Paid apps · Telegram link coming soon.</p>'
 body+='</div></div></section>'
 body+=sources(b,[dict(title=a['title']+' — Google Play listing',url=a['store'],note=a['publisher']) for a in DATA['apps'] if a['free']])
 body+=related(b,g['id'])+'<aside class="tool-callout">For study and supervised reference. Check species, formulation and current clinical guidance before using drug or treatment information.</aside></div></div>'
 b.write_page(route(g),g['title'],g['description'],body,[(a['title'],route(g)+'#'+a['id']) for a in DATA['apps']])
def resources(b):
 g=GUIDES[1];body='<div class="container reading-page finder-page"><nav class="breadcrumbs" aria-label="Breadcrumb">'+b.link('/','Home')+' / '+b.link('/study-tools/','Tools & Tips')+'</nav><div class="study-guide" data-guide="online-resources"><section class="tool-directory" data-tool-collection><header class="finder-console"><div class="finder-brand"><span>Rx <b>Web Finder</b></span><span class="finder-count" role="status" data-tool-status>'+str(len(DATA['resources']))+' sites</span></div><div class="directory-search">'+b.icon('search')+'<div><h1><label for="resource-query">Veterinary resources online</label></h1><input id="resource-query" type="search" placeholder="Try TANUVAS, medicine or research…" autocomplete="off" data-tool-query></div></div>'+filters(['Notes','Clinical','Research','Official'],'Filter websites by use')+'</header><div class="tool-results">'
 for i,r in enumerate(DATA['resources']):
  domain=urlsplit(r['url']).netloc.removeprefix('www.')
  body+='<article class="tool-result" data-tool-item data-category="'+r['category']+'" data-tool-search="'+e(' '.join([r['title'],r['description'],r['use'],r['category'],r['source']]).lower(),quote=True)+'"><div class="result-source"><span class="rx-row-icon '+{'Notes':'sky','Clinical':'mint','Research':'purple','Official':'peach'}[r['category']]+'">'+b.icon({'Notes':'paper','Clinical':'stethoscope','Research':'microscope','Official':'shield'}[r['category']])+'</span><div><span>'+e(r['source'])+'</span><small>'+e(domain)+'</small></div><span class="result-category">'+r['category']+'</span></div><h2>'+b.link(r['url'],e(r['title']))+'</h2><p>'+e(r['description'])+'</p><p><strong>Good for:</strong> '+e(r['use'])+'</p><p class="result-access">'+e(r['access'])+'</p></article>'
 body+='</div><p class="tool-no-results" data-tool-empty hidden>No websites in this selection. Try a broader topic or choose All.</p></section>'
 body+=section(b,'Before you trust a page','A nice PDF cover is not a peer review.','shield','yellow')+'<div class="tool-checklist"><p><strong>Match your course.</strong> Year labels and older TANUVAS course codes can differ from your university’s current outline.</p><p><strong>Find the original.</strong> Check author, edition, species and references. Use official guidance for regulations and current clinical decisions.</p><p><strong>Read beyond the headline.</strong> For research, inspect the population, methods and limitations; a search result alone cannot answer a clinical question.</p><p><strong>Use AI as a helper.</strong> It can organise reading or explain terminology. Check every factual claim and citation before learning it.</p></div></section><p class="tool-review-note">Curated '+DATA['reviewed']+'. Links open the original websites. Access terms and availability can change; inclusion does not imply endorsement or ownership.</p>'
 body+=related(b,g['id'])+'</div></div>'
 b.write_page(route(g),g['title'],g['description'],body,[(r['title'],r['url']) for r in DATA['resources']])
def careers(b):
 g=GUIDES[2];body='<div class="container reading-page career-page"><nav class="breadcrumbs" aria-label="Breadcrumb">'+b.link('/','Home')+' / '+b.link('/study-tools/','Tools & Tips')+'</nav><div class="study-guide" data-guide="veterinary-careers" data-career-explorer><header class="career-hero"><div><span class="tool-eyebrow">THE VETERINARY CAREER EXPLORER</span><h1>Your path after BVSc</h1><p>Explore the work. Understand the entry route. Find your fit.</p></div><span class="career-hero-art" aria-hidden="true">'+b.icon('map')+'</span></header><nav class="career-tabs" aria-label="Career guide sections">'+''.join(b.link('#'+ident,b.icon(ic)+'<span>'+label+'</span>','career-tab') for ident,label,ic in [('career-routes','Explore','map'),('pg-or-practice','Further study','cap'),('overseas','Abroad','map'),('how-to-decide','How to decide','check')])+'</nav>'
 body+='<section class="career-workspace" id="career-routes" data-career-panel><div class="career-workspace-heading"><h2>What interests you?</h2><span>Start anywhere.</span></div><div data-tool-collection><div class="career-interests tool-filters js-only" data-tool-filters aria-label="Filter careers by work setting">'
 categories=[('All','All paths','map'),('Clinical','Clinical','stethoscope'),('Production','Production','leaf'),('Public service','Public service','shield'),('Research','Research','microscope'),('Industry','Industry','flask')]
 for i,(category,label,ic) in enumerate(categories):
  count=len(DATA['careers']) if category=='All' else sum(c['category']==category for c in DATA['careers'])
  body+='<button type="button" data-tool-filter="'+category+'" aria-pressed="'+str(i==0).lower()+'">'+b.icon(ic)+'<span>'+label+'</span><small aria-hidden="true">'+str(count)+'</small></button>'
 body+='</div><div class="career-list-label"><p role="status" data-tool-status>'+str(len(DATA['careers']))+' career routes</p><span>Open a path to explore</span></div><div class="career-grid">'
 source_map={s['id']:s for s in DATA['careerSources']}
 for i,c in enumerate(DATA['careers']):
  body+='<article class="career-card" data-career-tone="'+c['category']+'" id="'+c['id']+'" data-tool-item data-category="'+c['category']+'"><details class="career-details"><summary><span class="career-route-icon">'+b.icon(c['icon'])+'</span><span class="career-route-label"><h3>'+e(c['title'])+'</h3><span>'+e(c['summary'])+'</span></span>'+b.icon('chevron')+'</summary><div class="career-route-body"><p class="career-fit"><strong>You might enjoy this if…</strong> '+e(c['fit'])+'</p><div class="career-facts">'
  for label,key,ic in [('What will I do?','work','stethoscope'),('How do I start?','entry','cap'),('How can I try it?','first','check'),('What should I check?','watch','message')]:
   body+='<section class="career-fact" data-career-field="'+key+'"><h4>'+b.icon(ic)+label+'</h4><p>'+e(c[key])+'</p></section>'
  body+='</div>'+guidance.route_depth(b,c['id'])+'<button class="career-compare-add js-only" type="button" data-compare-route="'+c['id']+'" aria-pressed="false">Add to comparison '+b.icon('check')+'</button><p class="career-source-links">Check the source: '+''.join(b.link('#source-'+sid,e(source_map[sid]['title'].split(' — ')[0])) for sid in c['sources'])+'</p></div></details></article>'
 body+='</div><p class="tool-no-results" data-tool-empty hidden>Choose another setting to explore more routes.</p></div><div class="career-shortlist" data-career-comparison hidden><p data-compare-status role="status"></p><button type="button" data-open-comparison disabled>Compare paths</button><button type="button" data-clear-comparison>Clear</button></div><p class="tool-copy career-registration">Clinical practice in India requires the applicable training and veterinary registration. Always check the current official vacancy or admission notice for eligibility.</p></section>'
 body+='<dialog class="career-comparison" aria-labelledby="comparison-title"><header><h2 id="comparison-title">Two paths, at a glance</h2><button type="button" data-close-comparison aria-label="Close comparison">Close</button></header><p>Use this to start a conversation, then check the actual role.</p><div data-compare-cards></div></dialog>'
 body+='<script type="application/json" id="career-compare-data">'+json.dumps({k:v['compare'] for k,v in guidance.DATA['routes'].items()}).replace('<','\\u003c')+'</script>'
 body+=guidance.panels(b)
 body+='<details class="tool-sources career-official"><summary>Official checks & further reading '+b.icon('chevron')+'</summary><h2 class="sr-only">Official sources</h2><p class="tool-copy">Research checked '+DATA['reviewed']+'. Career descriptions and suggested next steps are editorial guidance. Overseas sources explain work settings or licensing in their own jurisdictions, not Indian eligibility.</p><ul>'+''.join('<li id="source-'+s['id']+'">'+b.link(s['url'],e(s['title']))+'<p>'+e(s['note'])+'</p></li>' for s in DATA['careerSources'])+'</ul></details>'
 body=re.sub(r'<section class="tool-section rx-section" id="(pg-or-practice|overseas|next-30-days)">',r'<section class="tool-section rx-section career-panel" id="\1" data-career-panel>',body)
 body+=related(b,g['id'])+'</div></div>'
 b.write_page(route(g),g['title'],g['description'],body,[(c['title'],route(g)+'#'+c['id']) for c in DATA['careers']])
def render(b):hub(b);apps(b);resources(b);careers(b)
def allowed_urls():
 return {c['url'] for c in guidance.DATA['community']}|{r['url'] for r in DATA['resources']}|{s['url'] for s in DATA['careerSources']}|{a['store'] for a in DATA['apps'] if a['free']}|{'https://www.ivri.nic.in/Extension/MobileApps.aspx'}|{DATA[k] for k in ['paidTelegramUrl','apkCollectionUrl'] if DATA.get(k)}

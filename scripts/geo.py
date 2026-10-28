"""Static discovery outputs derived from the same visible page content and catalogue."""
import json,re,hashlib
from datetime import datetime,timezone
from pathlib import Path
from html import escape,unescape
from html.parser import HTMLParser
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parent.parent
BASE='https://notes.thatvetguy.net'
META=json.loads((ROOT/'data/page-meta.json').read_text())
AUTHOR='Dr. Chirag Patidar'
PAGES={}
HISTORY_PATH=ROOT/'data/page-history.json'
HISTORY=json.loads(HISTORY_PATH.read_text()) if HISTORY_PATH.exists() else {}
SEARCH_META=json.loads((ROOT/'data/search-metadata.json').read_text())

def page_modified(path,title,description,body):
    """Track content changes, independently of source review and deploy dates."""
    digest=hashlib.sha256(json.dumps([title,description,body],ensure_ascii=False).encode()).hexdigest()
    previous=HISTORY.get(path,{})
    date=previous.get('modified') if previous.get('sha256')==digest else datetime.now(timezone.utc).date().isoformat()
    HISTORY[path]={'sha256':digest,'modified':date}
    return date

def faq_for(path):
    return META.get(path,{}).get('faq',[])[:2] if path in ['/about/','/request-resource/'] else []

def faq_html(path):
    pairs=faq_for(path)
    if not pairs:return ''
    return '<section class="content-section faq-list container" id="faq"><h2>Questions, answered</h2>'+''.join('<details><summary>'+escape(q)+'</summary><p>'+escape(a)+'</p></details>' for q,a in pairs)+'</section>'

def external_links(body):
    def fix(m):
        attrs,text=m.groups();href=re.search(r'href="([^"]+)"',attrs)
        if not href or not href[1].startswith(('https://','http://')) or href[1].startswith(BASE+'/'):return m[0]
        attrs=re.sub(r'\s+(target|rel)="[^"]*"','',attrs)
        if '<svg' not in text:text+='<svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" aria-hidden="true"><path d="M7 17 17 7M7 7h10v10"/></svg>'
        return '<a'+attrs+' target="_blank" rel="noopener noreferrer">'+text+'</a>'
    return re.sub(r'<a(\s[^>]*?)>(.*?)</a>',fix,body,flags=re.S)

def heading_ids(body):
    used=set(re.findall(r'\bid="([^"]+)"',body))
    def heading(m):
        tag,attrs,text=m.groups()
        if 'id=' in attrs:return m[0]
        name=re.sub(r'[^a-z0-9]+','-',unescape(re.sub('<[^>]+>','',text)).lower()).strip('-') or 'heading'
        anchor=name;n=2
        while anchor in used:anchor=name+'-'+str(n);n+=1
        used.add(anchor)
        return '<'+tag+attrs+' id="'+anchor+'">'+text+'</'+tag+'>'
    return re.sub(r'<(h[1-6])([^>]*)>(.*?)</h[1-6]>',heading,body,flags=re.S)

class Markdown(HTMLParser):
    def __init__(self):super().__init__();self.out=[];self.hide=0;self.anchor=[];self.head=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag in ('svg','button','script','style'):self.hide+=1
        if self.hide:return
        if tag in ('section','article','div','p','ul','ol','details','nav'):self.out.append('\n\n' if tag in ('section','article','p','details','nav') else '\n')
        if re.fullmatch('h[1-6]',tag):self.out.append('\n\n'+'#'*int(tag[1])+' ')
        if tag=='li':self.out.append('\n- ')
        if tag=='dt':self.out.append('\n- ')
        if tag=='dd':self.out.append(': ')
        if tag=='br':self.out.append(' ')
        if tag=='input' and a.get('type')=='checkbox':self.out.append('[ ] ')
        if tag=='a':
            u=a.get('href','');u=BASE+u if u.startswith('/') else u
            self.anchor.append(u);self.out.append('[')
    def handle_endtag(self,tag):
        if tag in ('svg','button','script','style'):
            self.hide=max(0,self.hide-1);return
        if self.hide:return
        if tag=='a' and self.anchor:self.out.append(']('+self.anchor.pop()+')')
        if tag in ('p','section','article','details') or re.fullmatch('h[1-6]',tag):self.out.append('\n\n')
    def handle_data(self,data):
        if not self.hide:self.out.append(data)
    def result(self):return re.sub(r'\n{3,}','\n\n',''.join(self.out)).strip()+'\n'

def register(path,title,desc,body,date,source_review=None,noindex=False):
    mirror=Markdown();mirror.feed(body)
    md=f'<!-- Canonical: {BASE+path}; updated: {date} -->\n\n'+mirror.result()+f'\nPage updated: {date}. Sources last reviewed: {source_review or date}; external file availability can change.\n'
    dest=ROOT/path.strip('/')/'index.md';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(md)
    PAGES[path]={'title':title,'description':desc,'markdown':md,'lastmod':date,'noindex':noindex}

def structured(path,title,description,items,home,body,records,date):
    orgid=BASE+'/#organization';personid=BASE+'/#author';siteid=BASE+'/#website'
    org={'@type':'Organization','@id':orgid,'name':'ThatVetGuy','url':'https://thatvetguy.net','logo':BASE+'/assets/favicon.svg','sameAs':['https://thatvetguy.net','https://t.me/vetshortnotesbytvg','https://t.me/jobupdatesbytvg']}
    person={'@type':'Person','@id':personid,'name':'Dr. Chirag Patidar','url':'https://www.thatvetguy.net/chirag','sameAs':['https://thatvetguy.net'],'hasCredential':[{'@type':'EducationalOccupationalCredential','name':'BVSc & AH'},{'@type':'EducationalOccupationalCredential','name':'MVSc'}]}
    site={'@type':'WebSite','@id':siteid,'name':'Notes.ThatVetGuy','alternateName':'Rx Notes by ThatVetGuy','url':BASE+'/','inLanguage':'en','publisher':{'@id':orgid},'potentialAction':{'@type':'SearchAction','target':{'@type':'EntryPoint','urlTemplate':BASE+'/search/?q={search_term_string}'},'query-input':'required name=search_term_string'}}
    page={'@type':'CollectionPage' if items is not None else 'WebPage','@id':BASE+path+'#webpage','name':title,'url':BASE+path,'description':description,'dateModified':date,'inLanguage':'en','isPartOf':{'@id':siteid},'author':{'@id':personid},'publisher':{'@id':orgid}}
    graph=[org,person,site,page]
    if path.startswith('/study-tools/') and path!='/study-tools/':
        from study_tools import DATA as TOOLS,GUIDES,route as tool_route
        guide=next(g for g in GUIDES if tool_route(g)==path)
        learning={'@type':'LearningResource','@id':BASE+path+'#guide','name':title,'url':BASE+path,'description':description,'educationalLevel':'BVSc & AH students and graduates','learningResourceType':'Career guide' if guide['id']=='veterinary-careers' else 'Study guide','inLanguage':'en','author':{'@id':personid},'dateModified':date}
        if guide['id']=='veterinary-careers':learning['citation']=[s['url'] for s in TOOLS['careerSources']]
        if guide['id']=='vet-apps':
            learning['hasPart']=[]
            for app in TOOLS['apps']:
                entry={'@type':'SoftwareApplication','@id':BASE+path+'#'+app['id'],'name':app['title'],'description':app['description'],'operatingSystem':'Android','applicationCategory':'EducationalApplication','publisher':{'@type':'Organization','name':app['publisher']},'image':BASE+app['icon']}
                if not app['free']:entry.pop('publisher',None)
                if app['free']:entry['downloadUrl']=app['store']
                graph.append(entry);learning['hasPart'].append({'@id':entry['@id']})
        graph.append(learning);page['hasPart']={'@id':learning['@id']}
    if re.fullmatch(r'/bvsc/year-[1-4]/roadmap/',path):
        from roadmaps import DATA as ROADMAPS
        yr=path.split('/')[2][-1]
        guide={'@type':'LearningResource','@id':BASE+path+'#guide','name':title,'url':BASE+path,'description':description,'educationalLevel':'BVSc & AH — Year '+yr,'learningResourceType':'Study guide','teaches':[s['name'] for s in ROADMAPS['years'][yr]['subjects']],'inLanguage':'en','author':{'@id':personid},'dateModified':date,'citation':[s['title']+'; '+s['location'] for s in ROADMAPS['academicSources'][:2]]}
        graph.append(guide);page['hasPart']={'@id':guide['@id']}
    if items is not None:
        listing={'@type':'ItemList','@id':BASE+path+'#contents','numberOfItems':len(items),'itemListElement':[{'@type':'ListItem','position':i+1,'name':n,'url':u if u.startswith('https:') else BASE+u} for i,(n,u) in enumerate(items)]}
        graph.append(listing);page['mainEntity']={'@id':listing['@id']}
    if not home:
        crumbs=[('Home','/')]
        if path.startswith('/bvsc/') and path!='/bvsc/':crumbs.append(('BVSc Notes & Books','/bvsc/'))
        year=re.match(r'/bvsc/(year-([1-4]))/[^/]+/',path)
        if year:crumbs.append(('Year '+year[2],'/bvsc/'+year[1]+'/'))
        if path.startswith('/books/') and path!='/books/':crumbs.append(('Veterinary Books','/books/'))
        if path.startswith('/study-tools/') and path!='/study-tools/':crumbs.append(('Tools & Tips','/study-tools/'))
        crumbs.append((title,path))
        graph.append({'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':i+1,'name':n,'item':BASE+u} for i,(n,u) in enumerate(crumbs)]})
    if path.endswith('/syllabus/') and path.startswith('/bvsc/'):
        from syllabus_pages import DATA as SYLLABI,checklist_url
        subject=next(s for s in SYLLABI['subjects'] if checklist_url(s['year'],s['subject'])==path)
        learning={'@type':'LearningResource','@id':BASE+path+'#checklist','name':title,'url':BASE+path,'description':description,'educationalLevel':'BVSc & AH — Year '+str(subject['year']),'learningResourceType':'Syllabus checklist','teaches':subject['subject'],'inLanguage':'en','isBasedOn':{'@type':'DigitalDocument','name':SYLLABI['authority'],'url':(subject['sourceUrl'] if subject['sourceUrl'].startswith('https://') else BASE+subject['sourceUrl'])+'#page='+str(subject['sourcePage'])},'dateModified':date}
        page['mainEntity']={'@id':learning['@id']};graph.append(learning)
    if path.startswith('/books/') and path!='/books/':
        from book_catalogue import books as book_registry
        book=next(b for b in book_registry() if b['page']==path)
        entry={'@type':['Book','LearningResource'] if book['type'] not in ['Reference sheet','Clinical guide'] else 'LearningResource','@id':BASE+path+'#book','name':book['title'],'url':BASE+path,'description':book['description'],'inLanguage':'en','educationalLevel':'BVSc & AH','learningResourceType':book['type'],'teaches':[s['name'] for s in book['subjects']] or ['Veterinary study'],'dateModified':date}
        if book.get('author'):entry['editor' if re.search(r'\(editors?\)',book['author'],re.I) else 'author']=[{'@type':'Person','name':re.sub(r'\s*\([^)]*\)|\s+et al\.?','',name).strip()} for name in re.split(r',\s*|\s+and\s+',book['author']) if name.strip().lower() not in ['editors','editor']]
        if book['references']:entry['citation']=book['references']
        if book.get('cover'):entry['image']=BASE+book['cover']['path']
        if book['primaryUrl']:entry['potentialAction']={'@type':'ReadAction','target':book['primaryUrl']}
        page['mainEntity']={'@id':entry['@id']};graph.append(entry)
    pairs=faq_for(path)
    if pairs:graph.append({'@type':'FAQPage','@id':BASE+path+'#faq','mainEntity':[{'@type':'Question','name':q,'acceptedAnswer':{'@type':'Answer','text':a}} for q,a in pairs]})
    for r in records:
        if r.get('public') is False:continue
        if not r['url'] or escape(r['url'],quote=True) not in body:continue
        for variant in r['variants']:
            graph.append({'@type':'LearningResource','@id':BASE+'/#resource-'+variant['id'],'name':r['title'],'url':variant['url'],'description':r['description'],'learningResourceType':r['type'],'educationalLevel':'BVSc & AH','teaches':r['subject'] or 'Veterinary study','inLanguage':'en','encodingFormat':variant['mime'],'isBasedOn':{'@type':'WebPage','url':variant['url']},**({'creditText':r['sourceCredit']} if r.get('sourceCredit') else {}),**({'dateModified':variant['updated']} if variant.get('updated') else {})})
    from course_outlines import DATA as OUTLINES
    for professional,outline in OUTLINES['years'].items():
        if outline['url'] not in body:continue
        graph.append({'@type':'LearningResource','@id':BASE+outline['url'],'name':outline['label']+' BVSc & AH Course Outline','url':BASE+outline['url'],'learningResourceType':'Course outline','educationalLevel':'BVSc & AH — '+outline['label'],'teaches':'Veterinary curriculum, theory and practical course contents','inLanguage':'en','encodingFormat':'application/pdf','creditText':'The Gazette of India: Extraordinary','dateModified':OUTLINES['reviewed']})
    return json.dumps({'@context':'https://schema.org','@graph':graph},ensure_ascii=False).replace('<','\\u003c')

def social(path):
    if path.startswith('/books/'):
        return '/assets/social/books/'+(path.strip('/').split('/')[-1] if path!='/books/' else 'index')+'.webp'
    section=path.strip('/').split('/')[0] or 'home'
    if section=='404':section='home'
    return '/assets/social/'+section+'.webp'

def discovery(date,index):
    HISTORY_PATH.write_text(json.dumps({p:HISTORY[p] for p in PAGES},indent=2)+'\n')
    bots=['*','GPTBot','OAI-SearchBot','ChatGPT-User','ClaudeBot','Claude-SearchBot','PerplexityBot','Google-Extended','Applebot-Extended','CCBot']
    (ROOT/'robots.txt').write_text(''.join(f'User-agent: {b}\nAllow: /\n\n' for b in bots)+'Sitemap: '+BASE+'/sitemap.xml\n')
    indexed={p:d for p,d in PAGES.items() if not d.get('noindex')}
    (ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'  <url><loc>{BASE+p}</loc><lastmod>{d["lastmod"]}</lastmod></url>\n' for p,d in indexed.items())+'</urlset>\n')
    intro='# Notes.ThatVetGuy\n\n> Free academic resources, thoughtfully made for future vets.\n\nNotes.ThatVetGuy (Rx Notes by ThatVetGuy) is a free academic library for BVSc & AH students in India. Site summaries: Dr. Chirag Patidar, BVSc & AH, MVSc. Notes and recommended reading are organised by professional year and subject. Topic notes open on Google Drive or their credited source PDFs and documents; objective and clinical collections open in Telegram. Book recommendations do not imply a downloadable copy is available. Known source credits are preserved; inclusion does not imply authorship or medical review.\n\nMain website: https://thatvetguy.net\nAuthor: '+AUTHOR+'\nLast source review: '+date+'. File access settings can change.\n\n'
    mapping='## Sections and subject guides\n\n'+''.join(f'- [{d["title"]}]({BASE+p}): {d["description"]}\n  - Markdown: {BASE+p}index.md\n' for p,d in indexed.items())
    retrieval='\n## Machine retrieval\n\n- Full visible page content: '+BASE+'/llms-full.txt\n- Resource index: '+BASE+'/search-index.json\n- Sitemap: '+BASE+'/sitemap.xml\n- Search (noindex): '+BASE+'/search/\n\n## Community\n\n- Short notes: https://t.me/vetshortnotesbytvg\n- Jobs: https://t.me/jobupdatesbytvg\n- Requests and contact: '+BASE+'/request-resource/\n'
    (ROOT/'llms.txt').write_text(intro+mapping+retrieval)
    (ROOT/'llms-full.txt').write_text(intro+'\n\n'.join('---\nCanonical: '+BASE+p+'\n\n'+d['markdown'] for p,d in PAGES.items()))
    raw=json.dumps(index,ensure_ascii=False,separators=(',',':'))+'\n'
    (ROOT/'search-index.json').write_text(raw);(ROOT/'assets/catalogue.json').write_text(raw)
    # Keep text mirrors retrievable while pointing duplicate representations at HTML.
    headers=ROOT/'_headers';existing=headers.read_text().split('# BEGIN GENERATED DISCOVERY')[0].rstrip()
    mirrors='\n'.join(p+'index.md\n  Link: <'+BASE+p+'>; rel="canonical"' for p in PAGES)
    headers.write_text(existing+'\n\n# BEGIN GENERATED DISCOVERY\n'+mirrors+'\n# END GENERATED DISCOVERY\n')

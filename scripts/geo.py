"""Static discovery outputs derived from the same visible page content and catalogue."""
import json,re
from pathlib import Path
from html import escape,unescape
from html.parser import HTMLParser
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parent.parent
BASE='https://notes.thatvetguy.net'
META=json.loads((ROOT/'data/page-meta.json').read_text())
LINKEDIN='https://www.linkedin.com/in/drchiragpatidarconnect'
PAGES={}

def faq_for(path):
    return META.get(path,{}).get('faq',[])

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
    return re.sub(r'<(h[1-3])([^>]*)>(.*?)</h[1-3]>',heading,body,flags=re.S)

class Markdown(HTMLParser):
    def __init__(self):super().__init__();self.out=[];self.hide=0;self.anchor=[];self.head=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag in ('svg','button','script','style'):self.hide+=1
        if self.hide:return
        if tag in ('section','article','div','p','ul','ol','details','nav'):self.out.append('\n\n' if tag in ('section','article','p','details','nav') else '\n')
        if re.fullmatch('h[1-6]',tag):self.out.append('\n\n'+'#'*int(tag[1])+' ')
        if tag=='li':self.out.append('\n- ')
        if tag=='br':self.out.append(' ')
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

def register(path,title,desc,body,date):
    mirror=Markdown();mirror.feed(body)
    md=f'<!-- Canonical: {BASE+path}; updated: {date} -->\n\n'+mirror.result()+f'\nLast checked: {date}. This date records source review, not a guarantee of external file availability.\n'
    dest=ROOT/path.strip('/')/'index.md';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(md)
    PAGES[path]={'title':title,'description':desc,'markdown':md,'lastmod':date}

def structured(path,title,description,items,home,body,records,date):
    orgid=BASE+'/#organization';personid=BASE+'/#author';siteid=BASE+'/#website'
    org={'@type':'Organization','@id':orgid,'name':'ThatVetGuy','url':'https://thatvetguy.net','logo':BASE+'/assets/favicon.svg','sameAs':['https://thatvetguy.net','https://t.me/vetshortnotesbytvg','https://t.me/jobupdatesbytvg']}
    person={'@type':'Person','@id':personid,'name':'Dr. Chirag Patidar','url':'https://www.thatvetguy.net/chirag','sameAs':[LINKEDIN,'https://thatvetguy.net'],'hasCredential':[{'@type':'EducationalOccupationalCredential','name':'BVSc & AH'},{'@type':'EducationalOccupationalCredential','name':'MVSc'}]}
    site={'@type':'WebSite','@id':siteid,'name':'Notes.ThatVetGuy','url':BASE+'/','inLanguage':'en','publisher':{'@id':orgid},'potentialAction':{'@type':'SearchAction','target':{'@type':'EntryPoint','urlTemplate':BASE+'/search/?q={search_term_string}'},'query-input':'required name=search_term_string'}}
    page={'@type':'CollectionPage' if items else 'WebPage','@id':BASE+path+'#webpage','name':title,'url':BASE+path,'description':description,'dateModified':date,'inLanguage':'en','isPartOf':{'@id':siteid},'author':{'@id':personid},'publisher':{'@id':orgid}}
    graph=[org,person,site,page]
    if items:
        listing={'@type':'ItemList','@id':BASE+path+'#contents','numberOfItems':len(items),'itemListElement':[{'@type':'ListItem','position':i+1,'name':n,'url':u if u.startswith('https:') else BASE+u} for i,(n,u) in enumerate(items)]}
        graph.append(listing);page['mainEntity']={'@id':listing['@id']}
    if not home:
        crumbs=[('Home','/')]
        if path.startswith('/bvsc/') and path!='/bvsc/':crumbs.append(('BVSc Notes & Books','/bvsc/'))
        crumbs.append((title,path))
        graph.append({'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':i+1,'name':n,'item':BASE+u} for i,(n,u) in enumerate(crumbs)]})
    pairs=faq_for(path)
    if pairs:graph.append({'@type':'FAQPage','@id':BASE+path+'#faq','mainEntity':[{'@type':'Question','name':q,'acceptedAnswer':{'@type':'Answer','text':a}} for q,a in pairs]})
    for r in records:
        if not r['url'] or escape(r['url'],quote=True) not in body:continue
        graph.append({'@type':'LearningResource','@id':BASE+'/#resource-'+r['id'],'name':r['title'],'url':r['url'],'description':r['description'],'learningResourceType':r['type'],'educationalLevel':'BVSc & AH','teaches':r['subject'] or 'Veterinary study and reference skills','inLanguage':'en','isBasedOn':{'@type':'WebPage','url':r['url'],'publisher':{'@type':'Organization','name':r['source']}}})
    return json.dumps({'@context':'https://schema.org','@graph':graph},ensure_ascii=False).replace('<','\\u003c')

def social(path):
    section=path.strip('/').split('/')[0] or 'home'
    return '/assets/social/'+section+'.webp'

def discovery(date,index):
    bots=['*','GPTBot','OAI-SearchBot','ChatGPT-User','ClaudeBot','Claude-SearchBot','PerplexityBot','Google-Extended','Applebot-Extended','CCBot']
    (ROOT/'robots.txt').write_text(''.join(f'User-agent: {b}\nAllow: /\n\n' for b in bots)+'Sitemap: '+BASE+'/sitemap.xml\n')
    indexed={p:d for p,d in PAGES.items() if p!='/search/'}
    (ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'  <url><loc>{BASE+p}</loc><lastmod>{d["lastmod"]}</lastmod></url>\n' for p,d in indexed.items())+'</urlset>\n')
    intro='# Notes.ThatVetGuy\n\n> Free academic resources, thoughtfully made for future vets.\n\nA free academic directory primarily for BVSc & AH students. Original summaries: Dr. Chirag Patidar, BVSc & AH, MVSc. External notes and books retain their source credit; links do not imply authorship or medical review.\n\nMain website: https://thatvetguy.net\nAuthor: '+LINKEDIN+'\nLast source review: '+date+'; external HTTP availability has not been verified in the build environment.\n\n'
    mapping='## Sections and subject guides\n\n'+''.join(f'- [{d["title"]}]({BASE+p}): {d["description"]}\n  - Markdown: {BASE+p}index.md\n' for p,d in indexed.items())
    retrieval='\n## Machine retrieval\n\n- Full visible page content: '+BASE+'/llms-full.txt\n- Resource index: '+BASE+'/search-index.json\n- Sitemap: '+BASE+'/sitemap.xml\n- Search (noindex): '+BASE+'/search/\n\n## Community\n\n- Short notes: https://t.me/vetshortnotesbytvg\n- Jobs: https://t.me/jobupdatesbytvg\n- Requests and contact: '+BASE+'/request-resource/\n'
    (ROOT/'llms.txt').write_text(intro+mapping+retrieval)
    (ROOT/'llms-full.txt').write_text(intro+'\n\n'.join('---\nCanonical: '+BASE+p+'\n\n'+d['markdown'] for p,d in PAGES.items()))
    raw=json.dumps(index,ensure_ascii=False,separators=(',',':'))+'\n'
    (ROOT/'search-index.json').write_text(raw);(ROOT/'assets/catalogue.json').write_text(raw)

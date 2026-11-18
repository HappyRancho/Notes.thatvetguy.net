"""Support links, email templates and complete visible FAQ/schema/crawl parity."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,parse_qs
import json,sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'scripts'))
from community_pages import DATA,FAQS,FORMATS,draft
from check_seo_loader import Document
faq=(ROOT/'faq/index.html').read_text();doc=Document(faq)
schema=next(s for s in doc.schemas if s.get('@type')=='FAQPage')
assert len(schema['mainEntity'])==len(FAQS)==22
assert len({q['id'] for q in FAQS})==len(FAQS)
md=(ROOT/'faq/index.md').read_text()
for source,entry in zip(FAQS,schema['mainEntity']):
 assert entry['name']==source['question'] and entry['acceptedAnswer']['text']==source['answer']
 assert source['question'] in md and source['answer'] in md
assert 'https://notes.thatvetguy.net/faq/' in (ROOT/'sitemap.xml').read_text()
assert '/faq/' in (ROOT/'index.html').read_text() and '/faq/' in (ROOT/'llms.txt').read_text()
assert any(r['url']=='/faq/' for r in json.loads((ROOT/'search-index.json').read_text()))
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.labels=set();self.fields=set()
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='a' and 'data-compose' in a:self.links.append(a['href'])
  if tag=='label' and a.get('for'):self.labels.add(a['for'])
  if tag in ['input','select','textarea'] and ('data-email-label' in a or 'data-draft' in a):self.fields.add(a['id'])
raw=(ROOT/'request-resource/index.html').read_text();parser=Links();parser.feed(raw)
assert parser.fields<=parser.labels,'Support controls must have explicit labels'
assert len(parser.links)==len(FORMATS)==5
assert raw.count('<!--email_off-->')>=5,'Keep static email templates intact through Cloudflare email obfuscation'
for (key,config),href in zip(FORMATS.items(),parser.links):
 url=urlsplit(href);params=parse_qs(url.query)
 assert url.scheme=='mailto' and url.path==DATA['email']
 assert params['subject']==[config['subject']] and params['body']==[draft(key)]
 assert all(label in params['body'][0] for _,label,_,_ in config['fields'])
assert 'Screenshot / attachment:' in draft('report') and 'Screenshot / attachment:' in draft('request')
for ident in ['request','report','contact','contribute','rights']:assert 'id="'+ident+'" open' in raw,'All support sections need a no-JavaScript path'
assert 'type="file"' not in raw,'Do not imply a screenshot upload service'
for path in ROOT.rglob('index.html'):
 if any(x in path.parts for x in ['node_modules','.git','docs','dist']):continue
 text=path.read_text()
 assert text.count('id="student-notice"')==1,(path,'Student notice missing/duplicated')
 assert text.index('</header>')<text.index('id="student-notice"')<text.index('<main'),(path,'Notice must follow header')
 assert DATA['email'] in text and 'data-notice-toggle' in text
for path in ['about','request-resource']:
 text=(ROOT/path/'index.html').read_text();assert 'Questions, answered' not in text
 assert not any(s.get('@type')=='FAQPage' for s in Document(text).schemas),'Central FAQ must be the source of answers'
print('PASS Community: 22 full FAQ answers/schema/mirrors; five structured mail drafts; labelled controls; static support anchors and global student notice.')

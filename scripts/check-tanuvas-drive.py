"""Reconcile the owner Drive hierarchy, public readers and destination labels."""
from pathlib import Path
from html import unescape
from html.parser import HTMLParser
from urllib.parse import urlsplit
import json,re
from tanuvas_drive import display_name,legacy_hashes
from subject_pages import url
ROOT=Path(__file__).resolve().parent.parent
read=lambda name:json.loads((ROOT/'data'/name).read_text())
source=read('tanuvas-source.json');inventory=read('tanuvas-drive-inventory.json')
assert not inventory['errors'] and not inventory['paginationReview']
files={f['id']:f for f in inventory['files']};notes={r['id']:r for r in source['notes']}
resources={r['id']:r for r in read('resources.json')['files']}
assert set(files)==set(notes)=={r['id'] for r in resources.values() if 'tanuvas' in r['collections'] and r.get('public',True)}
assert set(source['supersededTopicIds']).isdisjoint(notes)
assert all(not resources[i].get('public',True) for i in source['supersededTopicIds'])
directory=(ROOT/'bvsc/tanuvas-notes/index.html').read_text()
assert set(re.findall(r'data-tanuvas-course="([^"]+)"',directory))==set(files)
assert directory.count('data-tanuvas-course=')==len(files)
assert 'VetBVSc' not in directory and 'No dedicated fourth-year' not in directory
for folder in source['subjectFolders']:
 path=url(folder['year'],folder['subject']);raw=(ROOT/path.strip('/')/'index.html').read_text()
 assert folder['name']==display_name(folder['originalName']) and folder['name'] in unescape(directory)
 expected=sorted([f for f in inventory['files'] if f['parentId']==folder['id']],key=lambda f:f['sourceOrder'])
 panel=raw.split('id="tanuvas"',1)[1].split('class="subject-practical-link"',1)[0]
 assert re.findall(r'data-resource-id="([^"]+)"',panel)==[f['id'] for f in expected],path
 for f in expected:
  record=resources[f['id']];assert record['title']==record['name']==display_name(f['name'])
  assert record['url']==f['url'] and record['subject']==folder['subject'] and record['year']==folder['year']
  assert record['title'] in unescape(panel) and f['url'] in panel
  assert f['id'] in directory and record['sourceCredit']=='TANUVAS'
 for ident in legacy_hashes(folder['year'],folder['subject']):assert 'id="'+ident+'"' in raw
 assert folder['url'] in directory and path+'syllabus/' in directory
for f in read('vetbvsc-source.json')['notes']:
 r=resources[f['id']];assert r['url']==f['url']
 if f['id'] not in source['supersededTopicIds']:assert r.get('public',True) and r['sourceCredit']==f.get('sourceCredit')
class Downloads(HTMLParser):
 def __init__(self):super().__init__();self.active=None;self.links=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='a' and 'book-download' in a.get('class','').split():self.active=[a['href'],'']
 def handle_data(self,text):
  if self.active:self.active[1]+=text
 def handle_endtag(self,tag):
  if tag=='a' and self.active:self.links.append(self.active);self.active=None
books=read('books.json')
for book in books:
 raw=(ROOT/book['page'].strip('/')/'index.html').read_text();p=Downloads();p.feed(raw)
 assert len(p.links)==1
 href,label=p.links[0]
 if urlsplit(href).hostname=='drive.google.com':assert 'Google Drive' in label and 'Telegram' not in label,(book['id'],label)
for y in read('resources.json')['years']:
 for s in y['subjects']:
  own=[b for b in books if {'year':y['year'],'name':s['name']} in b['subjects']]
  raw=(ROOT/url(y['year'],s['name']).strip('/')/'index.html').read_text()
  assert ('class="subject-more-books"' in raw)==(len(own)>8)
  if len(own)>8:assert 'Show fewer books' in raw and f'Show {len(own)-6} more books' in raw
for path in ['objective','about','books']:
 raw=(ROOT/path/'index.html').read_text()
 assert not re.search(r'(?:open in|direct|links? (?:to|on)|via) Telegram',raw,re.I),(path,'Stale provider copy')
print(f'PASS TANUVAS Drive: {len(files)} exact filenames, 16 subject folders, all four years, stable legacy anchors; all book download labels and disclosure thresholds checked.')

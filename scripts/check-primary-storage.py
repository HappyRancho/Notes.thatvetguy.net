"""Keep primary downloads exact while preserving resource identity and note content."""
import json,re
from pathlib import Path
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parent.parent
read=lambda name:json.loads((ROOT/'data'/name).read_text())
links=read('primary-drive-links.json');books={b['id']:b for b in read('books.json')};resources=read('resources.json')['files']
assert len(links['books'])==26
assert len({f['id'] for f in links['books'].values()})==26,'Different books mapped to the same download'
for ident,file in links['books'].items():
 b=books[ident];raw=(ROOT/b['page'].strip('/')/'index.html').read_text()
 assert b['primaryUrl']==file['url'] and not b['telegram'],ident
 assert b['access']=='Google Drive' and b['downloadLabel']=='Open in Google Drive',ident
 assert 'Download via Telegram' not in raw and 'private collection' not in raw,ident
 assert file['url'] in raw and b['cover'],ident
for r in read('collections.json')['resources']:
 assert r['url']==links['books'][r['id']]['url'] and r['source']=='Google Drive'
 row=next(x for x in resources if x['id']=='telegram-'+r['id'])
 assert row['url']==r['url'] and row['variants'][0]['url']==r['url']
for f in read('vetbvsc-source.json')['notes']:
 assert next(r for r in resources if r['id']==f['id'])['url']==f['url'],'Unmatched note source changed'
class Details(HTMLParser):
 def __init__(self):super().__init__();self.open=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='details' and 'open' in a and any(c in a.get('class','').split() for c in ['reader-unit','syllabus-unit']):self.open.append(a)
for year in read('resources.json')['years']:
 for subject in year['subjects']:
  path=ROOT/'bvsc'/('year-'+str(year['year']))/subject['slug'];hub=(path/'index.html').read_text()
  assert hub.index('id="notes"')<hub.index('subject-practical-link') and hub.index('id="tanuvas"')<hub.index('subject-practical-link')
  for page in [path/'index.html',path/'syllabus/index.html']:
   parsed=Details();parsed.feed(page.read_text());assert not parsed.open,(page,'Unit starts expanded')
print('PASS primary storage: 26 exact file mappings, stable collection IDs, existing notes preserved, all subject/checklist units closed by default.')

#!/usr/bin/env python3
"""Reconcile books-only provenance, canonical pages and truthful access labels."""
from pathlib import Path
from collections import Counter
import json,re,sys
from PIL import Image
from check_seo_loader import Document
ROOT=Path(__file__).resolve().parent.parent
books=json.loads((ROOT/'data/books.json').read_text())
source=json.loads((ROOT/'data/vetverse-books.json').read_text())
curation=json.loads((ROOT/'data/book-curation.json').read_text())
search=json.loads((ROOT/'search-index.json').read_text())
actual=Counter(f['id'] for b in books for f in b['files'])
expected={f['id'] for f in source['files']}-set(curation['excludedFiles'])
assert set(actual)==expected and set(actual.values())=={1},'Lost or duplicated source book'
assert len({b['id'] for b in books})==len(books)
assert all(any(part.lower().strip() in ['book','books'] for part in f['path'].split('/')) for b in books for f in b['files']),'Non-Books folder imported'
coverage=Counter();unavailable=[]
for b in books:
 p=ROOT/b['page'].strip('/')/'index.html';raw=p.read_text();d=Document(raw)
 assert d.h1==1 and d.canonical==['https://notes.thatvetguy.net'+b['page']]
 assert p.with_suffix('.md').exists() and b['page'] in (ROOT/'llms.txt').read_text()
 assert any(r['url'].split('#')[0]==b['page'] for r in search)==bool(b['primaryUrl']),(b['id'],'search availability mismatch')
 schema=next(x for x in d.schemas if x.get('@id')=='https://notes.thatvetguy.net'+b['page']+'#book')
 assert schema['name']==b['title'] and schema['educationalLevel']=='BVSc & AH'
 assert not any(k in schema for k in ['isbn','aggregateRating','offers']),'Unverified commercial metadata'
 if b['telegram']:
  assert 'Download via Telegram' in raw and b['telegram'] in d.links
  assert 'opens the book’s Telegram post' in raw
  if '/c/' in b['telegram']:assert 'private collection' in raw
 elif b['files']:
  assert 'Open in Google Drive' in raw and 'Download via Telegram' not in raw
  assert all(f['url'] in d.links for f in b['files']),(b['id'],'copy link lost')
 else:assert 'Request this book' in raw and 'reading recommendation' in raw
 if b['primaryUrl']:assert schema['potentialAction']['target']==b['primaryUrl']
 if b['cover']:
  c=b['cover'];path=ROOT/c['path'].lstrip('/')
  with Image.open(path) as image:assert image.size==(c['width'],c['height'])
  assert f'width="{c["width"]}" height="{c["height"]}"' in raw
  if c['kind']=='reference-cover':assert 'linked edition may differ' in raw
  coverage[c['kind']]+=1
 else:assert 'Cover unavailable' in raw;unavailable.append(b['id'])
 with Image.open(ROOT/'assets/social/books'/str(b['id']+'.webp')) as image:assert image.size==(1200,630)
 assert 'Arthur Symons' not in raw
by_year=Counter(f['year'] for b in books for f in b['files'])
report={'pages':len(books),'driveFiles':len(actual),'driveWorks':sum(bool(b['files']) for b in books),'telegram':sum(bool(b['telegram']) for b in books),'readingGuides':sum(not b['primaryUrl'] for b in books),'filesByYear':dict(by_year),'coverTypes':dict(coverage),'coversUnavailable':unavailable,'excludedObjectivePacks':curation['excludedFiles']}
out=ROOT/'docs/qa/book-pages';out.mkdir(parents=True,exist_ok=True);(out/'data-report.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS BOOKS '+json.dumps({k:v for k,v in report.items() if k not in ['coversUnavailable','excludedObjectivePacks']}))

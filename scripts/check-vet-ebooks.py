"""Validate public PDF entries and their HTML, search and machine-readable equivalents."""
from pathlib import Path
from urllib.parse import urlsplit
import json,re,xml.etree.ElementTree as ET
from check_seo_loader import Document
ROOT=Path(__file__).resolve().parent.parent
source=json.loads((ROOT/'data/vet-ebooks-books.json').read_text())
entries=source['entries'];books={b['id']:b for b in json.loads((ROOT/'data/books.json').read_text())}
assert len(entries)==25 and len({e['id'] for e in entries})==25
assert len({e['directPdf']['url'] for e in entries})==25
assert sum(e['existingWork'] for e in entries)==1
sitemap={e.text for e in ET.parse(ROOT/'sitemap.xml').findall('.//{*}url/{*}loc')}
search=json.loads((ROOT/'search-index.json').read_text());library=(ROOT/'books/index.html').read_text()
for item in entries:
 b=books[item['id']];pdf=b['directPdf'];url='https://notes.thatvetguy.net'+b['page']
 assert urlsplit(pdf['url']).hostname=='download.vet-ebooks.com'
 assert pdf['httpStatus']==200 and pdf['signature']=='%PDF-' and pdf['encodingFormat']=='application/pdf'
 assert 0<pdf['bytes']<35_000_000 and pdf['checked']==source['reviewed']
 assert b['downloadLabel']=='Download PDF'
 assert library.count('data-book-id="'+b['id']+'"')==1
 assert url in sitemap and any(r['url'].split('#')[0]==b['page'] for r in search)
 path=ROOT/b['page'].strip('/')/'index.html';raw=path.read_text();doc=Document(raw)
 assert doc.canonical==[url] and 'noindex' not in doc.meta['robots']
 assert pdf['url'] in doc.links and item['sourcePage'] not in doc.links
 assert all(topic in raw for topic in b['studyUses'])
 schema=next(s for s in doc.schemas if s.get('@id')==url+'#book')
 assert schema['encoding']=={'@type':'MediaObject','contentUrl':pdf['url'],'encodingFormat':'application/pdf','contentSize':pdf['sizeLabel']}
 assert schema['bookFormat']=='https://schema.org/EBook' and schema['isAccessibleForFree'] is True
 assert schema['potentialAction']['target']==pdf['url']
 md=path.with_suffix('.md').read_text()
 assert pdf['url'] in md and all(topic in md for topic in b['studyUses'])
 if b['clinical']:assert b['studyUses'][-1]+'\n\nFor study' in md,'Study topics and clinical note must be separate Markdown blocks'
 assert 'Sources last reviewed: '+source['reviewed'] in md
 assert url in (ROOT/'llms.txt').read_text() and b['title'] in (ROOT/'llms-full.txt').read_text()
print('PASS Vet eBooks: 25 verified direct PDF records, unique canonical cards, complete schema, dated mirrors and crawl/search coverage.')

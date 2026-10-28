"""Verify the visible hierarchy, its real destinations and structured-data parity."""
from pathlib import Path
import json,re
from html import unescape
ROOT=Path(__file__).resolve().parent.parent
checked=0
for p in ROOT.rglob('index.html'):
 if any(x in p.parts for x in ['node_modules','.git']):continue
 if p==ROOT/'index.html':continue
 raw=p.read_text();navs=re.findall(r'<nav class="breadcrumbs"[^>]*>(.*?)</nav>',raw,re.S)
 assert len(navs)==1,(p,'exactly one breadcrumb')
 nav=navs[0];assert nav.count('aria-current="page"')==1,(p,'current page')
 crumbs=[]
 for li in re.findall(r'<li>(.*?)</li>',nav,re.S):
  node=re.search(r'<a href="([^"]+)">(.*?)</a>',li,re.S)
  current=re.search(r'<span aria-current="page">(.*?)</span>',li,re.S)
  assert node or current,(p,'label')
  target=unescape(node[1]) if node else '/'+str(p.parent.relative_to(ROOT))+'/'
  label=unescape(node[2] if node else current[1])
  crumbs.append((label,target))
  if node:
   dest=target.split('#')[0];assert (ROOT/dest.strip('/')/'index.html').exists(),(p,'missing parent',dest)
   assert dest!='/clinical/',(p,'retired clinical parent')
 assert crumbs[0]==('Home','/'),p
 graph=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',raw,re.S)[1])['@graph']
 schema=next(x for x in graph if x['@type']=='BreadcrumbList')['itemListElement']
 assert crumbs==[(x['name'],x['item'].removeprefix('https://notes.thatvetguy.net')) for x in schema],(p,'HTML/schema mismatch')
 path='/'+str(p.parent.relative_to(ROOT))+'/'
 if path.endswith(('/syllabus/','/practicals/')):
  assert len(crumbs)==5 and crumbs[-2][1]==path.rsplit('/',2)[0]+'/',(p,'subject parent missing')
 if path.startswith('/books/') and path!='/books/':assert [u for _,u in crumbs[:-1]]==['/','/books/'],(p,'mixed academic/book hierarchy')
 if path.startswith('/study-tools/') and path!='/study-tools/':assert len(crumbs)==3 and crumbs[1][1]=='/study-tools/',p
 checked+=1
print(f'PASS breadcrumbs: {checked} pages; current page, real parents and JSON-LD agree.')

#!/usr/bin/env python3
"""Fail on a navigation or machine-index URL outside the Drive/Telegram/own-site policy."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import json
ROOT=Path(__file__).resolve().parent.parent
BASE='notes.thatvetguy.net';OWN={'thatvetguy.net','www.thatvetguy.net','blog.thatvetguy.net'}
def check_policy():
 data=json.loads((ROOT/'data/resources.json').read_text());allowed={v['url'] for r in data['files'] for v in r['variants']}|{v['download'] for r in data['files'] for v in r['variants'] if v.get('download')};telegram={'https://t.me/vetshortnotesbytvg','https://t.me/jobupdatesbytvg'};errors=[];counts=0
 from book_catalogue import books
 allowed|={b['telegram'] for b in books() if b.get('telegram')}
 from study_tools import allowed_urls
 tool_allowed=allowed_urls()
 curriculum=json.loads((ROOT/'data/msve-2016-source.json').read_text())['url']
 class Links(HTMLParser):
  def __init__(self,path):super().__init__();self.path=path;self.footer=False
  def handle_starttag(self,tag,attrs):
   nonlocal counts
   a=dict(attrs)
   if tag=='footer':self.footer=True
   if tag!='a':return
   url=a.get('href','');host=urlsplit(url).hostname
   if not url.startswith(('https://','http://')):return
   counts+=1
   if host==BASE:return
   if self.path.is_relative_to(ROOT/'study-tools') and url in tool_allowed:return
   if url in allowed or url in telegram or url.split('#')[0]==curriculum:return
   if host in OWN and self.footer:return
   errors.append((str(self.path.relative_to(ROOT)),url))
  def handle_endtag(self,tag):
   if tag=='footer':self.footer=False
 for path in ROOT.rglob('*.html'):
  if any(p in path.parts for p in ['docs','node_modules','.git','dist']):continue
  parser=Links(path);parser.feed(path.read_text())
 for r in json.loads((ROOT/'search-index.json').read_text()):
  if r['url'].startswith('https:') and r['url'] not in allowed:errors.append(('search-index.json',r['url']))
 if errors:raise AssertionError('Forbidden external links: '+repr(errors[:20]))
 print('PASS: strict link policy across generated HTML and the complete search index;',counts,'HTTP links checked.')
if __name__=='__main__':check_policy()

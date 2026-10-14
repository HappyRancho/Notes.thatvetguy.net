"""Public Drive HTML metadata reader. It never evaluates page scripts or uses frontend API keys."""
import json,re,time
from urllib.request import Request,urlopen
from html.parser import HTMLParser
FOLDER_MIME='application/vnd.google-apps.folder'
class Rows(HTMLParser):
 def __init__(self):super().__init__();self.ids=set();self.counts=[]
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t=='tr' and a.get('data-id'):self.ids.add(a['data-id'])
  if a.get('aria-rowcount','').isdigit():self.counts.append(int(a['aria-rowcount']))
def parse(html):
 match=re.search(r"window\['_DRIVE_ivd'\]\s*=\s*'((?:\\.|[^'\\])*)'",html)
 if not match:raise ValueError('No public folder metadata; access may require sign-in')
 literal=re.sub(r'\\x([0-9a-fA-F]{2})',lambda m:'\\u00'+m[1],match[1]).replace("\\'","'")
 decoded=json.loads('"'+literal+'"');data=json.loads(decoded)
 rows=Rows();rows.feed(html)
 entries=data[0] or []
 if not isinstance(entries,list):raise ValueError('Unrecognised public Drive data')
 return entries,{'embeddedCount':len(entries),'renderedCount':len(rows.ids),'ariaCounts':rows.counts,'tail':data[1:]}
def fetch(folder):
 req=Request('https://drive.google.com/drive/folders/'+folder,headers={'User-Agent':'Mozilla/5.0'})
 with urlopen(req,timeout=30) as r:html=r.read().decode('utf-8')
 return parse(html)

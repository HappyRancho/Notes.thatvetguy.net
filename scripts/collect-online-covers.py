"""Fetch researched cover candidates for human visual review, never auto-adopt."""
from pathlib import Path
from urllib.parse import urljoin
from html.parser import HTMLParser
from concurrent.futures import ThreadPoolExecutor
import json,io,base64
import requests
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'assets/books/online-review';OUT.mkdir(parents=True,exist_ok=True)
class Meta(HTMLParser):
 def __init__(self,html):super().__init__();self.images=[];self.feed(html)
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='meta' and a.get('property',a.get('name')) in ['og:image','twitter:image'] and a.get('content'):self.images.append(a['content'])
def fetch(s):
 try:
  url=s['url']
  if not url:
   page=requests.get(s['reference'],timeout=25);page.raise_for_status();images=Meta(page.text).images
   if not images:raise ValueError('No product image metadata')
   url=urljoin(s['reference'],images[0])
  r=requests.get(url,timeout=25);r.raise_for_status()
  with Image.open(io.BytesIO(r.content)) as im:
   im=im.convert('RGB');im.load();assert im.width>=90 and im.height>=125 and im.convert('L').entropy()>2
   im.thumbnail((520,760));p=OUT/(s['id']+'.webp');im.save(p,'WEBP',quality=85)
   return dict(id=s['id'],path='/assets/books/online-review/'+p.name,width=im.width,height=im.height,kind='reference-cover',source=url,reference=s['reference'])
 except Exception as ex:print('ONLINE_ERROR',s['id'],str(ex));return None
items=[r for r in ThreadPoolExecutor(max_workers=5).map(fetch,json.loads((ROOT/'data/cover-online-sources.json').read_text())) if r]
(ROOT/'data/cover-online-candidates.json').write_text(json.dumps(items,indent=2)+'\n')
sheet=Image.new('RGB',(1200,300*((len(items)+3)//4)),'#eaf8ff');d=ImageDraw.Draw(sheet);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',12)
for i,r in enumerate(items):
 x=i%4*300;y=i//4*300
 with Image.open(ROOT/r['path'].lstrip('/')) as im:im.thumbnail((280,260));sheet.paste(im,(x+(300-im.width)//2,y))
 d.text((x+5,y+265),str(i)+' '+r['id'][:36],fill='#101b43',font=font)
b=io.BytesIO();sheet.save(b,'JPEG',quality=82);print('ONLINE_SHEET '+base64.b64encode(b.getvalue()).decode())
print('ONLINE_RESULTS '+json.dumps(items))

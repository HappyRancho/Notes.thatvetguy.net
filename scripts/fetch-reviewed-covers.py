#!/usr/bin/env python3
"""Cache images from individually researched bibliographic cover sources."""
from pathlib import Path
from urllib.request import urlopen,Request
from concurrent.futures import ThreadPoolExecutor
from PIL import Image,ImageChops,ImageStat
from io import BytesIO
import json,hashlib
ROOT=Path(__file__).resolve().parent.parent
specs=json.loads((ROOT/'data/reviewed-cover-sources.json').read_text())
def fetch(s):
 try:
  with urlopen(Request(s['url'],headers={'User-Agent':'Mozilla/5.0'}),timeout=25) as response:raw=response.read(5_000_000)
  with Image.open(BytesIO(raw)) as im:
   im=im.convert('RGB');assert im.width>=100 and im.height>=140
   # Remove only plain white margins around retailer product photography.
   diff=ImageChops.difference(im,Image.new('RGB',im.size,(255,255,255))).convert('L').point(lambda x:255 if x>35 else 0);box=diff.getbbox()
   if box and box[2]-box[0]>100 and box[3]-box[1]>140:im=im.crop(box)
   assert ImageStat.Stat(im).stddev[0]>15
   im.thumbnail((500,700));path=ROOT/'assets/books'/('verified-'+s['id']+'.webp');im.save(path,'WEBP',quality=85,method=6)
   return s['id'],dict(path='/assets/books/'+path.name,width=im.width,height=im.height,source=s['url'],reference=s['reference'],kind='reference-cover',sha256=hashlib.sha256(path.read_bytes()).hexdigest())
 except Exception as exc:print('COVER_FAILED',s['id'],str(exc),flush=True);return s['id'],None
covers=dict(ThreadPoolExecutor(max_workers=4).map(fetch,specs));(ROOT/'data/reviewed-cover-results.json').write_text(json.dumps(covers,indent=2)+'\n');print('COVERS_FETCHED',sum(bool(c) for c in covers.values()),flush=True)

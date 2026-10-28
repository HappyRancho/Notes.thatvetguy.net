"""Retain small, attributed icons from the exact Google Play listings; never APKs."""
import concurrent.futures, io, json, re, urllib.request
from html import unescape
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
APPS={'vetconnect':'com.vetconnect.user.vetconnect','vet-study':'com.asr.vetstudy2','ivri-clinical':'com.icar.ivri.iasri.veterinaryclinicalcareapp','msd-veterinary':'com.msd.veterinary','dog-anatomy':'com.biosphera.doganatomy','cat-anatomy':'com.biosphera.catanatomy','horse-anatomy':'com.biosphera.horseanatomy','pig-anatomy':'com.biosphera.piganatomy','goat-anatomy':'com.biosphera3d.caprineanatomy','bird-anatomy':'com.biosphera.birdanatomy'}
def get(url):
 req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
 with urllib.request.urlopen(req,timeout=35) as response:return response.read(4_000_000)
def save(pair):
 key,package=pair;url='https://play.google.com/store/apps/details?id='+package+'&hl=en_US';html=get(url).decode()
 tags=re.findall(r'<meta\b[^>]+>',html)
 image=next(unescape(re.search(r'content="([^"]+)"',t).group(1)) for t in tags if 'property="og:image"' in t)
 assert image.startswith('https://play-lh.googleusercontent.com/'),image
 raw=get(image);im=Image.open(io.BytesIO(raw)).convert('RGBA');im.thumbnail((128,128))
 dest=ROOT/'assets/tools/apps'/f'{key}.webp';dest.parent.mkdir(parents=True,exist_ok=True);im.save(dest,'WEBP',quality=88,method=6)
 return {'id':key,'package':package,'listing':url,'imageSource':image,'icon':'/'+str(dest.relative_to(ROOT)),'width':im.width,'height':im.height}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(save,APPS.items()))
(ROOT/'data/app-icon-sources.json').write_text(json.dumps({'checked':'2026-10-28','apps':rows},ensure_ascii=False,indent=2)+'\n')
print('Imported',len(rows),'original Play icons; total',sum((ROOT/r['icon'].lstrip('/')).stat().st_size for r in rows),'bytes')

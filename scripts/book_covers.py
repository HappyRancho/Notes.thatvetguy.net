"""Reviewed original covers, with clearly identified symbolic artwork as a last resort."""
from pathlib import Path
from functools import lru_cache
from hashlib import sha256
import json,io
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent.parent
@lru_cache(maxsize=1)
def selections():
 p=ROOT/'data/book-cover-selections.json'
 return json.loads(p.read_text()) if p.exists() else {}
@lru_cache(maxsize=2)
def font_bytes(name):
 from fontTools.ttLib import TTFont
 f=TTFont(ROOT/'assets/fonts'/f'{name}-latin.woff2');f.flavor=None;b=io.BytesIO();f.save(b);return b.getvalue()
def font(name,size):return ImageFont.truetype(io.BytesIO(font_bytes(name)),size)
def wrapped(draw,text,f,width):
 lines=[];line=''
 for word in text.split():
  proposed=(line+' '+word).strip()
  if draw.textlength(proposed,font=f)>width and line:lines.append(line);line=word
  else:line=proposed
 if line:lines.append(line)
 return lines

def symbolic(book):
 title=book['title'];author=book.get('author') or 'Author not listed'
 tones=[('#e3f4ff','#0866ad'),('#e5f6ee','#176c55'),('#f0eaff','#61438c'),('#fff0e4','#a45027')]
 bg,accent=tones[int(sha256(book['id'].encode()).hexdigest()[:4],16)%len(tones)]
 p=ROOT/'assets/books'/('symbolic-'+book['id']+'.webp');stamp=sha256(('v2|'+title+'|'+author).encode()).hexdigest()
 # Deterministic images are self-hosted; no browser dependency or network fallback.
 im=Image.new('RGB',(500,750),bg);d=ImageDraw.Draw(im)
 d.rectangle((0,0,18,750),fill=accent);d.rectangle((18,0,24,750),fill='#ffffff')
 d.rounded_rectangle((51,38,449,84),radius=23,fill='white');d.text((70,50),'RX NOTES  /  '+book['type'].upper(),font=font('inter',16),fill=accent)
 # A minimal open book and veterinary paw; original symbolic artwork.
 d.rounded_rectangle((326,109,447,222),radius=28,fill='white')
 d.line([(343,139),(366,134),(386,143),(407,134),(431,139),(431,190),(407,185),(386,194),(366,185),(343,190),(343,139)],fill=accent,width=4)
 d.line((386,144,386,194),fill=accent,width=3)
 d.ellipse((58,137,88,163),fill=accent);d.ellipse((91,126,117,153),fill=accent);d.ellipse((123,137,149,163),fill=accent);d.ellipse((80,165,131,203),fill=accent)
 for size in range(47,25,-1):
  f=font('balsamiq',size);lines=wrapped(d,title,f,392)
  if len(lines)*(size+7)<=304:break
 y=252
 for line in lines:d.text((54,y),line,font=f,fill='#101b43');y+=size+7
 d.line((54,590,170,590),fill=accent,width=5)
 af=font('inter',22);lines=wrapped(d,author,af,390)
 if len(lines)>3:af=font('inter',18);lines=wrapped(d,author,af,390)
 for i,line in enumerate(lines):d.text((54,612+i*27),line,font=af,fill='#334461')
 d.text((54,714),'SYMBOLIC COVER',font=font('inter',13),fill=accent)
 p.parent.mkdir(exist_ok=True);im.save(p,'WEBP',quality=88,method=4)
 return dict(path='/assets/books/'+p.name,width=500,height=750,kind='symbolic-cover',source='Rx Notes original symbolic artwork',title=title,author=author,fingerprint=stamp)

def resolve(book):
 s=selections();chosen=s.get('covers',{}).get(book['id']);current=book.get('cover')
 if chosen:
  assert (ROOT/chosen['path'].lstrip('/')).exists(),f'Missing reviewed cover: {book["id"]}'
  return dict(chosen)
 if book['id'] not in s.get('replacePreviews',[]) and current and current['kind'] in ['file-cover','reference-cover']:return current
 return symbolic(book)

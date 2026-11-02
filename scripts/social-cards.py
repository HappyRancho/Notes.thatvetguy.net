#!/usr/bin/env python3
"""Render Rx Notes share cards from bundled fonts; content-addressed JPEG URLs."""
from PIL import Image,ImageDraw,ImageFont
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from pathlib import Path
from io import BytesIO
import hashlib,json
from functools import lru_cache
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'assets/social';OUT.mkdir(exist_ok=True)
NAVY='#101b43';BLUE='#0769ce';MUTED='#475571';SKY='#eaf8ff'
@lru_cache(maxsize=None)
def font(name,size,weight=400):
    t=TTFont(ROOT/f'assets/fonts/{name}-latin.woff2')
    if 'fvar' in t:
        axes={a.axisTag:weight for a in t['fvar'].axes if a.axisTag=='wght'}
        if axes:t=instantiateVariableFont(t,axes,inplace=True)
    t.flavor=None;buf=BytesIO();t.save(buf);buf.seek(0)
    return ImageFont.truetype(buf,size)
heading=font('balsamiq',62,700);hand=font('caveat',43,500);sans=font('inter',24);small=font('inter',20)
sections={
 'home':('Free Veterinary','Academic Resources','Thoughtfully organised for future vets.',['BVSc Notes','Books & MCQs','Clinical References']),
 'bvsc':('Your year. Your subjects.','A clearer way to study.','Notes, books, checklists & year-start guides.',['1st Year','2nd Year','3rd Year','4th Year']),
 'objective':('Build your confidence.','One question at a time.','Objective notes & veterinary question banks.',['Objective Notes','Question Banks','Revision']),
 'study-tools':('A smarter study kit.','A wider world of veterinary.','Apps, notes websites & career guidance.',['Vet Apps','Notes Websites','Career Options']),
 'clinical':('Keep clinical references','close at hand.','Handbooks, drug indexes & veterinary resources.',['Handbooks','Drug Index','Clinical Learning']),
 'search':('Find your next','veterinary reference.','Search notes, books, question banks & more.',['Notes','Books','Question Banks']),
 'about':('Made for future vets.','Built around your studies.','Meet the library behind Rx Notes.',['BVSc & AH','Organised Resources','ThatVetGuy']),
 'request-resource':('Help your next batch','find their next good read.','Request a resource, contribute or report a link.',['Request','Contribute','Report a Link'])}
manifest={}
for key,(line1,line2,subtitle,tags) in sections.items():
    im=Image.new('RGB',(1200,630),SKY);d=ImageDraw.Draw(im)
    # A prescription-paper masthead with the site's own typefaces and syringe.
    d.rounded_rectangle((28,24,1172,606),radius=30,fill='white')
    d.polygon([(546,24),(691,24),(686,44),(552,51),(557,38)],fill='#b8dbef')
    d.text((66,40),'R',font=font('caveat',44,500),fill=BLUE);d.text((91,63),'x',font=font('caveat',25,500),fill=BLUE)
    logo_font=font('balsamiq',69,700)
    d.text((66,77),'No',font=logo_font,fill=NAVY)
    no_width=d.textlength('No',font=logo_font)
    syringe=Image.open(ROOT/'assets/home/syringe.webp').convert('RGBA');syringe.thumbnail((18,100))
    sx=round(66+no_width+2);im.paste(syringe,(sx,57),syringe)
    d.text((sx+17,77),'es',font=logo_font,fill=NAVY)
    d.text((260,113),'by thatvetguy',font=font('caveat',29,500),fill=NAVY)
    d.line((292,145,408,139),fill='#ef6e7a',width=3)
    d.text((839,77),'notes.thatvetguy.net',font=font('inter',22,500),fill=MUTED)
    d.line((65,168,1134,168),fill='#dcecf5',width=2)
    # The content is deliberately legible at messaging-preview size.
    chosen=heading
    for size in range(62,44,-2):
        chosen=font('balsamiq',size,700)
        if max(d.textlength(t,font=chosen) for t in [line1,line2])<=1058:break
    d.text((66,204),line1,font=chosen,fill=NAVY)
    d.text((66,282),line2,font=chosen,fill=NAVY)
    subfont=hand
    if d.textlength(subtitle,font=subfont)>1040:subfont=font('caveat',37,500)
    if key=='home':
        prefix='Thoughtfully organised for ';x=66+d.textlength(prefix,font=subfont)
        d.rectangle((int(x)-3,378,int(x+d.textlength('future vets.',font=subfont))+5,414),fill='#fff1a4')
    d.text((66,366),subtitle,font=subfont,fill=MUTED)
    x=66;tones=['#e8f6ff','#e8f6ee','#fff5cf','#f1e8ff']
    for i,tag in enumerate(tags):
        width=round(d.textlength(tag,font=sans))+42
        d.rounded_rectangle((x,456,x+width,511),radius=15,fill=tones[i%4])
        d.text((x+21,470),tag,font=sans,fill=NAVY);x+=width+12
    d.text((66,550),'FREE RESOURCES FOR BVSc & AH STUDENTS',font=small,fill=MUTED)
    # Small paw stamp, matching the pale blue motif in the site header.
    for x,y in [(1086,548),(1103,538),(1122,541),(1136,555)]:d.ellipse((x-5,y-8,x+5,y+8),fill='#b6d9f4')
    d.rounded_rectangle((1095,559,1129,582),radius=11,fill='#b6d9f4')
    encoded=BytesIO();im.save(encoded,'JPEG',quality=90,optimize=True,subsampling=0)
    raw=encoded.getvalue();digest=hashlib.sha256(raw).hexdigest()[:12];name=f'rx-{key}-{digest}.jpg'
    (OUT/name).write_bytes(raw)
    manifest[key]={'path':'/assets/social/'+name,'width':1200,'height':630,'type':'image/jpeg','alt':f'Rx Notes by ThatVetGuy — {line1} {line2}'}
(ROOT/'data/social-cards.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Generated',len(sections),'Rx-themed JPEG previews (1200×630), with content-addressed URLs.')

#!/usr/bin/env python3
"""Generate lightweight, section-specific 1200×630 social previews."""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'assets/social';OUT.mkdir(exist_ok=True)
serif='/tmp/bricolage-social.ttf'
sans='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
if not Path(serif).exists():serif=sans
sections={'home':('A little less searching.','A lot more studying.','The veterinary student’s open shelf.'),'bvsc':('Your year. Your subjects.','Your next good read.','BVSc notes & books · Four professional years'),'objective':('Good revision starts','with better questions.','ICAR PYQs · Subject-wise questions · Objective books'),'study-tools':('Make room for','a better study day.','Practical AI guides · Free apps · Useful tools'),'clinical':('Keep the essentials','close at hand.','Veterinary handbooks & professional references'),'search':('Find your next','useful reference.','Search notes, books, PYQs & study tools'),'about':('Made for curious minds.','And future vets.','About Notes.ThatVetGuy'),'request-resource':('A better library','starts with you.','Request a resource · Contribute · Report a link')}
for key,(a,b,sub) in sections.items():
 im=Image.new('RGB',(1200,630),'#FFF8EC');d=ImageDraw.Draw(im)
 d.rounded_rectangle((52,48,1148,582),radius=24,outline='#14231F',width=2)
 d.rectangle((52,48,64,582),fill='#14231F')
 d.text((100,88),'Notes.ThatVetGuy',fill='#14231F',font=ImageFont.truetype(sans,30))
 d.text((100,196),a,fill='#14231F',font=ImageFont.truetype(serif,60))
 d.text((100,278),b,fill='#14231F',font=ImageFont.truetype(serif,60))
 d.text((103,402),sub,fill='#3A4A45',font=ImageFont.truetype(sans,24))
 d.line((100,484,1092,484),fill='#14231F',width=2)
 d.text((100,517),'FREE ACADEMIC RESOURCES FOR FUTURE VETS',fill='#14231F',font=ImageFont.truetype(sans,18))
 # Restrained veterinary cross, like the imprint on a handbook.
 d.rounded_rectangle((1020,84,1100,164),radius=16,fill='#C8F169')
 d.line((1060,103,1060,145),fill='#14231F',width=8);d.line((1039,124,1081,124),fill='#14231F',width=8)
 im.save(OUT/(key+'.webp'),'WEBP',quality=84,method=6)
print('Generated',len(sections),'section previews (1200×630).')

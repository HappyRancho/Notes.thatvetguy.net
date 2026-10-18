#!/usr/bin/env python3
"""Download OFL sources at build time and self-host small Latin WOFF2 subsets."""
from pathlib import Path
from urllib.request import urlopen,Request
from urllib.parse import quote
from io import BytesIO
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools import subset
ROOT=Path(__file__).resolve().parent.parent;OUT=ROOT/'assets/fonts';OUT.mkdir(exist_ok=True)
SOURCES=[('bricolage','bricolagegrotesque','BricolageGrotesque[opsz,wdth,wght].ttf',{'opsz':32,'wdth':100,'wght':(700,800)}),('inter','inter','Inter[opsz,wght].ttf',{'opsz':14,'wght':(400,600)}),('caveat','caveat','Caveat[wght].ttf',{'wght':500})]
for name,folder,filename,axes in SOURCES:
    dest=OUT/(name+'-latin.woff2')
    if dest.exists():continue
    base='https://raw.githubusercontent.com/google/fonts/main/ofl/'+folder+'/'
    with urlopen(Request(base+quote(filename),headers={'User-Agent':'NotesThatVetGuy-build'}),timeout=30) as r:raw=r.read()
    font=instantiateVariableFont(TTFont(BytesIO(raw)),axes,inplace=True)
    # Instancing can synthesise spacing glyphs without gvar entries. They are static.
    if 'gvar' in font:
        for glyph in font.getGlyphOrder():
            if glyph not in font['gvar'].variations:font['gvar'].variations[glyph]=[]
    options=subset.Options();options.flavor='woff2';options.layout_features=['kern','liga','calt'];options.name_IDs=[1,2,3,4,5,6];options.recalc_bounds=True
    sub=subset.Subsetter(options=options);sub.populate(unicodes=list(range(32,256))+list(range(0x2000,0x2070))+[0x2192,0x2197,0x21b3]);sub.subset(font)
    font.flavor='woff2';font.save(dest)
    with urlopen(base+'OFL.txt',timeout=30) as r:(OUT/(name+'-OFL.txt')).write_bytes(r.read())
    # Social-card rendering uses an uncompressed local font, never a client request.
    font.flavor=None;font.save('/tmp/'+name+'-social.ttf')
    print(name,dest.stat().st_size,'bytes; self-hosted OFL subset')

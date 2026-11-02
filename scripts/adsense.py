"""Verification is independent of advertising; placements fail closed by default."""
from pathlib import Path
from html.parser import HTMLParser
from html import escape
import json,re
ROOT=Path(__file__).resolve().parent.parent
CONFIG=json.loads((ROOT/'data/adsense.json').read_text())
assert re.fullmatch(r'ca-pub-\d{16}',CONFIG['publisherId'])
def verification(config=CONFIG):
    if not config.get('verificationEnabled'):return ''
    return '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client='+config['publisherId']+'"\n     crossorigin="anonymous"></script>'
def ads_txt(config=CONFIG):
    return 'google.com, '+config['publisherId'].removeprefix('ca-')+', DIRECT, f08c47fec0942fa0\n'
def component(key,config=CONFIG):
    placement=config['placements'][key]
    if not all(config.get(k) is True for k in ['approved','renderEnabled','autoAdsOffConfirmed']):return ''
    slot=placement.get('slotId')
    if placement.get('enabled') is not True or not isinstance(slot,str) or not re.fullmatch(r'\d{10}',slot):return ''
    return '<aside class="rx-ad" aria-label="Advertisement" data-rx-ad="'+escape(key,quote=True)+'"><span class="rx-ad-label">Advertisement</span><div class="rx-ad-frame"><ins class="adsbygoogle rx-ad-unit" data-rx-ad-unit data-ad-client="'+config['publisherId']+'" data-ad-slot="'+slot+'" data-full-width-responsive="false"></ins></div></aside>'
class SectionEnd(HTMLParser):
    def __init__(self,html,ident):
        super().__init__();self.ident=ident;self.depth=0;self.end=None;self.lines=html.splitlines(keepends=True)
    def handle_starttag(self,tag,attrs):
        if tag=='section' and (self.depth or dict(attrs).get('id')==self.ident):self.depth+=1
    def handle_endtag(self,tag):
        if tag=='section' and self.depth:
            self.depth-=1
            if not self.depth:
                line,col=self.getpos();self.end=sum(map(len,self.lines[:line-1]))+col+len('</section>')
def insert(body,path,config=CONFIG):
    matches=[(key,p['pages'][path]) for key,p in config['placements'].items() if path in p['pages']]
    assert len(matches)<=1,'Only one advertisement placement per page'
    if not matches:return body
    key,ident=matches[0];parser=SectionEnd(body,ident);parser.feed(body)
    assert parser.end is not None,('Ad placement section missing',path,ident)
    html=component(key,config)
    # Inactive hooks are comments: no blank space, labels, ins elements or requests.
    return body[:parser.end]+'<!-- rx-ad-placement:'+key+' -->'+html+body[parser.end:]

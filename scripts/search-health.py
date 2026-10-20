#!/usr/bin/env python3
"""Public HTTP crawl diagnostics. UA probes do not authenticate real search bots."""
import argparse, concurrent.futures, json, re, time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
BASE = 'https://notes.thatvetguy.net'
def fetch(url, ua='NotesThatVetGuy-SearchHealth/1'):
    start = time.monotonic()
    try:
        try: response = urlopen(Request(url, headers={'User-Agent': ua}), timeout=20)
        except HTTPError as error: response = error
        with response:
            raw = response.read(3000000).decode('utf-8', 'replace')
            headers = {k.lower(): v for k, v in response.headers.items() if k.lower() in ['content-type','x-robots-tag','cf-mitigated','server','location','link','cf-cache-status']}
            result = {'url':url,'finalURL':response.url,'status':response.status,'headers':headers,'seconds':round(time.monotonic()-start,3)}
        for key, pattern in {'title':r'<title>(.*?)</title>','canonical':r'<link rel="canonical" href="([^"]+)"','robots':r'<meta name="robots" content="([^"]+)"','build':r'<meta name="site-build" content="([^"]+)"'}.items():
            match = re.search(pattern, raw, re.S|re.I);result[key]=match[1] if match else None
        result['h1Count']=len(re.findall(r'<h1\b',raw,re.I))
        return result,raw
    except Exception as error: return {'url':url,'error':type(error).__name__+': '+str(error)},''

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--label',default='live');args=parser.parse_args()
    urls=[node.text for node in ET.parse(ROOT/'sitemap.xml').getroot().iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
    extras=['/robots.txt','/sitemap.xml','/llms.txt','/llms-full.txt','/search-index.json','/search/','/definitely-missing-search-health-check/','/bvsc/year-1/veterinary-anatomy/','/bvsc/year-1/notes/index.md','/index.html']
    targets=urls+[BASE+p for p in extras]+['http://notes.thatvetguy.net/','https://notes-thatvetguy-net.pages.dev/','https://notes-thatvetguy-net.pages.dev/bvsc/year-1/']
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool: responses=list(pool.map(fetch,targets))
    report={'label':args.label,'checkedAt':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'pages':[r for r,_ in responses],'findings':[],'botUserAgentProbes':[]}
    for result,raw in responses:
        url=result['url']
        if url in urls:
            if result.get('status')!=200:report['findings'].append({'url':url,'issue':'Sitemap page does not return 200'})
            if result.get('canonical')!=url:report['findings'].append({'url':url,'issue':'Canonical does not match sitemap URL'})
            if 'noindex' in (str(result.get('robots'))+' '+result.get('headers',{}).get('x-robots-tag','')).lower():report['findings'].append({'url':url,'issue':'Indexable page has noindex'})
            if result.get('h1Count')!=1:report['findings'].append({'url':url,'issue':'Expected one H1'})
        if '/definitely-missing-' in url and result.get('status')!=404:report['findings'].append({'url':url,'issue':'Missing URL does not return 404'})
        if url.endswith('/robots.txt'):report['robotsText']=raw
    for name,ua in [('Googlebot','Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'),('Bingbot','Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)'),('OAI-SearchBot','OAI-SearchBot/1.3; +https://openai.com/searchbot')]:
        result,_=fetch(BASE+'/',ua);result['name']=name;report['botUserAgentProbes'].append(result)
    out=ROOT/'docs/qa/search';out.mkdir(parents=True,exist_ok=True);(out/(args.label+'.json')).write_text(json.dumps(report,indent=2)+'\n')
    print('SEARCH_HEALTH '+json.dumps(report))
    # A public network error is diagnostic evidence, not proof of an indexing block.
    return report
if __name__=='__main__':main()

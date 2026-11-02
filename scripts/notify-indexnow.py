#!/usr/bin/env python3
"""Notify participating search engines after deploy; acceptance is not indexing."""
import argparse,json,re,subprocess,sys,time
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent.parent
BASE='https://notes.thatvetguy.net'
ENDPOINT='https://api.indexnow.org/indexnow'
def previous(path):
    result=subprocess.run(['git','show','HEAD^:'+path],cwd=ROOT,text=True,capture_output=True)
    return result.stdout if result.returncode==0 else None

def urls(xml):
    return {x.text for x in ET.fromstring(xml).iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')}

def changed(current,old,current_history,old_history,first=False):
    if first:return sorted(current)
    return sorted((current^old)|{u for u in current&old if current_history.get(u.removeprefix(BASE),{}).get('sha256')!=old_history.get(u.removeprefix(BASE),{}).get('sha256')})

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--dry-run',action='store_true');args=parser.parse_args()
    config=json.loads((ROOT/'data/indexnow.json').read_text());key_path=config['keyFile']
    key=(ROOT/key_path.lstrip('/')).read_text().strip()
    assert re.fullmatch(r'[a-f0-9]{32}',key) and re.fullmatch(r'/[A-Za-z0-9-]+\.txt',key_path),'Invalid key file'
    current=urls((ROOT/'sitemap.xml').read_text());old_xml=previous('sitemap.xml');old_history=previous('data/page-history.json')
    old_config=previous('data/indexnow.json')
    first=previous(key_path.lstrip('/')) is None or (json.loads(old_config).get('submissionBatch') if old_config else None)!=config.get('submissionBatch')
    if not first and (old_xml is None or old_history is None):raise RuntimeError('Previous deployment is required to select changed URLs; use checkout fetch-depth: 2')
    selected=changed(current,urls(old_xml) if old_xml else set(),json.loads((ROOT/'data/page-history.json').read_text()),json.loads(old_history) if old_history else {},first)
    assert all(u.startswith(BASE+'/') and not any(c in u for c in ['?','#']) for u in selected)
    report={'checkedAt':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'firstSubmission':first,'urls':selected,'count':len(selected),'status':'dry-run' if args.dry_run else 'no-changes','note':'Acceptance is not a guarantee of crawling, indexing or ranking. Google does not use IndexNow.'}
    if selected and not args.dry_run:
        try:
            # Confirm the public key and live sitemap before notifying any search engine.
            with urlopen(Request(BASE+key_path,headers={'User-Agent':'NotesThatVetGuy-IndexNow/1'}),timeout=25) as response:
                if response.read().decode().strip()!=key:raise RuntimeError('Published key does not match this build')
            with urlopen(Request(BASE+'/sitemap.xml',headers={'User-Agent':'NotesThatVetGuy-IndexNow/1'}),timeout=25) as response:
                if urls(response.read())!=current:raise RuntimeError('Published sitemap does not match this build')
            payload={'host':'notes.thatvetguy.net','key':key,'keyLocation':BASE+key_path,'urlList':selected}
            request=Request(ENDPOINT,data=json.dumps(payload).encode(),headers={'Content-Type':'application/json; charset=utf-8','User-Agent':'NotesThatVetGuy-IndexNow/1'},method='POST')
            try:
                with urlopen(request,timeout=30) as response:code=response.status
            except HTTPError as error:code=error.code
            report['httpStatus']=code;report['status']='accepted' if code==200 else 'accepted-key-validation-pending' if code==202 else 'not-accepted'
        except (HTTPError,URLError,RuntimeError,TimeoutError) as error:
            report['status']='preflight-or-network-error';report['error']=str(error);report['errorURL']=getattr(error,'url',None)
    out=ROOT/'docs/qa/search';out.mkdir(parents=True,exist_ok=True);(out/'indexnow.json').write_text(json.dumps(report,indent=2)+'\n')
    print('INDEXNOW '+json.dumps(report))
    if report['status'] in ['not-accepted','preflight-or-network-error']:raise SystemExit(1)
if __name__=='__main__':main()

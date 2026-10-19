#!/usr/bin/env python3
"""Verify production bytes and optionally perform the explicitly requested cache purge."""
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError
import os,json,hashlib,re
ROOT=Path(__file__).resolve().parent.parent
out=ROOT/'docs/qa/task2-production';out.mkdir(parents=True,exist_ok=True)
report={'purge':'not attempted: Cloudflare token/zone unavailable','pages':[]}
token=os.getenv('CLOUDFLARE_API_TOKEN') or os.getenv('CF_API_TOKEN');zone=os.getenv('CLOUDFLARE_ZONE_ID') or os.getenv('CF_ZONE_ID')
if token and zone:
 try:
  req=Request('https://api.cloudflare.com/client/v4/zones/'+zone+'/purge_cache',data=b'{"purge_everything":true}',headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'},method='POST')
  with urlopen(req,timeout=30) as response:result=json.load(response)
  report['purge']='success' if result.get('success') else 'failed'
 except Exception as e:report['purge']='failed: '+type(e).__name__
for path in ['/','/bvsc/','/objective/','/study-tools/','/clinical/handbooks/','/clinical/drug-index/','/search/','/about/','/request-resource/']:
 record={'path':path}
 try:
  req=Request('https://notes.thatvetguy.net'+path,headers={'User-Agent':'NotesThatVetGuy-DeployAudit/2','Cache-Control':'no-cache'})
  with urlopen(req,timeout=25) as response:
   raw=response.read();record.update(status=response.status,headers={k:response.headers.get(k) for k in ['cf-cache-status','age','etag','last-modified','cf-ray']})
  html=raw.decode('utf-8');local=(ROOT/('index.html' if path=='/' else path.strip('/')+'/index.html')).read_bytes()
  local_html=local.decode('utf-8')
  pattern=r'<meta name="site-build" content="([^"]+)"'
  live_build=re.search(pattern,html);repo_build=re.search(pattern,local_html)
  assets=lambda text:re.findall(r'(?:href|src)="(/assets/(?:site\.css|site\.js|logic\.js|theme\.js)[^"]*)"',text)
  record.update(buildMatches=bool(live_build and repo_build and live_build[1]==repo_build[1]),liveBuild=live_build[1] if live_build else None,repoBuild=repo_build[1] if repo_build else None,assetVersionsMatch=assets(html)==assets(local_html))
  record.update(sha256=hashlib.sha256(raw).hexdigest(),repoSha256=hashlib.sha256(local).hexdigest(),matchesRepo=raw==local,oldExploreHeading=bool(re.search(r'<h2\b[^>]*>\s*Explore\.',html)),orphanObjective='Past papers: a reality check, without the viva.' in html)
 except Exception as e:record.update(status='unverified',reason=type(e).__name__+': '+str(e))
 report['pages'].append(record)
(out/'deployment.json').write_text(json.dumps(report,indent=2)+'\n');print('DEPLOY_AUDIT '+json.dumps(report))
raise SystemExit(0 if all((p.get('matchesRepo') or p.get('buildMatches')) for p in report['pages']) else 1)

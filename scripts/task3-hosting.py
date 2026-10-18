#!/usr/bin/env python3
"""Bounded public hosting diagnosis, including the Pages alias and build identity."""
import socket,json,re
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from pathlib import Path
out=Path('docs/qa/task3');out.mkdir(parents=True,exist_ok=True)
local=json.loads(Path('build-info.json').read_text()) if Path('build-info.json').exists() else {}
report=[]
for host in ['notes-thatvetguy-net.pages.dev','notes.thatvetguy.net']:
    row={'host':host}
    try:row['addresses']=sorted({v[4][0] for v in socket.getaddrinfo(host,443,type=socket.SOCK_STREAM)})
    except Exception as ex:row['dnsError']=str(ex)
    try:
        req=Request('https://'+host+'/',headers={'User-Agent':'NotesThatVetGuy-QA/3','Cache-Control':'no-cache'})
        try:response=urlopen(req,timeout=12)
        except HTTPError as ex:response=ex
        with response:
            text=response.read(500000).decode('utf-8','replace');row.update(status=response.status,finalURL=response.url,headers={k:response.headers.get(k) for k in ['server','cf-cache-status','location','cf-ray']})
        marker=re.search(r'<meta name="site-build" content="([^"]+)"',text);row['liveBuild']=marker[1] if marker else None;row['expectedBuild']=local.get('build');row['matchesBuild']=row['liveBuild']==local.get('build') if marker else False
        title=re.search('<title>(.*?)</title>',text,re.S);row['title']=title[1] if title else None;row['bodyExcerpt']=re.sub('<[^>]+>',' ',text)[:600]
    except Exception as ex:row['httpError']=type(ex).__name__+': '+str(ex)
    report.append(row)
(out/'hosting.json').write_text(json.dumps(report,indent=2)+'\n');print('TASK3_HOSTING '+json.dumps(report))

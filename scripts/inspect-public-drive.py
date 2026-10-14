#!/usr/bin/env python3
"""Read the supplied public folder pages; do not infer missing file metadata."""
import json,re
from pathlib import Path
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parent.parent
FOLDERS={'1':'18FGhR7f03vR1gXpkVwkuTYOx6c-Xk1a3','2':'12WNUVTXyjCDLLqhCUfZ12eCetQhKihte','3':'1u1HaIPxbTPI7tlu6iVt6T0gh5H4oNDFS','4':'11z4OHfm9OCQvpfekbgOMQGwHj2E5hva5'}
out=ROOT/'docs/qa/task2-drive';out.mkdir(parents=True,exist_ok=True)
for year,fid in FOLDERS.items():
 try:
  with urlopen(Request('https://drive.google.com/drive/folders/'+fid,headers={'User-Agent':'Mozilla/5.0'}),timeout=30) as r:html=r.read().decode('utf-8');status=r.status
  (out/('year-'+year+'.html')).write_text(html)
  markers={k:[html[max(0,m.start()-80):m.start()+700] for m in list(re.finditer(re.escape(k),html))[:2]] for k in ['_DRIVE_ivd','data-id=','application/ld+json','AF_initDataCallback','window.WIZ_global_data']}
  print('DRIVE_INSPECT '+json.dumps({'year':year,'status':status,'length':len(html),'title':re.findall('<title>(.*?)</title>',html),'markers':markers}))
 except Exception as e:print('DRIVE_INSPECT '+json.dumps({'year':year,'error':type(e).__name__+': '+str(e)}))

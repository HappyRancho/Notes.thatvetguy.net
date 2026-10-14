#!/usr/bin/env python3
"""Exercise real API pagination/recursion and classification boundary cases without credentials."""
import json
from io import BytesIO
from urllib.parse import urlsplit,parse_qs
from drive_manifest import list_children,import_api,FOLDERS,validate
from library import subject_for,clean_title,natural
calls=[]
def request(req,timeout=30):
 q=parse_qs(urlsplit(req.full_url).query);calls.append(q)
 assert 'key='not in req.full_url and q['pageSize']==['1000']
 parent=q['q'][0].split("'")[1]
 if parent==FOLDERS[1] and 'pageToken'not in q:payload={'files':[{'id':'testFolder12345','name':'Anatomy','mimeType':'application/vnd.google-apps.folder'}],'nextPageToken':'page2'}
 elif parent==FOLDERS[1]:payload={'files':[{'id':'testFile1234567','name':'Anatomy_2.pdf','mimeType':'application/pdf','size':'24999999','modifiedTime':'2025-01-01T00:00:00Z'}]}
 elif parent=='testFolder12345':payload={'files':[{'id':'testFile9876543','name':'Anatomy_10.pdf','mimeType':'application/pdf','size':'25000000','modifiedTime':'2025-01-02T00:00:00Z'}]}
 else:payload={'files':[]}
 return BytesIO(json.dumps(payload).encode())
files=validate(import_api('test-only-key',request))
assert len(files)==2 and any('pageToken'in c for c in calls)
assert len({c['q'][0]for c in calls})==5
assert clean_title('ANATOMY_lecture_2.PDF')=='ANATOMY lecture 2'
assert sorted(['note 10','note 2'],key=natural)==['note 2','note 10']
print('PASS: API v3 page tokens, nested folders, requested fields, key isolation, title cleanup and natural sorting.')

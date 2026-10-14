from pathlib import Path
import hashlib,json
roots=['assets','data','scripts','docs','bvsc','objective','study-tools','clinical','search','about','request-resource','404','.github']
files=[Path(p) for p in ['index.html','404.html','index.md','README.md','robots.txt','sitemap.xml','llms.txt','llms-full.txt','search-index.json','build-info.json','package.json','.nojekyll'] if Path(p).exists()]
for folder in roots:
 if Path(folder).exists():files.extend(p for p in Path(folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix in ['.html','.css','.js','.cjs','.mjs','.py','.json','.md','.txt','.xml','.svg','.yml'])
print(json.dumps([{'path':str(p),'hash':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(set(files))]))

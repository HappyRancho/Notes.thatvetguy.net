"""Keep only visually reviewed artwork from the one-off source audit."""
from pathlib import Path
import json,shutil
ROOT=Path(__file__).resolve().parent.parent
for c in json.loads((ROOT/'data/book-cover-selections.json').read_text())['covers'].values():
 dest=ROOT/c['path'].lstrip('/')
 if not dest.exists():shutil.copyfile(ROOT/c['candidatePath'].lstrip('/'),dest)
for name in ['audit','online-review']:
 p=ROOT/'assets/books'/name
 if p.exists():shutil.rmtree(p)

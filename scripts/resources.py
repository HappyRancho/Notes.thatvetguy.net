"""Canonical catalogue and rendering helpers shared by listing pages."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
RECORDS=json.loads((ROOT/'data/catalogue.json').read_text())
CATALOGUE={item['id']:item for item in RECORDS}

def unique(ids):
    return list(dict.fromkeys(ids))

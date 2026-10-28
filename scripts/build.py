#!/usr/bin/env python3
from pathlib import Path
import runpy
# Regenerate checklists from the retained, hash-identified university source.
# No network request is made during ordinary builds.
if __name__=='__main__':
    if (Path(__file__).resolve().parent.parent/'data/msve-2016-source.json').exists():
        runpy.run_path(str(Path(__file__).with_name('extract-msve-syllabi.py')),run_name='__main__')
    from build_site import run
    run()

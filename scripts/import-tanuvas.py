#!/usr/bin/env python3
"""Refresh TANUVAS from the owner-organized public Drive, preserving source names."""
from pathlib import Path
import runpy
if __name__=='__main__':
    scripts=Path(__file__).resolve().parent
    runpy.run_path(str(scripts/'inspect-tanuvas-drive.py'),run_name='__main__')
    runpy.run_path(str(scripts/'tanuvas_drive.py'),run_name='__main__')

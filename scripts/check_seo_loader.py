"""Import the existing SEO parser without duplicating its implementation."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('site_seo_check',Path(__file__).with_name('check-seo.py'))
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
Document=module.Document

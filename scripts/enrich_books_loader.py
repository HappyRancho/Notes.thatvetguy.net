"""Import the hyphenated source-review script for a shared image validator."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('book_image_review',Path(__file__).with_name('enrich-books.py'))
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
save_cover=module.save_cover

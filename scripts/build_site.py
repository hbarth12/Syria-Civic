"""Rebuild English pages, then Arabic counterparts and language navigation."""
from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parent
for script in ['import_nsls.py','build_records.py','build_about.py','build_futures.py','build_sada.py','build_donate.py','build_arabic.py','build_seo.py']:
 subprocess.run([sys.executable,str(root/script)],check=True)

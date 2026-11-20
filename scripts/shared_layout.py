from pathlib import Path
import re

def footer(prefix=""):
    home=(Path(__file__).resolve().parents[1]/"dist/index.html").read_text()
    markup=re.search(r'<footer class="site-footer">.*?</footer>',home,re.S).group()
    def link(m):
        target=m[1]
        if target.startswith("#"):target="index.html"+target
        if not re.match(r"[a-z]+:",target):target=prefix+target
        return 'href="'+target+'"'
    return re.sub(r'href="([^"]+)"',link,markup)

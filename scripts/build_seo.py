"""Refresh search metadata. Absolute URLs require content/site-url.txt."""
from pathlib import Path
from html import escape,unescape
from urllib.parse import quote,urlparse
import re,json,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'dist'
config=ROOT/'content/site-url.txt'
base=config.read_text().strip().rstrip('/') if config.exists() else ''
if base:assert urlparse(base).scheme=='https' and urlparse(base).netloc, 'Use the public HTTPS site address'
def text(s):return re.sub(r'\s+',' ',unescape(re.sub('<[^>]+>',' ',s))).strip()
def url(path):
 rel=path.relative_to(OUT).as_posix()
 if rel.endswith('index.html'):rel=rel[:-10]
 return base+'/'+quote(rel,safe='/')
pages=[]
for p in OUT.rglob('*.html'):
 rel=p.relative_to(OUT)
 if any(x in rel.parts for x in ['record-drafts','dreamland']) or p.name=='article-preview.html':continue
 s=p.read_text()
 if re.search(r'<meta[^>]+noindex',s):continue
 pages.append(p)
for p in pages:
 s=p.read_text();title=text(re.search(r'<title>(.*?)</title>',s,re.S)[1])
 desc=re.search(r'<meta name="description" content="([^"]*)"',s)
 if desc:desc=unescape(desc[1])
 else:
  main=s.split('<main',1)[-1];paragraphs=re.findall(r'<p\b[^>]*>(.*?)</p>',main,re.S)
  desc=next((text(x) for x in paragraphs if len(text(x))>90),title)
  if len(desc)>180:desc=desc[:177].rsplit(' ',1)[0]+'…'
 s=re.sub(r'<meta (?:name|property)="(?:description|og:[^"]*|twitter:[^"]*)"[^>]*>','',s)
 s=re.sub(r'<!-- SEO START -->.*?<!-- SEO END -->','',s,flags=re.S)
 tags=[f'<meta name="description" content="{escape(desc,quote=True)}">',f'<meta property="og:title" content="{escape(title,quote=True)}">',f'<meta property="og:description" content="{escape(desc,quote=True)}">','<meta property="og:site_name" content="Syria Civic">','<meta property="og:type" content="website">','<meta name="twitter:card" content="summary">',f'<meta name="twitter:title" content="{escape(title,quote=True)}">',f'<meta name="twitter:description" content="{escape(desc,quote=True)}">']
 if base:
  tags += [f'<link rel="canonical" href="{url(p)}">',f'<meta property="og:url" content="{url(p)}">',f'<meta property="og:image" content="{base}/assets/favicon.png">','<meta property="og:image:alt" content="Syria Civic">']
  rel=p.relative_to(OUT);ar=rel.parts[0]=='ar';en=OUT/Path(*rel.parts[1:]) if ar else p;arabic=OUT/'ar'/en.relative_to(OUT)
  if en in pages and arabic in pages:
   tags += [f'<link rel="alternate" hreflang="{lang}" href="{url(f)}">' for lang,f in [('en',en),('ar',arabic),('x-default',en)]]
  if p in [OUT/'index.html',OUT/'ar/index.html']:
   data={'@context':'https://schema.org','@type':'Organization','name':'Syria Civic','url':base+'/','logo':base+'/assets/favicon.png','email':'info@syriacivic.com','description':'Independent research, public debate, and civic participation in Syria.'}
   tags += ['<script type="application/ld+json">'+json.dumps(data)+'</script>']
 s=s.replace('</head>','<!-- SEO START -->\n'+'\n'.join(tags)+'\n<!-- SEO END -->\n</head>');p.write_text(s)
if base:
 ns='http://www.sitemaps.org/schemas/sitemap/0.9';ET.register_namespace('',ns);tree=ET.Element('{'+ns+'}urlset')
 for p in sorted(pages):ET.SubElement(ET.SubElement(tree,'{'+ns+'}url'),'{'+ns+'}loc').text=url(p)
 ET.ElementTree(tree).write(OUT/'sitemap.xml',encoding='utf-8',xml_declaration=True)
 (OUT/'robots.txt').write_text('User-agent: *\nAllow: /\n\nSitemap: '+base+'/sitemap.xml\n')
print(f'Metadata updated on {len(pages)} pages. '+('Sitemap, canonical URLs and bilingual alternates generated.' if base else 'Public URL required for sitemap and canonical URLs.'))

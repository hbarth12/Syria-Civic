from shared_layout import footer as shared_footer
"""Import the supplied NSLS snapshot without changing its publication metadata."""
import json, re, zipfile, hashlib
from pathlib import Path
from html import escape
from html.parser import HTMLParser
from urllib.parse import quote
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
ZIP = Path('/Users/haddonbarth/Downloads/NSLS-Website-Final-main (1).zip')
PREFIX = 'NSLS-Website-Final-main/ISLS/'
z = zipfile.ZipFile(ZIP)
raw = z.read(PREFIX + 'content/publications-bilingual.json')
records = sorted(json.loads(raw)['publications'], key=lambda r:r['date'], reverse=True)
issues, copied = [], {}
def e(v): return escape(str(v or ''), quote=True)
def asset(path):
    if not path or path.startswith('http'): return path
    dest = 'assets/nsls/' + path.removeprefix('assets/')
    data = z.read(PREFIX + path)
    target = OUT / dest
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    copied[dest] = hashlib.sha256(data).hexdigest()
    return quote(dest, safe='/')
def url(r, lang='en'):
    return ('ar/' if lang == 'ar' else '') + 'publications/' + quote(r['slug'], safe='') + '/index.html'
def publisher(r): return 'Syria Civic' if r['source']=='NSLS' else r['source']
def headline(title):
    return e(title)
def date(r):
    return datetime.strptime(r['date'], '%Y-%m-%d' if len(r['date'])==10 else '%Y-%m').strftime('%d %B %Y' if len(r['date'])==10 else '%B %Y').lstrip('0')
class Body(HTMLParser):
    def __init__(self, cls): super().__init__(convert_charrefs=False); self.cls=cls; self.depth=0; self.parts=[]
    def handle_starttag(self, tag, attrs):
        if self.depth:
            self.parts.append(self.get_starttag_text())
            if tag not in ('img','br','hr','input','meta','link','source','wbr'): self.depth+=1
        elif self.cls in dict(attrs).get('class','').split(): self.depth=1
    def handle_endtag(self, tag):
        if self.depth:
            self.depth-=1
            if self.depth: self.parts.append('</'+tag+'>')
    def handle_data(self,s):
        if self.depth:self.parts.append(s)
    def handle_entityref(self,s): self.handle_data('&'+s+';')
    def handle_charref(self,s): self.handle_data('&#'+s+';')
def rendered(r,lang):
    path=PREFIX+('ar/' if lang=='ar' else '')+'publications/'+r['slug']+'/index.html'
    text=z.read(path).decode('utf-8')
    for cls in ('publication-detail-body','policy-paper-summary'):
        parser=Body(cls);parser.feed(text)
        if parser.parts: return ''.join(parser.parts)
    raise ValueError('No rendered body: '+path)
def shell(title, body, prefix='', lang='en'):
    home = (OUT/'index.html').read_text()
    header = home[home.index('  <div id="top">'):home.index('  <main id="main">')]
    header = header.replace('<h1 class="masthead-title">', '<div class="masthead-title">').replace('</h1>', '</div>')
    header = re.sub(r'href="#([^"]*)"', lambda m: 'href="'+prefix+'index.html#'+m.group(1)+'"', header)
    header = header.replace('href="publications.html"', 'href="'+prefix+'publications.html"')
    header = header.replace('href="about.html"', 'href="'+prefix+'about.html"')
    header = header.replace('href="parliamentary-record.html"', 'href="'+prefix+'parliamentary-record.html"')
    header = header.replace('href="civic-futures.html"', 'href="'+prefix+'civic-futures.html"')
    header = header.replace('href="sada-house.html"', 'href="'+prefix+'sada-house.html"')
    header = header.replace('href="donate.html"', 'href="'+prefix+'donate.html"')
    return f'''<!doctype html><html lang="{lang}" dir="{'rtl' if lang=='ar' else 'ltr'}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)} — Syria Civic</title><link href="https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;500;600;900&amp;family=Source+Serif+4:opsz,wght@8..60,400;600&amp;display=swap" rel="stylesheet"><link rel="stylesheet" href="{prefix}styles.css"><link rel="stylesheet" href="{prefix}editorial.css"><link rel="icon" type="image/png" href="{prefix}assets/favicon.png"></head><body>{header}{body}{shared_footer(prefix)}<script src="{prefix}script.js"></script></body></html>'''

for r in records:
    r['_image']=asset(r.get('image',''))
    for lang in ('en','ar'):
        if not r[lang].get('title'):
            issues.append(r['slug']+': Arabic article content not supplied; English version only.')
            continue
        t=dict(r[lang]); t.setdefault('label', r['type']); prefix='../../../' if lang=='ar' else '../../'
        pdf=t.get('pdf')
        if not pdf and r['publicationFormat']=='pdf':
            pdf=r['en'].get('pdf');issues.append(r['slug']+': no Arabic PDF supplied; Arabic page links to English PDF.')
        pdf=asset(pdf) if pdf else None
        if not t.get('author'): issues.append(r['slug']+': '+lang+' author not supplied; source attribution retained.')
        image=r['_image']; image= image if image.startswith('http') else prefix+image
        # Remote image proxies are retained in source data, not loaded as unreliable covers.
        photo='' if 'api.microlink.io' in image else f'<figure class="article-image"><img src="{e(image)}" alt="{e(t.get("imageAlt",""))}"></figure>'
        action=''
        if pdf: action=f'<p class="publication-action"><a href="{prefix}{pdf}">{"Read the full paper (PDF)" if lang=="en" else "قراءة البحث (PDF)"} →</a></p>'
        if r['publicationFormat']=='external': action=f'<p class="publication-action"><a href="{e(r["url"])}">Read the full article at {e(r["source"])} ↗</a></p>'
        note='Published by Syria Civic.' if r['source']=='NSLS' else 'Originally published by '+r['source']+'. Read the full article at the publisher’s website.'
        counterpart='en' if lang=='ar' or not r['ar'].get('title') else 'ar'
        body=f'''<main><header class="article-heading"><p class="eyebrow">{e(t['label'])}</p><h1>{headline(t['title'])}</h1><p class="dek">{e(t.get('description',''))}</p><div class="byline"><strong class="article-author">{e(t.get('author') or publisher(r))}</strong><small><time datetime="{r['date']}">{date(r)}</time> · {e(t.get('readTime',''))}</small></div><p><a href="{prefix}{url(r,counterpart)}" lang="{counterpart}">{'English' if counterpart=='en' else 'العربية'}</a></p></header>{photo}<div class="reading-column">{action}<div class="article-body">{rendered(r,lang)}</div><div class="author-note">{e(note)}<p><a href="{prefix}publications.html">All publications →</a></p></div></div></main>'''
        target=OUT/('ar/' if lang=='ar' else '')/'publications'/r['slug']/'index.html';target.parent.mkdir(parents=True,exist_ok=True);target.write_text(shell(t['title'],body,prefix,lang))

cards=[]
for r in records:
    t=r['en'];im=r['_image']; image='' if 'api.microlink.io' in im else f'<a href="{url(r)}" tabindex="-1" aria-hidden="true"><img loading="lazy" src="{e(im)}" alt=""></a>'
    cards.append(f'''<article class="archive-card" data-kind="{e(t['label'])}" data-search="{e((t['title']+' '+t.get('author','')+' '+t.get('description','')).lower())}">{image}<p class="eyebrow">{e(t['label'])}</p><h2><a href="{url(r)}">{e(t['title'])}</a></h2><p>{e(t.get('description',''))}</p><p class="archive-meta">{e(t.get('author') or publisher(r))} · {date(r)}</p></article>''')
filters=''.join(f'<option>{e(x)}</option>' for x in sorted({r['en']['label'] for r in records}))
lead=records[0]; lt=lead['en']
body=f'''<main class="archive ideas-initiative"><header class="initiative-intro"><p class="eyebrow">Syria Civic</p><h1>Our Ideas Initiative</h1><!-- Initiative messaging to be supplied by Syria Civic. --><p class="initiative-deck">New perspectives on Syria’s public life.</p><a class="initiative-jump" href="#explore-ideas">Explore the ideas ↓</a></header><section class="initiative-feature" aria-labelledby="featured-idea"><a class="initiative-photo" href="{url(lead)}" aria-label="{e(lt['title'])}"><img src="{e(lead['_image'])}" alt="{e(lt.get('imageAlt',''))}"></a><div class="initiative-feature-copy"><p class="eyebrow">In focus · {e(lt['label'])}</p><h2 id="featured-idea"><a href="{url(lead)}">{e(lt['title'])}</a></h2><p class="archive-meta">{e(lt.get('author') or publisher(lead))}<br>{date(lead)}</p><a class="initiative-jump" href="{url(lead)}">Read the piece →</a></div></section><section id="explore-ideas" aria-labelledby="explore-title"><div class="initiative-section-heading"><h2 id="explore-title">Ideas to explore</h2><p>Essays, research, and policy proposals</p></div><details class="initiative-search"><summary>Find a piece</summary><div class="archive-controls"><label>Search publications<input id="search" type="search" placeholder="Title, author, or topic"></label><label>Publication type<select id="kind"><option value="">All publications</option>{filters}</select></label></div><p id="results" role="status">11 publications</p></details><div class="archive-grid">{''.join(cards)}</div><p id="empty" hidden>No publications match your search.</p></section></main><script src="archive.js"></script>'''
(OUT/'publications.html').write_text(shell('Our Ideas Initiative',body))
(OUT/'content').mkdir(exist_ok=True);(OUT/'content/nsls-publications.json').write_bytes(raw)

def homecard(r,lead=False):
    t=r['en']
    return f'''<article class="{'news-lead' if lead else 'news-card'}"><a class="news-image" href="{url(r)}" aria-label="{e(t['title'])}"><img src="{e(r['_image'])}" alt="{e(t.get('imageAlt',''))}"></a><p class="story-category">{e(t['label'])}</p><h3><a href="{url(r)}">{e(t['title'].split(':')[0] if not lead else 'Can the People’s Assembly Hold the Government Accountable?')}</a></h3><p class="story-meta">{('<span>'+e(t.get('author',''))+'</span>') if lead else ''}<time datetime="{r['date']}">{date(r)}</time></p></article>'''
home=(OUT/'index.html').read_text()
start=home.index('<div class="news-frontpage">');end=home.index('    </section>',start)
home=home[:start]+'<div class="news-frontpage">'+homecard(records[0],True)+'<div class="news-side news-left">'+homecard(records[1])+homecard(records[4])+'</div><div class="news-side news-right">'+homecard(records[2])+homecard(records[3])+'</div></div>\n'+home[end:]
home=home.replace('href="#latest">Publications','href="publications.html">Publications').replace('class="ideas-explore" href="#latest"','class="ideas-explore" href="publications.html"')
(OUT/'index.html').write_text(home)
issues.append('Source dates preserved as supplied. wheat-fields-reconstruction is dated 2026-05-21, but its publisher URL contains 2026/07; confirm before launch.')
issues.append('Two publisher image-proxy URLs omitted from archive cards; original URLs remain in source JSON. One Wikimedia image remains externally hosted.')
(ROOT/'MIGRATION.md').write_text('# NSLS publication migration\n\n11 publications; 21 English/Arabic pages. Original source JSON retained in dist/content/nsls-publications.json. Local image/PDF bytes copied unchanged. Original slugs retained, including source spelling.\n\n## Items to confirm\n\n'+'\n'.join('- '+x for x in dict.fromkeys(issues))+'\n\nNo hosting redirects have been configured.\n')
(ROOT/'migration-assets.json').write_text(json.dumps(copied,indent=2,ensure_ascii=False))
print(f'Imported {len(records)} publications / 21 pages / {len(copied)} local assets.')

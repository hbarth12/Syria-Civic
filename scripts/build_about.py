"""Build About Us using the site's shared masthead and footer."""
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1] / 'dist'
home = (root / 'index.html').read_text()
header = home[home.index('  <div id="top">'):home.index('  <main id="main">')]
header = header.replace('<h1 class="masthead-title">', '<div class="masthead-title">').replace('</h1>', '</div>')
footer = home[home.index('  <footer class="site-footer">'):home.index('    <script src=')]
def links(markup):
    return re.sub(r'href="#([^"]*)"', lambda m: 'href="index.html#'+m.group(1)+'"', markup)
header, footer = links(header), links(footer)
body = '''<main id="main" class="about-page charter-page"><div class="charter-shell">
<header class="charter-intro"><h1>About us</h1></header>
<section class="charter-text" aria-labelledby="purpose-title"><h2 id="purpose-title" class="sr-only">Our story</h2><p>Our work began in 2026 with the Network for Syrian Legislative Studies (NSLS), a volunteer initiative bringing together students and researchers from universities in Syria and abroad to support Syria’s new People’s Assembly. We began publishing policy proposals, engaging with lawmakers, and making parliamentary proceedings more accessible to the public.</p><p>As we build relationships in Damascus, new projects began to take shape. We joined with Syria Direct to establish Sada House, a cultural space in central Damascus. And we began forming chapters at US universities and launched policy clinics for university students in Syria so that more young Syrians could participate in policymaking.</p><p>These efforts grew organically, enabled by volunteers’ time and donated space. Our small network of volunteers became a broader initiative to open new avenues for political participation and public debate.</p><p><strong class="charter-emphasis">Syria Civic brings these activities together under one organization.</strong> Our Ideas Initiative develops policy proposals and works with legislators; Civic Futures supports young Syrians through university networks, fellowships, and civic initiatives; and Sada House brings people together across professions and generations for discussion and exchange.</p><p>We&#x27;re building the institutions, networks, and spaces that can help more Syrians take part in shaping their country&#x27;s future.</p></section>
<figure class="charter-photo"><img src="assets/sada-listeners.jpg" alt="Participants listening during a discussion at Sada House." loading="lazy"><figcaption>A discussion at Sada House, Damascus.</figcaption></figure>
<section class="people-section" aria-labelledby="team-title"><h2 id="team-title">Our team</h2><div class="people-grid">TEAM_ENTRIES</div></section>
<section class="people-section" aria-labelledby="board-title"><h2 id="board-title">Board</h2><ul class="board-list"><li>Malik Al Abdeh</li><li>Ayman Abdelnour</li><li>Zaid Al-Ali</li><li>Ambassador Cameron Hume</li><li>Max Weiss</li></ul></section>
<section class="people-section" aria-labelledby="advisory-title"><h2 id="advisory-title">Advisory Board</h2><ul class="board-list"><li>Sameer Saboungi</li><li>Samir al Abdallah</li><li>John Balouziyeh</li></ul></section>
<section class="charter-contact"><h2>Get in touch</h2><p>Help organize an event at Sada House, write for us, join our university network, or pitch a project of your own.</p><a href="mailto:info@syriacivic.com">info@syriacivic.com ↗</a></section>
</div></main>'''
import zipfile, json
from html import escape
with zipfile.ZipFile('/Users/haddonbarth/Downloads/NSLS-Website-Final-main (1).zip') as source:
    team = json.loads(source.read('NSLS-Website-Final-main/ISLS/content/team-bilingual.json'))['team']
entries=[]
for person in team:
    if person['section'] != 'staff': continue
    t=person['en']
    entries.append('<article><h3>'+escape(t['name'])+'</h3><p>'+escape(t['rosterRole'])+'</p></article>')
body=body.replace('TEAM_ENTRIES',''.join(entries))
page = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>About Us — Syria Civic</title><meta name="description" content="Syria Civic develops policy ideas, creates spaces for public debate, and helps people organize projects of their own."><link href="https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;500;600;900&amp;family=Source+Serif+4:opsz,wght@8..60,400;600&amp;display=swap" rel="stylesheet"><link rel="stylesheet" href="styles.css"><link rel="stylesheet" href="about.css"><link rel="icon" type="image/png" href="assets/favicon.png"></head><body><a class="skip-link" href="#main">Skip to content</a>'''
(root/'about.html').write_text(page+header+body+footer+'<script src="script.js"></script></body></html>')

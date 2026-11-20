from pathlib import Path
import re
from shared_layout import footer

root=Path(__file__).resolve().parents[1]/'dist'
home=(root/'index.html').read_text()
header=home[home.index('  <div id="top">'):home.index('  <main id="main">')].replace('<h1 class="masthead-title">','<div class="masthead-title">').replace('</h1>','</div>')
header=re.sub(r'href="#([^"]*)"',lambda m:'href="index.html#'+m[1]+'"',header)
font=re.search(r'https://fonts.googleapis.com/css2\?[^\"]+',home).group()
body='''<main id="main" class="donate-page"><p class="donate-label">Support Syria Civic</p><h1>Help make more possible.</h1><p class="donate-intro">Your support can help bring new ideas and initiatives to life in Syria.</p><p>We’re putting our donation arrangements in place. In the meantime, if you’d like to support our work, we’d love to hear from you.</p><a class="donate-contact" href="mailto:info@syriacivic.com?subject=Supporting%20Syria%20Civic">info@syriacivic.com <span aria-hidden="true">↗</span></a><p class="donate-note">Write to us to discuss making a contribution.</p></main>'''
head=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Donate — Syria Civic</title><meta name="description" content="Interested in supporting Syria Civic? Contact info@syriacivic.com to discuss making a contribution."><link href="{font}" rel="stylesheet"><link rel="stylesheet" href="styles.css"><link rel="stylesheet" href="donate.css"><link rel="icon" type="image/png" href="assets/favicon.png"></head><body><a class="skip-link" href="#main">Skip to content</a>'''
(root/'donate.html').write_text(head+header+body+footer()+'<script src="script.js"></script></body></html>')

from shared_layout import footer as shared_footer
"""Render published records and a separate local draft review queue."""
from pathlib import Path
from html import escape as e
from urllib.parse import quote
import json, re

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dist'
home=(OUT/'index.html').read_text()
header=home[home.index('  <div id="top">'):home.index('  <main id="main">')].replace('<h1 class="masthead-title">','<div class="masthead-title">').replace('</h1>','</div>')
def shell(title,body,prefix='',draft=False):
    h=re.sub(r'href="#([^"]*)"',lambda m:'href="'+prefix+'index.html#'+m[1]+'"',header)
    for name in ('about.html','publications.html','parliamentary-record.html','civic-futures.html','sada-house.html','donate.html'):
        h=h.replace('href="'+name+'"','href="'+prefix+name+'"')
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">{'<meta name="robots" content="noindex,nofollow">' if draft else ''}<title>{e(title)} — Syria Civic</title><link href="https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;500;600;900&amp;family=Source+Serif+4:opsz,wght@8..60,400;600&amp;display=swap" rel="stylesheet"><link rel="stylesheet" href="{prefix}styles.css"><link rel="stylesheet" href="{prefix}editorial.css"><link rel="stylesheet" href="{prefix}records.css"><link rel="icon" type="image/png" href="{prefix}assets/favicon.png"></head><body>{h}<main class="records-shell">{body}</main>{shared_footer(prefix)}<script src="{prefix}script.js"></script></body></html>'''

def render(r,draft=False):
    slug=r['slug'];assert re.fullmatch(r'[a-z0-9-]+',slug)
    folder=('record-drafts/' if draft else 'parliamentary-record/')+slug
    target=OUT/folder;target.mkdir(parents=True,exist_ok=True)
    sections=[]
    for lang in ('en','ar'):
        t=r.get(lang,{})
        if not t.get('transcript'):continue
        paragraphs=[]
        for i,chunk in enumerate(t['transcript'].split('\n\n')):
            text=e(chunk).replace('\n','<br>')
            # Link every timestamp to its position in the original recording.
            def stamp(m):
                seconds=int(m[1])*3600+int(m[2])*60+int(m[3])
                return '<a class="timecode" href="'+e(r['sourceVideoUrl'])+'&amp;t='+str(seconds)+'s">'+m[0]+'</a>'
            text=re.sub(r'\[(\d{2}):(\d{2}):(\d{2})\]',stamp,text)
            paragraphs.append(f'<p id="{lang}-{i}">{text}</p>')
        sections.append(f'<section class="record-language" id="{lang}" lang="{lang}" dir="{"rtl" if lang=="ar" else "ltr"}"><h2>{"English transcript" if lang=="en" else "النص العربي"}</h2>'+''.join(paragraphs)+'</section>')
    t=r['en'];pdf=t.get('pdf');pdf_link=''
    if pdf:
        name=Path(pdf).name
        if (OUT/'assets'/name).exists():pdf_link=f'<a href="../../assets/{quote(name)}">Download PDF ↓</a>'
    languages=' · '.join(f'<a href="#{l}">{"English" if l=="en" else "العربية"}</a>' for l in ('en','ar') if r.get(l,{}).get('transcript'))
    body=f'''<a href="../../{'record-drafts/index.html' if draft else 'parliamentary-record.html'}">← {'Draft review queue' if draft else 'Parliamentary Record'}</a><header class="record-heading"><p class="eyebrow">{'Draft · awaiting review' if draft else 'Parliamentary Record'} · {e(t.get('typeLabel','Hearing'))}</p><h1>{e(t['title'])}</h1><p class="record-date">{e(r['date'])} · {e(r.get('sessionNumber',''))}</p><p class="record-summary">{e(t.get('summary',''))}</p><nav class="record-actions" aria-label="Record resources">{languages}<a href="{e(r['sourceVideoUrl'])}">Watch source recording ↗</a>{pdf_link}</nav></header><aside class="record-note"><strong>About this transcript</strong><p>{e(t.get('accuracyNote','Draft transcript awaiting editorial review.'))}</p><p>{e(t.get('sourceCredit',''))}</p>{'<p>Arabic transcript not yet available.</p>' if not r.get('ar',{}).get('transcript') else ''}</aside>{''.join(sections)}'''
    (target/'index.html').write_text(shell(t['title'],body,'../../',draft))
    return f'<article class="record-entry"><p class="eyebrow">{e(r["date"])} · {e(t.get("typeLabel","Hearing"))}</p><h2><a href="{slug if draft else "parliamentary-record/"+slug}/index.html">{e(t["title"])}</a></h2><p>{e(t.get("summary",""))}</p><span>{"English · العربية" if r.get("ar",{}).get("transcript") else "English transcript · PDF · Source video"}</span></article>'

entries=[]
for f in sorted((OUT/'content/parliamentary-record').glob('*.json'),reverse=True):
    r=json.loads(f.read_text())
    if not r.get('placeholder') and r.get('status')!='draft':entries.append(render(r))
intro='''<header class="record-heading"><p class="eyebrow">Parliament &amp; Policy</p><h1>The Parliamentary Record</h1><p class="record-deck">Read what happens in Parliament.</p><p class="record-summary">We collect and publish parliamentary transcripts so they remain accessible to everyone. Read the debates, follow the questions, and return to the original recordings.</p></header><div class="record-index-heading"><h2>Sessions &amp; hearings</h2><p>Transcripts and source recordings</p></div>'''
(OUT/'parliamentary-record.html').write_text(shell('The Parliamentary Record',intro+''.join(entries)+'<p class="record-note">This collection is growing. Available languages and source material are listed with each record. <a href="mailto:info@syriacivic.com">Send a recording or correction →</a></p>'))
drafts=ROOT/'record-workflow/drafts';drafts.mkdir(parents=True,exist_ok=True)
queue=[]
for f in sorted(drafts.glob('*.json')):
    r=json.loads(f.read_text());queue.append(render(r,True))
(OUT/'record-drafts').mkdir(exist_ok=True)
(OUT/'record-drafts/index.html').write_text(shell('Transcript drafts','<header class="record-heading"><p class="eyebrow">Local editorial review</p><h1>Transcript drafts</h1><p>Unpublished work prepared for review.</p></header>'+(''.join(queue) or '<p>No new transcript drafts yet.</p>'),'../',True))
print(f'Rendered {len(entries)} published records and {len(queue)} drafts.')

from pathlib import Path
from html.parser import HTMLParser
from html import escape
from urllib.parse import urlsplit,unquote
import json,re,os
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'dist'
M=dict(line.split('|',1) for line in (ROOT/'content/ar-ui.txt').read_text().splitlines() if '|' in line)
records=json.loads((OUT/'content/nsls-publications.json').read_text())['publications']
for r in records:
 for key in ['title','description','author','label','imageAlt']:
  if r['en'].get(key) and r['ar'].get(key):M[r['en'][key]]=r['ar'][key]
# Titles without a supplied Arabic article still receive an Arabic listing label.
M.update({'Can the People’s Assembly Hold the Government Accountable? Lessons from Syria’s First Ministerial Hearings':'هل يستطيع مجلس الشعب مساءلة الحكومة؟ دروس من أولى جلسات الاستماع الوزارية في سوريا','Can the People’s Assembly Hold the Government Accountable?':'هل يستطيع مجلس الشعب مساءلة الحكومة؟','Relative Power Within Syrian Legislature':'موازين القوى داخل السلطة التشريعية السورية','Nadia Asaad and Lojean Hersi':'نادية أسعد ولوجين هرسي','Sanjana Kumar':'سانجانا كومار','Vincent Sanfedele':'فينسنت سانفيديلي','Alexander C. Grenier':'ألكسندر سي. غرينييه','Al-Monitor':'المونيتور','Middle East Institute':'معهد الشرق الأوسط','Syria Civic — Imagining New Political Possibilities':'سوريا سيفيك — آفاق جديدة للحياة العامة','Title, author, or topic':'العنوان أو الكاتب أو الموضوع','An idea, a question, or how you’d like to take part.':'فكرة أو سؤال أو طريقة تود المساهمة بها.'})
months={'August':'أغسطس','October':'أكتوبر','May':'مايو','July':'يوليو','September':'سبتمبر','November':'نوفمبر'}
unknown=set()
def tr(s):
 t=s.strip()
 if not t:return s
 value=M.get(t)
 if value is None:
  value=t
  for en,ar in sorted(M.items(),key=lambda a:-len(a[0])):
   if en in value:value=value.replace(en,ar)
  for en,ar in months.items():value=value.replace(en,ar)
  if re.search('[A-Za-z]{3}',value) and not any(x in value for x in ['@','sadahouse.com','Wikimedia','NSLS','PDF']):unknown.add(value)
 return s[:len(s)-len(s.lstrip())]+value+s[len(s.rstrip()):]
main=['index.html','about.html','sada-house.html','civic-futures.html','donate.html','publications.html','parliamentary-record.html']
class Arabic(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.parts=[];self.skip=0
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if tag in ['script','style']:self.skip+=1
  for k in ['alt','aria-label','placeholder','title','content']:
   if k in d and (k!='content' or d.get('name')=='description'):d[k]=tr(d[k])
  if tag=='html':d.update(lang='ar',dir='rtl')
  if tag=='option':d.setdefault('value', '') # populated options below retain source filter keys
  if 'href' in d:
   u=d['href']; path=unquote(urlsplit(u).path)
   if not urlsplit(u).scheme and not u.startswith('#'):
    if path in main:pass
    elif path.startswith('publications/') and (OUT/'ar'/path).exists():pass
    else:d['href']='../'+u
  for k in ['src','action']:
   if k in d and not urlsplit(d[k]).scheme and not d[k].startswith('#'):d[k]='../'+d[k]
  if tag=='link' and d.get('rel')=='stylesheet' and d.get('href','').startswith('https://fonts.googleapis.com'):
   d['href']+='&family=Noto+Sans+Arabic:wght@400;500;600;700'
  if tag=='input' and d.get('type')=='email':d['dir']='ltr'
  self.parts.append('<'+tag+''.join(' '+k+('="'+escape(v,quote=True)+'"' if v is not None else '') for k,v in d.items())+'>')
 def handle_endtag(self,t):
  if t in ['script','style']:self.skip-=1
  if t=='head':self.parts.append('<link rel="stylesheet" href="../arabic.css">')
  self.parts.append('</'+t+'>')
 def handle_data(self,s):self.parts.append(s if self.skip else escape(tr(s)))
 def handle_decl(self,s):self.parts.append('<!'+s+'>')
 def handle_comment(self,s):pass
for name in main:
 source=(OUT/name).read_text()
 source=re.sub(r'<a class="language-switch".*?</a>','',source)
 parser=Arabic();parser.feed(source);result=''.join(parser.parts)
 # Keep filter values matched to the unmodified card metadata.
 for en in ['Commentary','Memo','Policy Paper']:
  result=result.replace('<option value="">'+M[en],'<option value="'+en+'">'+M[en])
 # Arabic search indexes match the actual translated titles.
 result=re.sub(r'data-search="([^"]*)"',lambda m:'data-search="'+escape(tr(m[1]),quote=True)+'"',result)
 # Mark English-only destinations explicitly.
 result=re.sub(r'(<a[^>]+href="\.\./(?:publications|parliamentary-record)/[^"]+"[^>]*>)([^<]+)(</a>)',lambda m:m[1]+m[2]+' <small>(بالإنجليزية)</small>'+m[3],result)
 (OUT/'ar'/name).write_text(result)
# Add corresponding-page language switches throughout, including existing Arabic articles.
for p in OUT.rglob('*.html'):
 s=p.read_text();s=re.sub(r'<a class="language-switch".*?</a>','',s)
 rel=p.relative_to(OUT);is_ar=rel.parts[0]=='ar'
 target=OUT/Path(*rel.parts[1:]) if is_ar else OUT/'ar'/rel
 if not target.exists():target=OUT/('publications.html' if is_ar else 'ar/publications.html')
 href=os.path.relpath(target,p.parent)
 label='English' if is_ar else 'العربية'
 switch=f'<a class="language-switch" href="{href}" lang="{"en" if is_ar else "ar"}" hreflang="{"en" if is_ar else "ar"}" aria-label="{"Read in English" if is_ar else "اقرأ بالعربية"}">{label}</a>'
 s=re.sub(r'(<nav id="primary-nav"[^>]*>)',lambda m:m[1]+'\n      '+switch,s,count=1)
 if is_ar and 'arabic.css' not in s:
  css=os.path.relpath(OUT/'arabic.css',p.parent);s=s.replace('</head>',f'<link rel="stylesheet" href="{css}"></head>')
 p.write_text(s)
(ROOT/'content/ar-review.txt').write_text('\n'.join(sorted(unknown)))
print('Built 7 Arabic pages, linked existing Arabic articles, and added language switches.')
# Translate shared chrome on the ten already-imported Arabic articles, without touching article text.
for p in (OUT/'ar/publications').glob('*/index.html'):
 s=p.read_text()
 def chrome(m):
  return re.sub(r'>([^<>]+)<',lambda n:'>'+escape(tr(n[1]))+'<',m[0])
 s=re.sub(r'<header class="site-header.*?</header>',chrome,s,flags=re.S)
 s=re.sub(r'<footer.*?</footer>',chrome,s,flags=re.S)
 s=s.replace('>Published by Syria Civic.<','>نشرته سوريا سيفيك.<').replace('>All publications →<','>جميع المنشورات ←<')
 if 'Noto+Sans+Arabic' not in s:s=s.replace('</head>','<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@400;500;600;700&amp;display=swap"></head>')
 p.write_text(s)

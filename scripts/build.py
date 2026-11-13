"""Build a dependency-free static site from the Pages CMS JSON articles."""
from pathlib import Path
from html import escape
from html.parser import HTMLParser
from datetime import date
from urllib.parse import urlsplit, quote
import json,re,shutil
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build'
SITE_URL='https://yamada-michie-office.github.io'

class CleanHTML(HTMLParser):
    allowed={'p','br','a','img','strong','b','em','i','u','s','h2','h3','h4','ul','ol','li','blockquote','pre','code','hr','div','span','figure','figcaption','table','thead','tbody','tr','td','th','sup','sub'}
    void={'br','img','hr'}
    blocked={'script','style','iframe','object','embed','form','input','button','textarea','svg','math'}
    def __init__(self):
        super().__init__(convert_charrefs=True); self.out=[];self.text=[];self.images=[];self.skip=0
    @staticmethod
    def safe_url(value,image=False):
        value=value.strip()
        if not value or re.search(r'[\x00-\x20\x7f]',value): return ''
        parsed=urlsplit(value)
        return value if parsed.scheme in ({'http','https'} if image else {'http','https','mailto','tel'}) or (not parsed.scheme and not parsed.netloc and value.startswith(('/','#'))) else ''
    def handle_starttag(self,tag,attrs):
        if tag in self.blocked:self.skip+=1;return
        if self.skip or tag not in self.allowed:return
        cleaned=[]
        for k,v in attrs:
            if v is None:continue
            if (tag,k) in {('a','href'),('img','src')}:
                v=self.safe_url(v,tag=='img')
                if not v:continue
                if tag=='img':self.images.append(v)
            elif k in {'alt','title'}:pass
            elif k in {'width','height','colspan','rowspan'} and v.isdigit():pass
            else:continue
            cleaned.append(f' {k}="{escape(v,quote=True)}"')
        if tag=='img':cleaned.append(' loading="lazy"')
        self.out.append('<'+tag+''.join(cleaned)+'>')
        if tag in {'p','br','div','li','h2','h3'}:self.text.append(' ')
    def handle_startendtag(self,tag,attrs):self.handle_starttag(tag,attrs)
    def handle_endtag(self,tag):
        if tag in self.blocked:
            self.skip=max(0,self.skip-1);return
        if not self.skip and tag in self.allowed and tag not in self.void:self.out.append('</'+tag+'>')
    def handle_data(self,data):
        if not self.skip:self.out.append(escape(data));self.text.append(data)

def build():
    if OUT.exists():shutil.rmtree(OUT)
    shutil.copytree(ROOT/'site',OUT)
    home=(OUT/'index.html').read_text()
    header=re.search(r'<header class="site-header">.*?</header>',home,re.S).group().replace('href="#','href="/#')
    posts=[]
    for path in sorted((ROOT/'content/posts').glob('*.json')):
        p=json.loads(path.read_text());slug=path.stem
        if not re.fullmatch(r'[A-Za-z0-9_-]+',slug):raise ValueError('Invalid article filename: '+path.name)
        if not isinstance(p.get('published'),bool):raise ValueError('Missing publication setting: '+path.name)
        if not p['published']:continue
        title=p.get('title','').strip();when=p.get('date','')
        if not title or not p.get('body','').strip():raise ValueError('Missing title/body: '+path.name)
        date.fromisoformat(when)
        clean=CleanHTML();clean.feed(p['body']);body=''.join(clean.out)
        image=CleanHTML.safe_url(p.get('image',''),True) or next(iter(clean.images),'')
        text=re.sub(r'\s+',' ',''.join(clean.text)).strip()
        url='/blog/'+quote(slug)+'/'
        page=f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)}｜山田みちえ</title><meta name="description" content="{escape(text[:120],quote=True)}"><link rel="canonical" href="{SITE_URL}{url}"><link rel="stylesheet" href="/style.css"><link rel="stylesheet" href="/blog.css"><link rel="icon" type="image/png" sizes="48x48" href="/site-icon.png"><link rel="apple-touch-icon" href="/apple-touch-icon.png"></head><body>{header}<main class="blog-main"><a class="textlink" href="/blog/">← 活動ブログ一覧</a><article class="blog-article"><p class="eyebrow">ACTIVITY BLOG</p><h1>{escape(title)}</h1><time datetime="{when}">{when.replace('-','.')}</time><div class="article-body">{body}</div></article></main><footer><a href="/">ホームに戻る</a><small>山田みちえ 活動ブログ</small></footer><script src="/navigation.js"></script></body></html>'''
        target=OUT/url.lstrip('/');target.mkdir(parents=True,exist_ok=True);(target/'index.html').write_text(page)
        posts.append({'id':slug,'title':title,'date':when,'year':when[:4],'url':url,'image':image,'text':text,'category':p.get('category','活動報告')})
    posts.sort(key=lambda p:(p['date'],p['id']),reverse=True)
    (OUT/'blog/posts.json').write_text(json.dumps(posts,ensure_ascii=False))
    blog=(OUT/'blog/index.html').read_text()
    years=''.join('<option>'+year+'</option>' for year in sorted({p['year'] for p in posts},reverse=True))
    blog=re.sub(r'(<select id="blog-year">).*?(</select>)',lambda m:m[1]+'<option value="">すべての年</option>'+years+m[2],blog,flags=re.S)
    (OUT/'blog/index.html').write_text(blog)
    if posts:
        p=posts[0]
        notice=f'<a class="notice" href="{p["url"]}"><span>お知らせ</span><time>{p["date"].replace("-",".")}</time><strong>{escape(p["title"])}</strong><b>↗</b></a>'
        home=re.sub(r'<a class="notice".*?</a>',lambda m:notice,home,flags=re.S)
        rows=''.join(f'<a class="journal-row" href="{p["url"]}"><time>{p["date"].replace("-",".")}</time><span class="tag">{escape(p["category"])}</span><div><h3>{escape(p["title"])}</h3><p>{escape(p["text"][:65])}…</p></div><b>↗</b></a>' for p in posts[:3])
        home=re.sub(r'(?:<a class="journal-row".*?</a>)+',lambda m:rows,home,flags=re.S)
    (OUT/'index.html').write_text(home)
    urls=['/','/blog/','/achievements/']+[p['url'] for p in posts]
    (OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{SITE_URL}{url}</loc></url>' for url in urls)+'</urlset>')
    (OUT/'sitemap.txt').write_text(''.join(f'{SITE_URL}{url}\n' for url in urls), encoding='utf-8')
    (OUT/'robots.txt').write_text(f'User-agent: *\nAllow: /\nDisallow: /editor/\nSitemap: {SITE_URL}/sitemap.xml\n')
    (OUT/'.nojekyll').touch()
    print(f'Built {len(posts)} published articles; output: {OUT}')
    return posts
if __name__=='__main__':build()

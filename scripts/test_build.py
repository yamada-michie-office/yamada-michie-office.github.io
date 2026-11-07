from pathlib import Path
from tempfile import TemporaryDirectory
import importlib.util,json,shutil
spec=importlib.util.spec_from_file_location('builder',Path(__file__).with_name('build.py'))
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
source_root=builder.ROOT
with TemporaryDirectory() as tmp:
 root=Path(tmp);shutil.copytree(source_root/'site',root/'site');(root/'content/posts').mkdir(parents=True)
 builder.ROOT=root;builder.OUT=root/'build'
 published={'title':'公開テスト <タグ>','date':'2027-01-02','published':True,'category':'お知らせ','image':'/assets/community.png','body':'<p>本文です。</p><img src="/assets/community.png" onerror="alert(1)"><script>alert(1)</script><a href="javascript:alert(1)">リンク</a>'}
 draft={**published,'title':'非公開テスト','date':'2027-01-03','published':False}
 (root/'content/posts/one.json').write_text(json.dumps(published));(root/'content/posts/two.json').write_text(json.dumps(draft))
 posts=builder.build();assert len(posts)==1
 assert not (root/'build/blog/two').exists()
 article=(root/'build/blog/one/index.html').read_text();assert '&lt;タグ&gt;' in article
 assert 'javascript:' not in article and 'onerror' not in article and 'alert(1)' not in article
 assert 'href="/blog/one/"' in (root/'build/index.html').read_text()
 assert '<option>2027</option>' in (root/'build/blog/index.html').read_text()
 published['published']=False;(root/'content/posts/one.json').write_text(json.dumps(published));builder.build()
 assert not (root/'build/blog/one').exists(),'Unpublishing must remove generated article'
 print('PASS: publish, draft exclusion, unpublish, escaping, unsafe HTML removal, homepage and year updates')

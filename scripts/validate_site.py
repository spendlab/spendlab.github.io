#!/usr/bin/env python3
"""Check published-document links, localized content, arithmetic and preserved policy assets."""
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import urlsplit, unquote
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASELINE = 'f1f33fbe38c1f4e64c05211f0ef86920568282bf'
registry = json.loads(subprocess.check_output(['node', '-e', 'process.stdout.write(JSON.stringify(require("./site-language.js").locales))'], cwd=ROOT))


class Document(HTMLParser):
    def __init__(self):
        super().__init__()
        self.references = []
        self.ids = []
        self.canonical = []
        self.alternates = []
        self.images = []
        self.links = []
        self.html_lang = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag == 'html':
            self.html_lang = attrs.get('lang')
        for attr in ['src', 'href']:
            if attrs.get(attr):
                self.references.append(attrs[attr])
        if tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonical.append(attrs['href'])
        if tag == 'link' and attrs.get('rel') == 'alternate':
            self.alternates.append((attrs.get('hreflang'), attrs['href']))
        if tag == 'img':
            self.images.append(attrs)
        if tag == 'a':
            self.links.append(attrs)


def check_reference(ref, current):
    url = urlsplit(ref)
    if url.scheme or url.netloc:
        return
    if not url.path:
        if url.fragment:
            assert unquote(url.fragment) in current.ids, ref
        return
    path = ROOT / url.path.lstrip('/')
    assert path.is_file() or (path / 'index.html').is_file(), ref


editable_baseline = {'index.html', 'README.md', 'docs/active_work_tracker.md'}
preserved = [name for name in subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', BASELINE], cwd=ROOT).decode().splitlines() if name not in editable_baseline]
hashes = {}
for relative in preserved:
    original = subprocess.check_output(['git', 'show', f'{BASELINE}:{relative}'], cwd=ROOT)
    current = (ROOT / relative).read_bytes()
    assert current == original, f'Protected source changed: {relative}'
    hashes[relative] = hashlib.sha256(current).hexdigest()

baseline_html = subprocess.check_output(['git', 'show', f'{BASELINE}:index.html'], cwd=ROOT).decode()
baseline_images = re.findall(r'<img src="(/images/[^"]+)"', baseline_html)
for locale, info in registry.items():
    source = ROOT / info['path'].strip('/') / 'index.html'
    html = source.read_text()
    doc = Document()
    doc.feed(html)
    assert doc.html_lang == info['lang'], locale
    assert doc.canonical == ['https://app.spendlab.net' + info['path']], locale
    assert len(doc.alternates) == 17, locale
    assert len(doc.ids) == len(set(doc.ids)), locale
    assert [item['src'] for item in doc.images if item['src'].startswith('/images/')] == baseline_images, locale
    assert html.count('<a href="/privacy/">Privacy</a>') == 2, locale
    assert sum(item['href'] == '/privacy/' for item in doc.links) == 2, locale
    assert sum(item['href'] == 'https://apps.apple.com/app/id1208128587' for item in doc.links) == 1, locale
    assert sum(item['href'] == 'https://play.google.com/store/apps/details?id=net.spendlab.spend' for item in doc.links) == 1, locale
    assert html.index('id="features"') < html.index('id="guides"') < html.index('id="roadmap-title"'), locale
    assert len(re.findall(r'class="feature"', html)) == 7, locale
    assert len(re.findall(r'class="guide"', html)) == 3, locale
    assert len(re.findall(r'class="faq-item"', html)) == 3, locale
    for reference in doc.references:
        check_reference(reference, doc)

policy = (ROOT / 'privacy/index.html').read_text()
assert 'site-language.js' not in policy and 'discovery.css' not in policy and 'hreflang' not in policy
neutral = (ROOT / 'index.html').read_bytes()
assert neutral == (ROOT / 'en/index.html').read_bytes()
sitemap = ET.parse(ROOT / 'sitemap.xml')
urls = [element.text for element in sitemap.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
assert set(urls) == {'https://app.spendlab.net' + info['path'] for info in registry.values()}
assert (ROOT / 'robots.txt').read_text() == 'Sitemap: https://app.spendlab.net/sitemap.xml\n'
print(json.dumps({'localizedPages': len(registry), 'guides': len(registry) * 3, 'protectedFiles': hashes, 'neutralEnglishFallback': True}, indent=2))

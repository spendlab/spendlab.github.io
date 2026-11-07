#!/usr/bin/env python3
"""Check static routes, approved localized artwork and preserved policy assets."""
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import struct
import subprocess
from urllib.parse import urlsplit, unquote
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASELINE = 'f1f33fbe38c1f4e64c05211f0ef86920568282bf'
registry = json.loads(subprocess.check_output(['node', '-e', 'process.stdout.write(JSON.stringify(require("./site-language.js").locales))'], cwd=ROOT))
gallery = json.loads((ROOT / 'content/gallery.json').read_text())
asset_versions = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()[:12] for name in ['site-language.js', 'discovery.css']}


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
assert gallery['canonicalManifest']['sha256'] == 'c82f83602e3fac077007e3384a494e82b4589b68c38a6a4ede40f3194c59fe37'
assert len(registry) == 15 and set(gallery['locales']) == set(registry)
assert 'en-GB' not in registry
image_count = image_bytes = 0
for locale, entry in gallery['locales'].items():
    assert [image['order'] for image in entry['images']] == list(range(1, 10)), locale
    assert [image['key'] for image in entry['images']] == ['overview', 'settlement', 'roles', 'meetup', 'receipt', 'fx', 'insights', 'quick', 'games'], locale
    for image in entry['images']:
        assert image['sourceID'] == f'{entry["sourceLocale"]}/apple-medium/{image["order"]:02d}', image['sourceID']
        assert urlsplit(image['src']).path == '/' + image['destination'], image['src']
        assert urlsplit(image['src']).query == 'v=' + image['sourceSHA256'][:12], image['src']
        data = (ROOT / image['destination']).read_bytes()
        assert len(data) == image['bytes'], image['destination']
        assert hashlib.sha256(data).hexdigest() == image['sourceSHA256'], image['destination']
        assert data[:8] == b'\x89PNG\r\n\x1a\n', image['destination']
        assert struct.unpack('>II', data[16:24]) == (image['width'], image['height']) == (1206, 2622), image['destination']
        image_count += 1
        image_bytes += len(data)
assert [image['src'] for image in gallery['locales']['en-US']['images']] == baseline_images
for locale, info in registry.items():
    source = ROOT / info['path'].strip('/') / 'index.html'
    html = source.read_text()
    doc = Document()
    doc.feed(html)
    assert doc.html_lang == info['lang'], locale
    assert doc.canonical == ['https://app.spendlab.net' + info['path']], locale
    expected_alternates = {(value['lang'], 'https://app.spendlab.net' + value['path']) for value in registry.values()} | {('x-default', 'https://app.spendlab.net/')}
    assert len(doc.alternates) == len(expected_alternates) and set(doc.alternates) == expected_alternates, locale
    assert len(doc.ids) == len(set(doc.ids)), locale
    assert [item['src'] for item in doc.images if item['src'].startswith('/images/')] == [image['src'] for image in gallery['locales'][locale]['images']], locale
    assert all(image.get('alt') for image in doc.images), locale
    assert {link.get('data-site-locale') for link in doc.links if link.get('data-site-locale')} == set(registry), locale
    assert '/en-gb/' not in html and 'screens-note' not in html, locale
    for name, version in asset_versions.items():
        assert f'/{name}?v={version}' in doc.references, locale
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
legacy_english = Document()
legacy_english.feed((ROOT / 'en-gb/index.html').read_text())
assert legacy_english.canonical == ['https://app.spendlab.net/en/']
assert legacy_english.alternates == []
assert any(link['href'] == '/en/' for link in legacy_english.links)
assert '/site-language.js?v=' + asset_versions['site-language.js'] in legacy_english.references
for reference in legacy_english.references:
    check_reference(reference, legacy_english)
sitemap = ET.parse(ROOT / 'sitemap.xml')
urls = [element.text for element in sitemap.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
assert set(urls) == {'https://app.spendlab.net' + info['path'] for info in registry.values()}
assert (ROOT / 'robots.txt').read_text() == 'Sitemap: https://app.spendlab.net/sitemap.xml\n'
print(json.dumps({'localizedPages': len(registry), 'guides': len(registry) * 3, 'approvedNativeImages': image_count, 'imageBytes': image_bytes, 'assetVersions': asset_versions, 'legacyEnglishAlias': True, 'protectedFiles': hashes, 'neutralEnglishFallback': True}, indent=2))

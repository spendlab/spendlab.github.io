#!/usr/bin/env python3
"""Import byte-exact approved gallery artwork from the separate SPEND checkout."""
from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import shutil
import struct

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = 'docs/store_listing/2026.10.17/english-fx-fit30/manifest.json'
MANIFEST_SHA256 = 'c82f83602e3fac077007e3384a494e82b4589b68c38a6a4ede40f3194c59fe37'
LOCALES = {
    'en-US': ('en-US', 'en'), 'ko-KR': ('ko', 'ko'), 'ja-JP': ('ja', 'ja'),
    'zh-CN': ('zh-Hans', 'zh-hans'), 'zh-TW': ('zh-Hant', 'zh-hant'),
    'de-DE': ('de-DE', 'de'), 'fr-FR': ('fr-FR', 'fr'), 'es-ES': ('es-ES', 'es'),
    'it-IT': ('it', 'it'), 'nl-NL': ('nl-NL', 'nl'), 'pt-BR': ('pt-BR', 'pt-br'),
    'pt-PT': ('pt-PT', 'pt-pt'), 'id': ('id', 'id'), 'vi': ('vi', 'vi'), 'th': ('th', 'th')
}
KEYS = ['overview', 'settlement', 'roles', 'meetup', 'receipt', 'fx', 'insights', 'quick', 'games']


class Hero(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_h1 = False
        self.in_span = False
        self.spans = []

    def handle_starttag(self, tag, attrs):
        if tag == 'h1':
            self.in_h1 = True
        elif tag == 'span' and self.in_h1:
            self.in_span = True
            self.spans.append('')

    def handle_endtag(self, tag):
        if tag == 'h1':
            self.in_h1 = False
        elif tag == 'span':
            self.in_span = False

    def handle_data(self, data):
        if self.in_span:
            self.spans[-1] += data


def checked_bytes(path, expected):
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError(f'Approved source hash mismatch: {path}')
    return data


def source_relative(value):
    _, separator, relative = value.partition('/docs/store_listing/')
    if not separator:
        raise ValueError(f'Unexpected source path in pinned manifest: {value}')
    return Path('docs/store_listing') / relative


def import_gallery(source_root):
    manifest_data = checked_bytes(source_root / MANIFEST, MANIFEST_SHA256)
    rows = json.loads(manifest_data)['rows']
    english_sources = json.loads((ROOT / 'content/site-assets.json').read_text())['gallerySources']
    result = {
        'canonicalManifest': {'path': MANIFEST, 'sha256': MANIFEST_SHA256},
        'sourceAuthority': 'docs/work_history/store_screenshot_visual_alignment_2026.10.17.md',
        'scope': '15 website languages; original store catalogue remains 16 locales. Native artwork is copied without transformation.',
        'format': 'apple-medium', 'width': 1206, 'height': 2622, 'locales': {}
    }
    added = 0
    for locale, (source_locale, folder) in LOCALES.items():
        selected = sorted((row for row in rows if row['locale'] == source_locale and row['format'] == 'apple-medium'), key=lambda row: row['order'])
        if [row['order'] for row in selected] != list(range(1, 10)) or [row['key'] for row in selected] != KEYS:
            raise ValueError(f'Gallery ordering mismatch: {locale}')
        hero_row = selected[0]
        hero_path = source_relative(hero_row['html'])
        hero_data = checked_bytes(source_root / hero_path, hero_row['htmlSHA256'])
        hero = Hero()
        hero.feed(hero_data.decode())
        if len(hero.spans) < 2 or any(not text.strip() for text in hero.spans):
            raise ValueError(f'Cannot read approved hero spans: {locale}')
        entry = {
            'sourceLocale': source_locale,
            'hero': {
                'sourceID': hero_row['id'],
                'html': str(hero_path),
                'htmlSHA256': hero_row['htmlSHA256'],
                'spans': hero.spans,
                'title': [hero.spans[0], ' '.join(hero.spans[1:])]
            },
            'images': []
        }
        for index, row in enumerate(selected):
            source_png = source_relative(row['nativePNG'])
            data = checked_bytes(source_root / source_png, row['nativeSHA256'])
            if data[:8] != b'\x89PNG\r\n\x1a\n' or struct.unpack('>II', data[16:24]) != (1206, 2622):
                raise ValueError(f'Unexpected PNG dimensions: {row["id"]}')
            if locale == 'en-US':
                src = english_sources[index]
                destination = src.split('?', 1)[0].lstrip('/')
                if (ROOT / destination).read_bytes() != data:
                    raise ValueError(f'Existing English artwork differs: {destination}')
            else:
                destination = f'images/{folder}/{row["order"]:02d}-{row["key"]}.png'
                src = f'/{destination}?v={row["nativeSHA256"][:12]}'
                (ROOT / destination).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source_root / source_png, ROOT / destination)
                added += 1
            if hashlib.sha256((ROOT / destination).read_bytes()).hexdigest() != row['nativeSHA256']:
                raise ValueError(f'Copied artwork differs: {destination}')
            entry['images'].append({
                'sourceID': row['id'], 'sourcePNG': str(source_png),
                'sourceSHA256': row['nativeSHA256'], 'order': row['order'], 'key': row['key'],
                'destination': destination, 'src': src, 'bytes': len(data), 'width': 1206, 'height': 2622
            })
        result['locales'][locale] = entry
    (ROOT / 'content/gallery.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'webLanguages': len(result['locales']), 'nativeImages': 135, 'copiedImages': added, 'totalBytes': sum(image['bytes'] for locale in result['locales'].values() for image in locale['images'])}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source_root', type=Path, help='The separate SPEND checkout containing the approved store artwork')
    import_gallery(parser.parse_args().source_root.resolve())

#!/usr/bin/env python3
"""Render reviewed locale content as crawlable static GitHub Pages documents."""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
import subprocess
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://app.spendlab.net'
APPLE = 'https://apps.apple.com/app/id1208128587'
GOOGLE = 'https://play.google.com/store/apps/details?id=net.spendlab.spend'
REGISTRY = json.loads(subprocess.check_output(['node', '-e', 'process.stdout.write(JSON.stringify(require("./site-language.js").locales))'], cwd=ROOT))
ASSETS = json.loads((ROOT / 'content/site-assets.json').read_text())
IMAGES = ASSETS['gallerySources']
THEME_BUTTON = ASSETS['themeButton']
TRADEMARKS = ASSETS['trademarks']


def esc(value):
    return html.escape(str(value), quote=True)


def alternate_links():
    links = [f'<link rel="alternate" hreflang="{esc(info["lang"])}" href="{BASE}{esc(info["path"])}">' for info in REGISTRY.values()]
    links.append(f'<link rel="alternate" hreflang="x-default" href="{BASE}/">')
    return '\n  '.join(links)


def language_picker(locale, text):
    links = []
    for key, info in REGISTRY.items():
        current = ' aria-current="true"' if key == locale else ''
        links.append(f'<a href="{esc(info["path"])}" hreflang="{esc(info["lang"])}" lang="{esc(info["lang"])}" data-site-locale="{esc(key)}"{current}>{esc(info["name"])}</a>')
    return f'<details class="locale-picker"><summary aria-label="{esc(text["nav"]["language"])}: {esc(text["languageName"])}">{esc(text["languageName"])}</summary><nav aria-label="{esc(text["nav"]["language"])}">{"".join(links)}</nav></details>'


def render(text):
    locale = text['locale']
    info = REGISTRY[locale]
    path = info['path']
    nav = text['nav']
    toggle = THEME_BUTTON.replace('aria-label="Switch to light mode"', f'aria-label="{esc(text["themeLight"])}" data-label-light="{esc(text["themeLight"])}" data-label-dark="{esc(text["themeDark"])}"')
    image_markup = []
    for index, (source, alt) in enumerate(zip(IMAGES, text['screenshotAlts'])):
        loading = ' loading="lazy"' if index >= 3 else ''
        image_markup.append(f'<img src="{esc(source)}" width="1206" height="2622"{loading} alt="{esc(alt)}">')
    features = ''.join(f'<article class="feature"><h3>{esc(item["title"])}</h3><p>{esc(item["body"])}</p></article>' for item in text['features'])
    guides = []
    for item in text['guides']:
        steps = ''.join(f'<li>{esc(step)}</li>' for step in item['steps'])
        guides.append(f'<article class="guide" id="{esc(item["id"])}"><div><h3>{esc(item["title"])}</h3><p>{esc(item["body"])}</p></div><div><ol>{steps}</ol><aside class="guide-example"><h4>{esc(item["exampleTitle"])}</h4><p>{esc(item["example"])}</p></aside></div></article>')
    faqs = ''.join(f'<article class="faq-item"><h3>{esc(item["question"])}</h3><p>{esc(item["answer"])}</p></article>' for item in text['faqs'])
    roadmap_icons = ASSETS['roadmapIcons']
    roadmap = ''.join(f'<div class="roadmap-item"><dt>{icon}{esc(item["title"])}</dt><dd>{esc(item["body"])}</dd></div>' for icon, item in zip(roadmap_icons, text['roadmapItems']))
    return f'''<!doctype html>
<html lang="{esc(info['lang'])}" data-theme="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{esc(text['metaDescription'])}">
  <meta name="theme-color" content="#0a0a0a">
  <title>{esc(text['metaTitle'])}</title>
  <link rel="canonical" href="{BASE}{esc(path)}">
  {alternate_links()}
  <meta property="og:type" content="website">
  <meta property="og:title" content="{esc(text['metaTitle'])}">
  <meta property="og:description" content="{esc(text['metaDescription'])}">
  <meta property="og:url" content="{BASE}{esc(path)}">
  <meta property="og:image" content="{BASE}/apple-touch-icon.png">
  <link rel="icon" type="image/svg+xml" href="/favicon.svg">
  <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
  <link rel="stylesheet" href="/style.css?v=shared1">
  <link rel="stylesheet" href="/landing.css?v=badges4">
  <link rel="stylesheet" href="/discovery.css?v=20261107">
  <script src="/site-language.js?v=20261107"></script>
  <script src="/theme.js?v=spend-neutral1" defer></script>
</head>
<body class="landing">
  <div class="page">
    <header>
      <a class="wordmark" href="{esc(path)}" aria-label="SPEND">SPEND</a>
      <div class="header-controls">
        <nav class="primary-nav" aria-label="{esc(nav['main'])}"><a href="{esc(path)}" aria-current="page">{esc(nav['home'])}</a><a href="#guides">{esc(nav['guides'])}</a><a href="/privacy/">Privacy</a></nav>
        <div class="language-theme-controls">
          {language_picker(locale, text)}
          {toggle}
        </div>
      </div>
    </header>
    <main>
      <section class="intro" aria-labelledby="intro-title">
        <h1 id="intro-title">{esc(text['hero']['title'][0])}<br><span>{esc(text['hero']['title'][1])}</span></h1>
        <p class="intro-copy">{esc(text['hero']['body'])}</p>
        <div class="store-links">
          <a class="store-link" href="{APPLE}"><img src="/assets/store-badges/app-store-en.svg" height="48" alt="{esc(text['storeAlts'][0])}"></a>
          <a class="store-link store-link--google" href="{GOOGLE}"><img src="/assets/store-badges/google-play-en.png" width="646" height="250" alt="{esc(text['storeAlts'][1])}"></a>
        </div>
        <p class="availability">{esc(text['availability'])}</p>
      </section>
      <section class="screens-section" aria-label="{esc(text['screensTitle'])}">
        <div class="screens" tabindex="0" aria-label="{esc(text['screensLabel'])}">
          {''.join(image_markup)}
        </div>
        <p class="screens-note">{esc(text['screensNote'])}</p>
      </section>
      <section class="content-section" id="features" aria-labelledby="features-title">
        <div class="section-heading"><h2 id="features-title">{esc(text['featuresTitle'])}</h2><p>{esc(text['featuresIntro'])}</p></div>
        <div class="features-grid">{features}</div>
      </section>
      <section class="content-section" id="guides" aria-labelledby="guides-title">
        <div class="section-heading"><h2 id="guides-title">{esc(text['guidesTitle'])}</h2><p>{esc(text['guidesIntro'])}</p></div>
        <div class="guides-list">{''.join(guides)}</div>
      </section>
      <section class="content-section" id="faq" aria-labelledby="faq-title">
        <div class="section-heading"><h2 id="faq-title">{esc(text['faqTitle'])}</h2></div>
        <div class="faq-list">{faqs}</div>
      </section>
      <section class="roadmap" aria-labelledby="roadmap-title">
        <div class="roadmap-heading"><h2 id="roadmap-title">{esc(text['roadmapTitle'])}</h2><p>{esc(text['roadmapIntro'])}</p></div>
        <dl class="roadmap-list">{roadmap}</dl>
      </section>
    </main>
    <footer class="site-footer">
      <span>© 2017 SPEND</span>
      <nav aria-label="{esc(nav['footer'])}"><a href="/privacy/">Privacy</a><a href="mailto:cs@spendlab.net">{esc(nav['contact'])} <span aria-hidden="true">↗</span></a></nav>
      {TRADEMARKS}
    </footer>
  </div>
</body>
</html>
'''


def validate_shape(value, reference, path=''):
    if type(value) is not type(reference):
        raise ValueError(f'{path}: incompatible content type')
    if isinstance(reference, dict):
        if value.keys() != reference.keys():
            raise ValueError(f'{path}: content fields do not match canonical English')
        for key in reference:
            validate_shape(value[key], reference[key], f'{path}.{key}')
    elif isinstance(reference, list):
        if len(value) != len(reference):
            raise ValueError(f'{path}: item count does not match canonical English')
        for index, item in enumerate(value):
            validate_shape(item, reference[index], f'{path}[{index}]')
    elif not value.strip():
        raise ValueError(f'{path}: empty content')


def build(selected=None):
    reference = json.loads((ROOT / 'content/locales/en-US.json').read_text())
    keys = selected or list(REGISTRY)
    for locale in keys:
        text = json.loads((ROOT / 'content/locales' / f'{locale}.json').read_text())
        validate_shape(text, reference, locale)
        if text['locale'] != locale or text['htmlLang'] != REGISTRY[locale]['lang']:
            raise ValueError(f'Locale identity mismatch: {locale}')
        if [item['id'] for item in text['guides']] != [item['id'] for item in reference['guides']]:
            raise ValueError(f'Guide identity mismatch: {locale}')
        if any(char in json.dumps(text, ensure_ascii=False) for char in ['\u00b7', '\u30fb', '\u2022', '\u2027']):
            raise ValueError(f'Unapproved separator in {locale}')
        folder = ROOT / REGISTRY[locale]['path'].strip('/')
        folder.mkdir(exist_ok=True)
        rendered = render(text)
        (folder / 'index.html').write_text(rendered)
        if locale == 'en-US':
            (ROOT / 'index.html').write_text(rendered)
    ET.register_namespace('', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    sitemap = ET.Element('{http://www.sitemaps.org/schemas/sitemap/0.9}urlset')
    for info in REGISTRY.values():
        url = ET.SubElement(sitemap, '{http://www.sitemaps.org/schemas/sitemap/0.9}url')
        ET.SubElement(url, '{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text = BASE + info['path']
    (ROOT / 'sitemap.xml').write_bytes(ET.tostring(sitemap, encoding='utf-8', xml_declaration=True) + b'\n')
    (ROOT / 'robots.txt').write_text(f'Sitemap: {BASE}/sitemap.xml\n')
    print(f'Rendered {len(keys)} locale pages and the English neutral entry when selected.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--locales', nargs='+', choices=list(REGISTRY), help='Render selected locales during editorial review; the default builds all 16.')
    build(parser.parse_args().locales)

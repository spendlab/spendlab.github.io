const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const language = require('../site-language.js');

test('each supported language selects its published route', () => {
  for (const locale of Object.keys(language.locales)) {
    assert.equal(language.preferredLocale([locale]), locale);
    assert.equal(language.redirectTarget({ pathname: '/', languages: [locale] }), language.locales[locale].path);
  }
});

test('regional Portuguese, Chinese scripts and English remain distinct', () => {
  for (const [input, expected] of [
    ['pt-PT', 'pt-PT'], ['pt-BR', 'pt-BR'], ['pt-AO', 'pt-PT'], ['pt', 'pt-BR'],
    ['zh-Hant', 'zh-TW'], ['zh-HK', 'zh-TW'], ['zh-TW', 'zh-TW'],
    ['zh-Hans', 'zh-CN'], ['zh-SG', 'zh-CN'], ['zh-Hans-HK', 'zh-CN'],
    ['en-GB', 'en-GB'], ['en-AU', 'en-GB'], ['en-US', 'en-US'], ['en-CA', 'en-US']
  ]) assert.equal(language.matchLanguage(input), expected, input);
});

test('browser preference order and supported manual choice take priority', () => {
  assert.equal(language.preferredLocale(['ru-RU', 'ja-JP', 'ko-KR']), 'ja-JP');
  assert.equal(language.preferredLocale(['en-US', 'ko-KR']), 'en-US');
  assert.equal(language.preferredLocale(['ja-JP'], 'ko-KR'), 'ko-KR');
  assert.equal(language.preferredLocale(['de-DE'], 'https://evil.example/'), 'de-DE');
  assert.equal(language.preferredLocale(['ru-RU', 'ar-SA']), 'en-US');
  assert.equal(language.preferredLocale([]), 'en-US');
});

test('explicit locale, policy, legacy and unknown paths never redirect', () => {
  const paths = Object.values(language.locales).flatMap(info => [info.path, info.path + 'index.html']);
  paths.push('/privacy/', '/privacy/index.html', '/spend/2019/01/30/privacy-policy.html', '/unknown/');
  for (const pathname of paths) {
    assert.equal(language.redirectTarget({ pathname, remembered: 'ja-JP', languages: ['ko-KR'] }), null, pathname);
  }
});

test('root routing preserves campaign query and guide fragment without another root hop', () => {
  const target = language.redirectTarget({ pathname: '/index.html', languages: ['ko-KR'], search: '?utm_source=chatgpt.com&x=1', hash: '#guides' });
  assert.equal(target, '/ko/?utm_source=chatgpt.com&x=1#guides');
  assert.equal(language.redirectTarget({ pathname: '/ko/', languages: ['en-US'] }), null);
});

test('blocked local storage does not prevent initial language navigation', () => {
  let destination;
  const window = {
    document: {},
    location: { pathname: '/', search: '?campaign=test', hash: '#features', replace(value) { destination = value; } },
    navigator: { languages: ['pt-PT', 'en-US'] }
  };
  Object.defineProperty(window, 'localStorage', { get() { throw new Error('Storage denied'); } });
  vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../site-language.js'), 'utf8'), { window });
  assert.equal(destination, '/pt-pt/?campaign=test#features');
});

test('a language link keeps navigating when preference storage is unavailable', () => {
  const clicks = [];
  const link = { dataset: { siteLocale: 'ja-JP' }, href: '/ja/', addEventListener(type, listener) { clicks.push({ type, listener }); } };
  const document = { readyState: 'complete', querySelectorAll() { return [link]; }, getElementById() { return null; } };
  const window = {
    document, navigator: { languages: ['ko-KR'] },
    location: { pathname: '/en/', search: '?source=guide', hash: '#multiple-payers', replace() { throw new Error('Explicit URL should remain'); } },
    addEventListener() {},
    localStorage: { setItem() { throw new Error('Storage denied'); } }
  };
  vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../site-language.js'), 'utf8'), { window });
  assert.equal(link.href, '/ja/?source=guide#multiple-payers');
  assert.equal(clicks[0].type, 'click');
  assert.doesNotThrow(() => clicks[0].listener());
});

test('switching language after an in-page guide jump keeps the current fragment', () => {
  const events = {};
  const link = { dataset: { siteLocale: 'en-US' }, href: '/en/', addEventListener() {} };
  const window = {
    document: { readyState: 'complete', querySelectorAll() { return [link]; }, getElementById() { return null; } },
    navigator: { languages: ['ko-KR'] },
    location: { pathname: '/ko/', search: '?source=guide', hash: '', replace() { throw new Error('Explicit URL should remain'); } },
    addEventListener(type, listener) { events[type] = listener; }
  };
  vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../site-language.js'), 'utf8'), { window });
  assert.equal(link.href, '/en/?source=guide');
  window.location.hash = '#guides';
  if (events.hashchange) events.hashchange();
  assert.equal(link.href, '/en/?source=guide#guides');
  window.location.hash = '#multiple-payers';
  if (events.hashchange) events.hashchange();
  assert.equal(link.href, '/en/?source=guide#multiple-payers');
});

test('unrecognized stored values cannot become destinations', () => {
  const storage = { getItem() { return '//evil.example/'; }, setItem() { throw new Error('Invalid values must not be saved'); } };
  assert.equal(language.readPreference(storage), null);
  assert.equal(language.rememberPreference(storage, '//evil.example/'), false);
  assert.equal(language.rememberPreference(storage, '__proto__'), false);
  assert.equal(language.preferredLocale(['fr-FR'], '__proto__'), 'fr-FR');
});

(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (!root || !root.document) return;

  let storage = null;
  try { storage = root.localStorage; } catch (_) { /* Language links still work. */ }
  const redirect = api.redirectTarget({
    pathname: root.location.pathname,
    search: root.location.search,
    hash: root.location.hash,
    languages: root.navigator.languages || [root.navigator.language],
    remembered: api.readPreference(storage)
  });
  if (redirect) {
    root.location.replace(redirect);
    return;
  }

  function bindControls() {
    const document = root.document;
    const languageLinks = document.querySelectorAll('a[data-site-locale]');
    function refreshLanguageLinks() {
      languageLinks.forEach(function (link) {
        const locale = link.dataset.siteLocale;
        if (!api.locales[locale]) return;
        link.href = api.locales[locale].path + root.location.search + root.location.hash;
      });
    }
    refreshLanguageLinks();
    root.addEventListener('hashchange', refreshLanguageLinks);
    languageLinks.forEach(function (link) {
      const locale = link.dataset.siteLocale;
      if (!api.locales[locale]) return;
      link.addEventListener('click', function () {
        api.rememberPreference(storage, locale);
      });
    });

    const toggle = document.getElementById('theme-toggle');
    if (!toggle) return;
    function labelTheme() {
      const dark = document.documentElement.dataset.theme === 'dark';
      const label = dark ? toggle.dataset.labelLight : toggle.dataset.labelDark;
      if (!label) return;
      toggle.setAttribute('aria-label', label);
      toggle.title = label;
    }
    labelTheme();
    toggle.addEventListener('click', labelTheme);
  }
  if (root.document.readyState === 'loading') {
    root.document.addEventListener('DOMContentLoaded', bindControls);
  } else {
    bindControls();
  }
})(typeof window === 'undefined' ? null : window, function () {
  'use strict';
  const locales = {
    'en-US': { path: '/en/', lang: 'en-US', name: 'English (US)' },
    'en-GB': { path: '/en-gb/', lang: 'en-GB', name: 'English (UK)' },
    'ko-KR': { path: '/ko/', lang: 'ko', name: '한국어' },
    'ja-JP': { path: '/ja/', lang: 'ja', name: '日本語' },
    'zh-CN': { path: '/zh-hans/', lang: 'zh-Hans', name: '简体中文' },
    'zh-TW': { path: '/zh-hant/', lang: 'zh-Hant', name: '繁體中文' },
    'de-DE': { path: '/de/', lang: 'de', name: 'Deutsch' },
    'fr-FR': { path: '/fr/', lang: 'fr', name: 'Français' },
    'es-ES': { path: '/es/', lang: 'es', name: 'Español' },
    'it-IT': { path: '/it/', lang: 'it', name: 'Italiano' },
    'nl-NL': { path: '/nl/', lang: 'nl', name: 'Nederlands' },
    'pt-BR': { path: '/pt-br/', lang: 'pt-BR', name: 'Português (Brasil)' },
    'pt-PT': { path: '/pt-pt/', lang: 'pt-PT', name: 'Português (Portugal)' },
    id: { path: '/id/', lang: 'id', name: 'Bahasa Indonesia' },
    vi: { path: '/vi/', lang: 'vi', name: 'Tiếng Việt' },
    th: { path: '/th/', lang: 'th', name: 'ไทย' }
  };
  const preferenceKey = 'spend-site-language';
  const simpleLanguages = { ko: 'ko-KR', ja: 'ja-JP', de: 'de-DE', fr: 'fr-FR', es: 'es-ES', it: 'it-IT', nl: 'nl-NL', id: 'id', vi: 'vi', th: 'th' };

  function matchLanguage(value) {
    if (typeof value !== 'string') return null;
    const parts = value.trim().replace(/_/g, '-').toLowerCase().split('-');
    const language = parts[0];
    if (language === 'zh') {
      if (parts.includes('hant')) return 'zh-TW';
      if (parts.includes('hans')) return 'zh-CN';
      return parts.some(function (part) { return ['tw', 'hk', 'mo'].includes(part); }) ? 'zh-TW' : 'zh-CN';
    }
    if (language === 'pt') return parts.slice(1).some(function (part) { return ['pt', 'ao', 'mz', 'cv', 'gw', 'st', 'tl'].includes(part); }) ? 'pt-PT' : 'pt-BR';
    if (language === 'en') return parts.slice(1).some(function (part) { return ['gb', 'uk', 'au', 'nz', 'ie', 'za', 'in', 'sg'].includes(part); }) ? 'en-GB' : 'en-US';
    return simpleLanguages[language] || null;
  }

  function preferredLocale(languages, remembered) {
    if (Object.prototype.hasOwnProperty.call(locales, remembered)) return remembered;
    for (const language of Array.isArray(languages) ? languages : []) {
      const match = matchLanguage(language);
      if (match) return match;
    }
    return 'en-US';
  }

  function redirectTarget(options) {
    if (!options || !['/', '/index.html'].includes(options.pathname)) return null;
    const locale = preferredLocale(options.languages, options.remembered);
    return locales[locale].path + (options.search || '') + (options.hash || '');
  }

  function readPreference(storage) {
    try {
      const value = storage && storage.getItem(preferenceKey);
      return Object.prototype.hasOwnProperty.call(locales, value) ? value : null;
    } catch (_) { return null; }
  }

  function rememberPreference(storage, locale) {
    if (!Object.prototype.hasOwnProperty.call(locales, locale)) return false;
    try {
      if (!storage) return false;
      storage.setItem(preferenceKey, locale);
      return true;
    } catch (_) { return false; }
  }
  return { locales: locales, matchLanguage: matchLanguage, preferredLocale: preferredLocale, redirectTarget: redirectTarget, readPreference: readPreference, rememberPreference: rememberPreference };
});

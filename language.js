const languages = ['ko', 'en'];
function showLanguage() {
  const requested = location.hash.slice(1);
  const language = languages.includes(requested) ? requested : 'ko';
  document.documentElement.lang = language;
  document.title = language === 'ko' ? '개인정보처리방침 · SPEND' : 'Privacy Policy · SPEND';
  for (const id of languages) document.getElementById(id).hidden = id !== language;
  for (const link of document.querySelectorAll('[data-language]')) {
    if (link.dataset.language === language) link.setAttribute('aria-current', 'true');
    else link.removeAttribute('aria-current');
  }
}
window.addEventListener('hashchange', showLanguage);
showLanguage();

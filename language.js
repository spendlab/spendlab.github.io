const languages = ['ko', 'en'];
const themeToggle = document.getElementById('theme-toggle');
function updateThemeLabel() {
  const dark = document.documentElement.dataset.theme === 'dark';
  const ko = document.documentElement.lang === 'ko';
  themeToggle.textContent = ko ? (dark ? '라이트' : '다크') : (dark ? 'Light' : 'Dark');
  themeToggle.setAttribute('aria-label', ko ? (dark ? '라이트 모드로 전환' : '다크 모드로 전환') : (dark ? 'Switch to light mode' : 'Switch to dark mode'));
}
themeToggle.hidden = false;
themeToggle.addEventListener('click', () => {
  const dark = document.documentElement.dataset.theme !== 'dark';
  document.documentElement.dataset.theme = dark ? 'dark' : 'light';
  document.querySelector('meta[name="theme-color"]').content = dark ? '#111413' : '#ffffff';
  updateThemeLabel();
});
function showLanguage() {
  const requested = location.hash.slice(1);
  const language = languages.includes(requested) ? requested : 'ko';
  document.documentElement.lang = language;
  updateThemeLabel();
  document.title = language === 'ko' ? '개인정보처리방침 · SPEND' : 'Privacy Policy · SPEND';
  for (const id of languages) document.getElementById(id).hidden = id !== language;
  for (const link of document.querySelectorAll('[data-language]')) {
    if (link.dataset.language === language) link.setAttribute('aria-current', 'true');
    else link.removeAttribute('aria-current');
  }
}
window.addEventListener('hashchange', showLanguage);
showLanguage();

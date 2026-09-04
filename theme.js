const themeToggle = document.getElementById('theme-toggle');
function updateThemeLabel() {
  const dark = document.documentElement.dataset.theme === 'dark';
  const label = dark ? 'Switch to light mode' : 'Switch to dark mode';
  themeToggle.setAttribute('aria-label', label);
  themeToggle.title = label;
}
themeToggle.hidden = false;
themeToggle.addEventListener('click', () => {
  const dark = document.documentElement.dataset.theme !== 'dark';
  document.documentElement.dataset.theme = dark ? 'dark' : 'light';
  document.querySelector('meta[name="theme-color"]').content = dark ? '#111413' : '#ffffff';
  updateThemeLabel();
});
updateThemeLabel();

(function () {
  var TURN_MS = 2000;
  var KEY = 'sl-dir';

  var SVG = '<svg class="sl" viewBox="0 0 340 96" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">' +
    '<g fill="none" stroke="#f2c14e" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round">' +
    '<rect x="8" y="38" width="52" height="28" rx="2" fill="#1a1a1a"/>' +
    '<rect x="64" y="36" width="58" height="30" rx="2" fill="#1a1a1a"/>' +
    '<rect x="126" y="34" width="46" height="32" rx="2" fill="#111"/>' +
    '<path d="M176 64 V28 h78 a8 8 0 0 1 8 8 v28z" fill="#1a1408"/>' +
    '<rect x="262" y="22" width="36" height="42" rx="2" fill="#111"/>' +
    '<path d="M278 22 v-12 h8 v12" fill="#f2c14e"/>' +
    '<circle class="steam" cx="282" cy="6" r="7" fill="#ddd" stroke="none"/>' +
    '<circle class="steam" cx="294" cy="2" r="5" fill="#bbb" stroke="none" style="animation-delay:.18s"/>' +
    '<circle class="steam" cx="272" cy="0" r="4" fill="#999" stroke="none" style="animation-delay:.36s"/>' +
    '<circle cx="28" cy="72" r="10" fill="#111"/><circle cx="28" cy="72" r="4" fill="#f2c14e" stroke="none"/>' +
    '<circle cx="86" cy="72" r="10" fill="#111"/><circle cx="86" cy="72" r="4" fill="#f2c14e" stroke="none"/>' +
    '<circle cx="148" cy="74" r="8" fill="#111"/>' +
    '<circle cx="196" cy="74" r="11" fill="#111"/><circle cx="196" cy="74" r="4" fill="#f2c14e" stroke="none"/>' +
    '<circle cx="230" cy="74" r="11" fill="#111"/><circle cx="230" cy="74" r="4" fill="#f2c14e" stroke="none"/>' +
    '<circle cx="278" cy="74" r="10" fill="#111"/><circle cx="278" cy="74" r="4" fill="#f2c14e" stroke="none"/>' +
    '<path d="M176 48 h90" stroke-width="1.6"/>' +
    '<path d="M8 66 h290"/>' +
    '</g></svg>';

  function overlay() {
    var el = document.getElementById('sl-run');
    if (el) return el;
    el = document.createElement('div');
    el.id = 'sl-run';
    el.innerHTML = '<div class="page">' + SVG + '</div><div class="rail"></div>';
    document.body.appendChild(el);
    return el;
  }

  function reduced() {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }

  function go(href, dir) {
    try { sessionStorage.setItem(KEY, dir); } catch (err) {}
    if (reduced()) {
      location.href = href;
      return;
    }
    var el = overlay();
    el.className = '';
    void el.offsetWidth;
    el.className = 'on ' + dir;
    setTimeout(function () { location.href = href; }, TURN_MS);
  }

  function playEnter() {
    var dir;
    try {
      dir = sessionStorage.getItem(KEY);
      sessionStorage.removeItem(KEY);
    } catch (err) {
      document.documentElement.classList.remove('sl-wait');
      return;
    }
    if (!dir || reduced()) {
      document.documentElement.classList.remove('sl-wait');
      return;
    }
    var el = overlay();
    el.className = 'on ' + dir + ' enter';
    document.documentElement.classList.remove('sl-wait');
    setTimeout(function () { el.className = ''; }, TURN_MS);
  }

  function kind(href) {
    var path = href.split('?')[0].split('#')[0];
    var file = path.split('/').pop() || '';
    if (file === 'index.html' || file === '' || file === '.') return 'index';
    if (/^(tokyo|osaka|hukuoka)\.html$/.test(file)) return 'map';
    return '';
  }

  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href]');
    if (!a) return;
    if (a.target === '_blank' || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    var type = kind(a.getAttribute('href') || '');
    if (!type) return;
    e.preventDefault();
    var file = (a.getAttribute('href') || '').split('?')[0].split('#')[0].split('/').pop();
    var dir = file === 'tokyo.html' ? 'rtl' : 'ltr';
    go(a.href, dir);
  });

  playEnter();
})();

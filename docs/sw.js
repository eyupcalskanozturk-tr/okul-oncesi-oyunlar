/* Okul Öncesi Oyunlar: çevrimdışı çalışma.
   Sayfalar önce internetten alınır (en yeni sürüm), internet yoksa cihazdaki kopya açılır. */
const VERSION = 'd4d7d81b3ce0';
const CACHE = 'oyunlar-' + VERSION;
const FILES = [
  "./",
  "index.html",
  "manifest.webmanifest",
  "icons/apple-touch-icon.png",
  "icons/favicon-32.png",
  "icons/icon-192.png",
  "icons/icon-512.png",
  "icons/maskable-512.png",
  "oyunlar/mandalli-kelimeler.html",
  "oyunlar/harf-avcilari.html",
  "oyunlar/ahtapot.html",
  "oyunlar/hafiza-bavulu.html",
  "oyunlar/cizgi-takibi.html"
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k.startsWith('oyunlar-') && k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

function fromNetwork(req, ms) {
  return new Promise((resolve, reject) => {
    const t = setTimeout(() => reject(new Error('zaman aşımı')), ms);
    fetch(req).then(res => {
      clearTimeout(t);
      if (res && res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(req, copy)); }
      resolve(res);
    }, err => { clearTimeout(t); reject(err); });
  });
}

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== self.location.origin) return;
  const page = req.mode === 'navigate' || (req.headers.get('accept') || '').includes('text/html');
  if (page) {
    e.respondWith(caches.match(req, { ignoreSearch: true }).then(cached =>
      fromNetwork(req, cached ? 4000 : 30000).catch(() => cached || caches.match('./'))));
  } else {
    e.respondWith(caches.match(req, { ignoreSearch: true }).then(cached => cached || fetch(req)));
  }
});

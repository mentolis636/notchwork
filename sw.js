// Notchwork service worker: lets the app open without a connection.
// Bump CACHE when you want every installed copy to drop its old files.
const CACHE = 'notchwork-v1';
const CORE = [
  './',
  'index.html',
  'manifest.webmanifest',
  'icons/icon-192.png',
  'icons/icon-512.png',
  'icons/icon-maskable-512.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE).then(cache => cache.addAll(CORE)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

function remember(request, response) {
  if (response && (response.ok || response.type === 'opaque')) {
    const copy = response.clone();
    caches.open(CACHE).then(cache => cache.put(request, copy));
  }
  return response;
}

self.addEventListener('fetch', event => {
  const request = event.request;
  if (request.method !== 'GET') return;

  const url = new URL(request.url);
  const sameOrigin = url.origin === self.location.origin;
  const fonts = url.hostname === 'fonts.googleapis.com' || url.hostname === 'fonts.gstatic.com';
  if (!sameOrigin && !fonts) return;

  if (sameOrigin) {
    // Own files: try the network first so updates arrive, fall back to the cache offline.
    event.respondWith(
      fetch(request)
        .then(response => remember(request, response))
        .catch(() => caches.match(request, { ignoreSearch: true }).then(hit => hit || caches.match('index.html')))
    );
  } else {
    // Pixel fonts: cache first, so the look survives offline after the first visit.
    event.respondWith(
      caches.match(request).then(hit => hit || fetch(request).then(response => remember(request, response)))
    );
  }
});

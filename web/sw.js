// SlowfiClock offline cache: the app shell works without a connection after the first visit
const CACHE = 'slowfi-v5';
// precache:start
const ASSETS = [
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "./content/catalog.json",
  "./icons/apple-touch-icon.png",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
  "./icons/icon-maskable-512.png",
  "./fonts/cormorant-garamond-latin-500-italic.woff2",
  "./fonts/cormorant-garamond-latin-500-normal.woff2",
  "./fonts/cormorant-garamond-latin-600-normal.woff2",
  "./fonts/jost-latin-300-normal.woff2",
  "./fonts/jost-latin-400-normal.woff2",
  "./fonts/jost-latin-500-normal.woff2",
  "./content/clocks/walnut-dusk/frame.webp",
  "./content/backgrounds/stadium-dusk/image.jpg",
  "./content/sands/cr7-celebration/picture.png",
  "./content/music/transformation/track.mp3",
  "./content/clocks/walnut-lamp/frame.webp",
  "./content/backgrounds/night-desk/image.jpg",
  "./content/sands/mona-lisa/picture.png"
];
// precache:end

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(ASSETS)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))).then(() => self.clients.claim()));
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin === self.location.origin) {
    // app shell: serve from cache, refresh in the background
    e.respondWith(caches.open(CACHE).then((c) => c.match(req, { ignoreSearch: true }).then((hit) => {
      const net = fetch(req).then((res) => { if (res.ok) c.put(req, res.clone()); return res; }).catch(() => hit || c.match('./index.html'));
      return hit || net;
    })));
  } else if (/fonts\.(googleapis|gstatic)\.com$/.test(url.hostname)) {
    // fonts: keep a copy so the type still looks right offline
    e.respondWith(caches.open(CACHE).then((c) => c.match(req).then((hit) => hit || fetch(req).then((res) => { c.put(req, res.clone()); return res; }))));
  }
});

const CACHE = "md-v4";
const STATIC = [
  "/",
  "/index.html",
  "/dashboard.html",
  "/preferences.html",
  "/pricing.html",
  "/contact.html",
  "/ui-pro.js",
  "/logo-icon.svg",
  "/manifest.json",
  "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap"
];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(STATIC).catch(() => {})));
  self.skipWaiting();
});

self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(keys =>
    Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
  ));
  self.clients.claim();
});

self.addEventListener("fetch", e => {
  if (e.request.method !== "GET") return;
  const url = new URL(e.request.url);
  // Always network-first for API/Worker calls
  if (url.hostname.includes("workers.dev") || url.pathname.startsWith("/api")) {
    return;
  }
  // 同源資源(HTML / JS / CSS)一律抓伺服器最新版,繞過瀏覽器 HTTP 快取;
  // 快取只當離線後援 —— 避免改版後看到舊頁或新舊檔案版本不一致。
  const sameOrigin = url.origin === self.location.origin;
  const req = sameOrigin ? new Request(e.request.url, { cache: "no-store" }) : e.request;
  e.respondWith(
    fetch(req)
      .then(res => {
        if (res.ok) {
          const clone = res.clone();
          caches.open(CACHE).then(c => c.put(e.request, clone));
        }
        return res;
      })
      .catch(() => caches.match(e.request))
  );
});

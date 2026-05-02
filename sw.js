// Service Worker - キャッシュ完全無効版
const CACHE_NAME = "junior-vocab-v17";

self.addEventListener("install", event => {
  self.skipWaiting();
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.map(key => caches.delete(key)))
    ).then(() => self.clients.claim())
  );
});

// 常にネットワークから取得（キャッシュ一切なし）
self.addEventListener("fetch", event => {
  event.respondWith(
    fetch(event.request, { cache: "no-store" }).catch(() => {
      return new Response("Network error", { status: 503 });
    })
  );
});

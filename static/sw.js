/**
 * SoulLink - Service Worker
 * Web Push notifications + PWA offline support
 */

const CACHE_NAME = 'soullink-v1';
const STATIC_ASSETS = [
  '/',
  '/static/css/variables.css',
  '/static/css/base.css',
  '/static/css/components.css',
  '/static/css/animations.css',
  '/static/js/base.js',
  '/static/images/favicon.svg'
];

// ============ Install: Cache static assets ============
self.addEventListener('install', event => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(STATIC_ASSETS);
    })
  );
});

// ============ Activate: Clean old caches ============
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => {
      return Promise.all(
        keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
      );
    }).then(() => self.clients.claim())
  );
});

// ============ Fetch: Serve from cache, fallback to network ============
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(cached => {
      return cached || fetch(event.request);
    })
  );
});

// ============ Push: Show notification ============
self.addEventListener('push', event => {
  let data = {};
  if (event.data) {
    try {
      data = event.data.json();
    } catch (e) {
      data = { title: 'SoulLink', body: event.data.text() };
    }
  }

  const title = data.title || 'SoulLink 灵犀';
  const options = {
    body: data.body || '你有新的通知',
    icon: data.icon || '/static/images/favicon.svg',
    badge: '/static/images/favicon.svg',
    vibrate: [200, 100, 200],
    tag: 'soullink-notification',
    requireInteraction: true,
    data: {
      url: data.url || '/',
      notification_id: data.notification_id || null
    }
  };

  event.waitUntil(
    self.registration.showNotification(title, options)
  );
});

// ============ Notification Click: Open app and navigate ============
self.addEventListener('notificationclick', event => {
  event.notification.close();

  const urlToOpen = event.notification.data?.url || '/';

  event.waitUntil(
    clients.matchAll({
      type: 'window',
      includeUncontrolled: true
    }).then(windowClients => {
      // Check if there's already a window open
      for (const client of windowClients) {
        if (client.url.includes(window.location.host) && 'focus' in client) {
          // Navigate the existing client to the URL
          if ('navigate' in client) {
            return client.navigate(urlToOpen).then(() => client.focus());
          }
          return client.focus();
        }
      }
      // Open new window
      if (clients.openWindow) {
        return clients.openWindow(urlToOpen);
      }
    })
  );
});

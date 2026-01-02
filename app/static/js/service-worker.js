/**
 * Service Worker for PWA Support
 * Enables offline functionality and caching
 */

const CACHE_NAME = 'youtube-automation-v1';
const STATIC_CACHE = 'static-v1';
const DYNAMIC_CACHE = 'dynamic-v1';

const STATIC_ASSETS = [
  '/',
  '/static/css/modern-theme.css',
  '/static/css/theme-enhancements.css',
  '/static/favicon.ico',
  '/static/favicon.png',
  '/static/favicon.svg',
  '/static/site.webmanifest',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
  'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css',
  'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap'
];

// Install Event - Cache static assets
self.addEventListener('install', (event) => {
  console.log('[Service Worker] Installing...');
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => {
      console.log('[Service Worker] Caching static assets');
      return cache.addAll(STATIC_ASSETS);
    })
  );
  self.skipWaiting();
});

// Activate Event - Clean up old caches
self.addEventListener('activate', (event) => {
  console.log('[Service Worker] Activating...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
            console.log('[Service Worker] Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  return self.clients.claim();
});

// Fetch Event - Serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }

  // Skip API requests (they should always go to network)
  if (url.pathname.startsWith('/api/')) {
    return;
  }

  event.respondWith(
    caches.match(request).then((cachedResponse) => {
      // Return cached version if available
      if (cachedResponse) {
        return cachedResponse;
      }

      // Fetch from network
      return fetch(request)
        .then((response) => {
          // Don't cache non-successful responses
          if (!response || response.status !== 200 || response.type !== 'basic') {
            return response;
          }

          // Clone the response
          const responseToCache = response.clone();

          // Cache dynamic content
          caches.open(DYNAMIC_CACHE).then((cache) => {
            cache.put(request, responseToCache);
          });

          return response;
        })
        .catch(() => {
          // Return offline page if available
          if (request.headers.get('accept').includes('text/html')) {
            return caches.match('/');
          }
        });
    })
  );
});

// Background Sync (if supported)
self.addEventListener('sync', (event) => {
  console.log('[Service Worker] Background sync:', event.tag);
  // Implement background sync logic here
});

// Push Notifications (if supported)
self.addEventListener('push', (event) => {
  console.log('[Service Worker] Push notification received');
  const options = {
    body: event.data ? event.data.text() : 'New update available',
    icon: '/static/favicon.png',
    badge: '/static/favicon.png',
    vibrate: [200, 100, 200],
    tag: 'youtube-automation',
  };

  event.waitUntil(
    self.registration.showNotification('YouTube Automation', options)
  );
});

// Notification Click
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  event.waitUntil(
    clients.openWindow('/')
  );
});


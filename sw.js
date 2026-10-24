self.addEventListener('push', event => {
    let data = { title: 'הבית שלנו', body: 'יש לך תזכורת' };
    try { data = { ...data, ...event.data.json() }; } catch (e) {}
    event.waitUntil(self.registration.showNotification(data.title, { body: data.body, icon: 'icon.svg', dir: 'rtl', lang: 'he' }));
});

self.addEventListener('notificationclick', event => {
    event.notification.close();
    event.waitUntil(self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then(list => {
        const open = list.find(c => 'focus' in c);
        return open ? open.focus() : self.clients.openWindow('./');
    }));
});

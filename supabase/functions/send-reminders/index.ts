import webpush from 'npm:web-push@3.6.7';
import { createClient } from 'npm:@supabase/supabase-js@2';

const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
const serviceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
const publicKey = Deno.env.get('VAPID_PUBLIC_KEY')!;
const privateKey = Deno.env.get('VAPID_PRIVATE_KEY')!;
const cronSecret = Deno.env.get('CRON_SECRET')!;

webpush.setVapidDetails('https://health-app-web-umber.vercel.app', publicKey, privateKey);

const admin = createClient(supabaseUrl, serviceKey);
const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json' } });

function israelDay(offsetDays: number): string {
  const d = new Date(Date.now() + offsetDays * 86400000);
  return new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Jerusalem', year: 'numeric', month: '2-digit', day: '2-digit' }).format(d);
}

Deno.serve(async req => {
  if (req.method === 'GET') return json({ publicKey });
  if (req.method !== 'POST' || req.headers.get('x-cron-secret') !== cronSecret) return json({ error: 'forbidden' }, 403);

  const { when } = await req.json().catch(() => ({ when: 'today' }));
  const day = when === 'tomorrow' ? israelDay(1) : israelDay(0);
  const label = when === 'tomorrow' ? 'תזכורת למחר' : 'להיום';

  const { data: subs, error: subsError } = await admin.from('push_subscriptions').select('endpoint, user_id, p256dh, auth');
  if (subsError) return json({ error: subsError.message }, 500);

  let sent = 0;
  for (const sub of subs ?? []) {
    const { data: membership } = await admin.from('couple_members').select('couple_id').eq('user_id', sub.user_id).maybeSingle();
    if (!membership) continue;
    const { data: tasks } = await admin
      .from('task_items')
      .select('title, start_time, is_private, created_by, done')
      .eq('couple_id', membership.couple_id)
      .eq('due_date', day)
      .eq('done', false);
    const visible = (tasks ?? []).filter(t => !t.is_private || t.created_by === sub.user_id);
    if (visible.length === 0) continue;

    const body = visible
      .sort((a, b) => (a.start_time ?? '99:99').localeCompare(b.start_time ?? '99:99'))
      .map(t => `• ${t.title}${t.start_time ? ' ב-' + String(t.start_time).slice(0, 5) : ''}`)
      .join('\n');
    try {
      await webpush.sendNotification(
        { endpoint: sub.endpoint, keys: { p256dh: sub.p256dh, auth: sub.auth } },
        JSON.stringify({ title: `🔔 ${label}`, body }),
      );
      sent++;
    } catch (err) {
      const status = (err as { statusCode?: number }).statusCode;
      if (status === 404 || status === 410) await admin.from('push_subscriptions').delete().eq('endpoint', sub.endpoint);
    }
  }
  return json({ sent });
});

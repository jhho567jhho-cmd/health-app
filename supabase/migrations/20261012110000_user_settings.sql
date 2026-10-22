-- Per-person settings, so the privacy eye hides only for the person who turned it on. Applied to project iewlhdcinmktrzepjstc.
create table public.user_settings (
  user_id uuid primary key references auth.users(id) on delete cascade,
  hide_private boolean not null default false
);

alter table public.user_settings enable row level security;

create policy "own settings read" on public.user_settings for select
  using (user_id = auth.uid());

create policy "own settings write" on public.user_settings for insert
  with check (user_id = auth.uid());

create policy "own settings update" on public.user_settings for update
  using (user_id = auth.uid())
  with check (user_id = auth.uid());

alter publication supabase_realtime add table public.user_settings;

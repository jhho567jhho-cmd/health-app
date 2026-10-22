-- Settings shared by both partners, starting with the privacy eye toggle. Applied to project iewlhdcinmktrzepjstc.
create table public.couple_settings (
  couple_id uuid primary key references public.couples(id) on delete cascade,
  hide_private boolean not null default false,
  updated_by uuid references auth.users(id) on delete set null
);

alter table public.couple_settings enable row level security;

create policy "members read settings" on public.couple_settings for select
  using (public.is_couple_member(couple_id));

create policy "members add settings" on public.couple_settings for insert
  with check (public.is_couple_member(couple_id));

create policy "members update settings" on public.couple_settings for update
  using (public.is_couple_member(couple_id))
  with check (public.is_couple_member(couple_id));

alter publication supabase_realtime add table public.couple_settings;

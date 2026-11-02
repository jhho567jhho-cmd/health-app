-- Dropshipping work items shared by both partners: tasks to do, things to research, and notes on what to know.
create table public.dropship_items (
  id uuid primary key default gen_random_uuid(),
  couple_id uuid not null references public.couples(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  kind text not null check (kind in ('task', 'research', 'note')),
  title text not null check (length(title) between 1 and 300),
  done boolean not null default false,
  created_at timestamptz not null default now()
);

create index dropship_items_couple_id_idx on public.dropship_items (couple_id);
create index dropship_items_user_id_idx on public.dropship_items (user_id);

alter table public.dropship_items enable row level security;

create policy "members read dropship items" on public.dropship_items for select
  using (public.is_couple_member(couple_id));

create policy "members add own dropship items" on public.dropship_items for insert
  with check (public.is_couple_member(couple_id) and user_id = (select auth.uid()));

create policy "members update dropship items" on public.dropship_items for update
  using (public.is_couple_member(couple_id))
  with check (public.is_couple_member(couple_id));

create policy "members delete own dropship items" on public.dropship_items for delete
  using (user_id = (select auth.uid()));

alter publication supabase_realtime add table public.dropship_items;

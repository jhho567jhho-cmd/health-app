-- Items saved under a shopping category without being put on the list. Applied to project iewlhdcinmktrzepjstc.
create table public.shopping_catalog (
  id uuid primary key default gen_random_uuid(),
  couple_id uuid not null references public.couples(id) on delete cascade,
  created_by uuid not null references auth.users(id) on delete cascade,
  category text not null check (length(category) <= 60),
  name text not null check (length(name) between 1 and 80),
  created_at timestamptz not null default now(),
  unique (couple_id, category, name)
);

alter table public.shopping_catalog enable row level security;

create policy "members read catalog" on public.shopping_catalog for select
  using (public.is_couple_member(couple_id));

create policy "members add catalog" on public.shopping_catalog for insert
  with check (public.is_couple_member(couple_id) and created_by = auth.uid());

create policy "members delete catalog" on public.shopping_catalog for delete
  using (public.is_couple_member(couple_id));

alter publication supabase_realtime add table public.shopping_catalog;

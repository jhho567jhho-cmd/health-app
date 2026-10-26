-- Projects (side businesses, research, partner programs) and their income and expense entries, shared by both partners.
create table public.projects (
  id uuid primary key default gen_random_uuid(),
  couple_id uuid not null references public.couples(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  name text not null check (length(name) between 1 and 120),
  status text not null default 'research' check (status in ('research', 'testing', 'active', 'closed')),
  note text check (length(note) <= 500),
  created_at timestamptz not null default now()
);

create table public.project_entries (
  id uuid primary key default gen_random_uuid(),
  couple_id uuid not null references public.couples(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  project_id uuid not null references public.projects(id) on delete cascade,
  kind text not null check (kind in ('income', 'expense')),
  amount numeric(10,2) not null check (amount > 0 and amount < 1000000),
  entry_date date not null,
  note text check (length(note) <= 200),
  created_at timestamptz not null default now()
);

create index project_entries_project_id_idx on public.project_entries (project_id);

alter table public.projects enable row level security;
alter table public.project_entries enable row level security;

create policy "members read projects" on public.projects for select
  using (public.is_couple_member(couple_id));

create policy "members add own projects" on public.projects for insert
  with check (public.is_couple_member(couple_id) and user_id = (select auth.uid()));

create policy "members update projects" on public.projects for update
  using (public.is_couple_member(couple_id))
  with check (public.is_couple_member(couple_id));

create policy "members delete own projects" on public.projects for delete
  using (user_id = (select auth.uid()));

create policy "members read project entries" on public.project_entries for select
  using (public.is_couple_member(couple_id));

create policy "members add own project entries" on public.project_entries for insert
  with check (public.is_couple_member(couple_id) and user_id = (select auth.uid()));

create policy "members delete own project entries" on public.project_entries for delete
  using (user_id = (select auth.uid()));

alter publication supabase_realtime add table public.projects;
alter publication supabase_realtime add table public.project_entries;

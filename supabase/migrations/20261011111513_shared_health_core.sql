-- Applied to project iewlhdcinmktrzepjstc on 2026-10-11.
-- A "couple" is the shared space both partners belong to.
create table public.couples (
  id uuid primary key default gen_random_uuid(),
  name text not null default 'חיים ודבורה',
  created_at timestamptz not null default now()
);

create table public.couple_members (
  couple_id uuid not null references public.couples(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  display_name text not null,
  created_at timestamptz not null default now(),
  primary key (couple_id, user_id)
);

-- Helper: is the current user a member of this couple?
create or replace function public.is_couple_member(c uuid)
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select exists (
    select 1 from public.couple_members
    where couple_id = c and user_id = auth.uid()
  );
$$;

create table public.water_logs (
  couple_id uuid not null references public.couples(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  day date not null,
  glasses int not null default 0 check (glasses between 0 and 30),
  updated_at timestamptz not null default now(),
  primary key (couple_id, day)
);

create table public.task_items (
  id uuid primary key default gen_random_uuid(),
  couple_id uuid not null references public.couples(id) on delete cascade,
  created_by uuid not null references auth.users(id) on delete cascade,
  title text not null check (length(title) between 1 and 200),
  done boolean not null default false,
  done_at timestamptz,
  created_at timestamptz not null default now()
);

create table public.weight_entries (
  id uuid primary key default gen_random_uuid(),
  couple_id uuid not null references public.couples(id) on delete cascade,
  created_by uuid not null references auth.users(id) on delete cascade,
  value numeric(5,1) not null check (value > 0 and value < 400),
  measured_at timestamptz not null default now()
);

create table public.meal_logs (
  id uuid primary key default gen_random_uuid(),
  couple_id uuid not null references public.couples(id) on delete cascade,
  created_by uuid not null references auth.users(id) on delete cascade,
  name text not null check (length(name) between 1 and 200),
  calories int not null default 0 check (calories between 0 and 10000),
  category text,
  eaten_at timestamptz not null default now()
);

alter table public.couples enable row level security;
alter table public.couple_members enable row level security;
alter table public.water_logs enable row level security;
alter table public.task_items enable row level security;
alter table public.weight_entries enable row level security;
alter table public.meal_logs enable row level security;

create policy "members read couple" on public.couples
  for select using (public.is_couple_member(id));

create policy "members read membership" on public.couple_members
  for select using (user_id = auth.uid() or public.is_couple_member(couple_id));

create policy "members manage water" on public.water_logs
  for all using (public.is_couple_member(couple_id)) with check (public.is_couple_member(couple_id) and user_id = auth.uid());

create policy "members manage tasks" on public.task_items
  for all using (public.is_couple_member(couple_id)) with check (public.is_couple_member(couple_id) and created_by = auth.uid());

create policy "members manage weights" on public.weight_entries
  for all using (public.is_couple_member(couple_id)) with check (public.is_couple_member(couple_id) and created_by = auth.uid());

create policy "members manage meals" on public.meal_logs
  for all using (public.is_couple_member(couple_id)) with check (public.is_couple_member(couple_id) and created_by = auth.uid());

alter publication supabase_realtime add table public.water_logs, public.task_items, public.weight_entries, public.meal_logs;

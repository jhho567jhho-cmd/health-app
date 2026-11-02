-- Fuel purchases, one row per fill-up, shared by both partners. Applied to project iewlhdcinmktrzepjstc.
create table public.fuel_logs (
  id uuid primary key default gen_random_uuid(),
  couple_id uuid not null references public.couples(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  amount numeric(10,2) not null check (amount > 0 and amount < 100000),
  filled_on date not null,
  created_at timestamptz not null default now()
);

alter table public.fuel_logs enable row level security;

create policy "members read fuel logs" on public.fuel_logs for select
  using (public.is_couple_member(couple_id));

create policy "members add own fuel logs" on public.fuel_logs for insert
  with check (public.is_couple_member(couple_id) and user_id = auth.uid());

create policy "members delete own fuel logs" on public.fuel_logs for delete
  using (user_id = auth.uid());

alter publication supabase_realtime add table public.fuel_logs;

-- Each person marks the exercises they did on a given day. Applied to project iewlhdcinmktrzepjstc.
create table public.workout_logs (
  id uuid primary key default gen_random_uuid(),
  couple_id uuid not null references public.couples(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  exercise text not null check (length(exercise) <= 80),
  done_on date not null,
  created_at timestamptz not null default now(),
  unique (user_id, exercise, done_on)
);

alter table public.workout_logs enable row level security;

create policy "members read workout logs" on public.workout_logs for select
  using (public.is_couple_member(couple_id));

create policy "members add own workout logs" on public.workout_logs for insert
  with check (public.is_couple_member(couple_id) and user_id = auth.uid());

create policy "members delete own workout logs" on public.workout_logs for delete
  using (user_id = auth.uid());

alter publication supabase_realtime add table public.workout_logs;

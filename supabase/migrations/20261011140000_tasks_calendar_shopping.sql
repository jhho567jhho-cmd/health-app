-- NOT YET APPLIED. Run in the Supabase SQL Editor for project iewlhdcinmktrzepjstc.
-- Tasks get a due date (for the calendar) and an owner; adds a shared shopping list.

-- assigned_to null means "both of us".
alter table public.task_items
  add column due_date date,
  add column assigned_to uuid references auth.users(id) on delete set null;

create index task_items_couple_due_idx on public.task_items (couple_id, due_date);

create table public.shopping_items (
  id uuid primary key default gen_random_uuid(),
  couple_id uuid not null references public.couples(id) on delete cascade,
  created_by uuid not null references auth.users(id) on delete cascade,
  name text not null check (length(name) between 1 and 200),
  done boolean not null default false,
  done_at timestamptz,
  created_at timestamptz not null default now()
);

alter table public.shopping_items enable row level security;

create policy "members read shopping" on public.shopping_items for select using (public.is_couple_member(couple_id));
create policy "members add shopping" on public.shopping_items for insert with check (public.is_couple_member(couple_id) and created_by = auth.uid());
create policy "members update shopping" on public.shopping_items for update using (public.is_couple_member(couple_id)) with check (public.is_couple_member(couple_id));
create policy "members delete shopping" on public.shopping_items for delete using (public.is_couple_member(couple_id));

alter publication supabase_realtime add table public.shopping_items;

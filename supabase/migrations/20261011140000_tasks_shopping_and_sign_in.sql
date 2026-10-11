-- Applied to project iewlhdcinmktrzepjstc on 2026-10-11 (allowed_members rows added separately).
-- 1) Tasks get a due date and an owner; 2) shared shopping list;
-- 3) sign-in: only allow-listed emails can join the couple's shared space.

-- ---------- Security advisor fix ----------
-- is_couple_member is SECURITY DEFINER; signed-in users need it for RLS, anonymous users do not.
revoke execute on function public.is_couple_member(uuid) from public, anon;
grant execute on function public.is_couple_member(uuid) to authenticated;

-- ---------- Tasks: due date and owner ----------
-- assigned_to null means "both of us".
alter table public.task_items
  add column due_date date,
  add column assigned_to uuid references auth.users(id) on delete set null;

create index task_items_couple_due_idx on public.task_items (couple_id, due_date);

-- ---------- Shopping list ----------
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

-- ---------- Sign-in: who may join ----------
-- Filled in separately (not in this file) so personal emails stay out of the repo:
--   insert into public.allowed_members (email, display_name) values ('...', 'חיים'), ('...', 'דבורה');
create table public.allowed_members (
  email text primary key check (email = lower(email)),
  display_name text not null
);

-- RLS on with no policies: only the function below can read it.
alter table public.allowed_members enable row level security;

-- Called by the app right after sign-in. Puts the user in the single shared space
-- (creating it on first use) if their confirmed email is allow-listed.
create or replace function public.join_couple()
returns uuid
language plpgsql
security definer
set search_path = public
as $$
declare
  v_email text := lower(auth.jwt() ->> 'email');
  v_name text;
  v_couple uuid;
begin
  if auth.uid() is null then
    raise exception 'not signed in';
  end if;

  select couple_id into v_couple from public.couple_members where user_id = auth.uid();
  if v_couple is not null then
    return v_couple;
  end if;

  select display_name into v_name from public.allowed_members where email = v_email;
  if v_name is null then
    raise exception 'email not allowed';
  end if;

  select id into v_couple from public.couples order by created_at limit 1;
  if v_couple is null then
    insert into public.couples default values returning id into v_couple;
  end if;

  insert into public.couple_members (couple_id, user_id, display_name)
  values (v_couple, auth.uid(), v_name);
  return v_couple;
end;
$$;

revoke execute on function public.join_couple() from public, anon;
grant execute on function public.join_couple() to authenticated;

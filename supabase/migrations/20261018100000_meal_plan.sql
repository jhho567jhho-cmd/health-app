-- Weekly meal plan shared by both partners: one meal per day and slot. Applied to project iewlhdcinmktrzepjstc.
create table public.meal_plan (
  couple_id uuid not null references public.couples(id) on delete cascade,
  plan_date date not null,
  slot text not null check (slot in ('breakfast', 'lunch', 'dinner')),
  meal text not null check (length(meal) between 1 and 120),
  updated_by uuid references auth.users(id) on delete set null,
  primary key (couple_id, plan_date, slot)
);

alter table public.meal_plan enable row level security;

create policy "members read meal plan" on public.meal_plan for select
  using (public.is_couple_member(couple_id));

create policy "members add meal plan" on public.meal_plan for insert
  with check (public.is_couple_member(couple_id));

create policy "members update meal plan" on public.meal_plan for update
  using (public.is_couple_member(couple_id))
  with check (public.is_couple_member(couple_id));

create policy "members delete meal plan" on public.meal_plan for delete
  using (public.is_couple_member(couple_id));

alter publication supabase_realtime add table public.meal_plan;

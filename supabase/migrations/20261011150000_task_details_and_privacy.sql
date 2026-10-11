-- Applied to project iewlhdcinmktrzepjstc.
-- Task details (time range, notes, status) and private tasks.
-- A private task is visible only to the person who created it; the database
-- enforces this, so a private task never reaches the partner's phone.

alter table public.task_items
  add column is_private boolean not null default false,
  add column start_time time,
  add column end_time time,
  add column notes text check (length(notes) <= 2000),
  add column status text not null default 'pending' check (status in ('pending', 'in_progress', 'done'));

update public.task_items set status = 'done' where done;

drop policy "members read tasks" on public.task_items;
drop policy "members update tasks" on public.task_items;
drop policy "members delete tasks" on public.task_items;

create policy "members read tasks" on public.task_items for select
  using (public.is_couple_member(couple_id) and (not is_private or created_by = auth.uid()));

create policy "members update tasks" on public.task_items for update
  using (public.is_couple_member(couple_id) and (not is_private or created_by = auth.uid()))
  with check (public.is_couple_member(couple_id) and (not is_private or created_by = auth.uid()));

create policy "members delete tasks" on public.task_items for delete
  using (public.is_couple_member(couple_id) and (not is_private or created_by = auth.uid()));

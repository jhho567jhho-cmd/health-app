-- NOT YET APPLIED: the Supabase connector cancels write tools for this session.
-- Run in the Supabase SQL Editor for project iewlhdcinmktrzepjstc.
-- Both partners must be able to change shared items (e.g. tick off a task the other added).
-- The author is still recorded on insert; any member may update or delete the couple's rows.
drop policy "members manage water" on public.water_logs;
drop policy "members manage tasks" on public.task_items;
drop policy "members manage weights" on public.weight_entries;
drop policy "members manage meals" on public.meal_logs;

create policy "members read water" on public.water_logs for select using (public.is_couple_member(couple_id));
create policy "members write water" on public.water_logs for insert with check (public.is_couple_member(couple_id) and user_id = auth.uid());
create policy "members update water" on public.water_logs for update using (public.is_couple_member(couple_id)) with check (public.is_couple_member(couple_id) and user_id = auth.uid());
create policy "members delete water" on public.water_logs for delete using (public.is_couple_member(couple_id));

create policy "members read tasks" on public.task_items for select using (public.is_couple_member(couple_id));
create policy "members add tasks" on public.task_items for insert with check (public.is_couple_member(couple_id) and created_by = auth.uid());
create policy "members update tasks" on public.task_items for update using (public.is_couple_member(couple_id)) with check (public.is_couple_member(couple_id));
create policy "members delete tasks" on public.task_items for delete using (public.is_couple_member(couple_id));

create policy "members read weights" on public.weight_entries for select using (public.is_couple_member(couple_id));
create policy "members add weights" on public.weight_entries for insert with check (public.is_couple_member(couple_id) and created_by = auth.uid());
create policy "members delete weights" on public.weight_entries for delete using (public.is_couple_member(couple_id));

create policy "members read meals" on public.meal_logs for select using (public.is_couple_member(couple_id));
create policy "members add meals" on public.meal_logs for insert with check (public.is_couple_member(couple_id) and created_by = auth.uid());
create policy "members delete meals" on public.meal_logs for delete using (public.is_couple_member(couple_id));

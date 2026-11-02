-- Supabase advisor fixes for the app's own tables (legacy tables users, meals, habits, messages and profiles are not touched).
-- 1. Evaluate auth.uid() once per query instead of once per row in RLS policies.
do $$
declare
  p record;
  q text;
  wc text;
begin
  for p in
    select * from pg_policies
    where schemaname = 'public'
      and tablename in ('user_settings', 'workout_logs', 'fuel_logs', 'receipts', 'push_subscriptions', 'task_items',
                        'weight_entries', 'shopping_items', 'shopping_catalog', 'water_logs', 'couple_members', 'meal_logs')
      and (coalesce(qual, '') like '%auth.uid()%' or coalesce(with_check, '') like '%auth.uid()%')
      and (coalesce(qual, '') not like '%select auth.uid()%' and coalesce(with_check, '') not like '%select auth.uid()%')
  loop
    q := replace(p.qual, 'auth.uid()', '(select auth.uid())');
    wc := replace(p.with_check, 'auth.uid()', '(select auth.uid())');
    execute format('drop policy %I on public.%I', p.policyname, p.tablename);
    execute format(
      'create policy %I on public.%I for %s to %s%s%s',
      p.policyname, p.tablename, p.cmd, array_to_string(p.roles, ', '),
      case when q is not null then ' using (' || q || ')' else '' end,
      case when wc is not null then ' with check (' || wc || ')' else '' end
    );
  end loop;
end $$;

-- 2. Indexes for foreign keys used by the app's tables.
create index if not exists fuel_logs_couple_id_idx on public.fuel_logs (couple_id);
create index if not exists fuel_logs_user_id_idx on public.fuel_logs (user_id);
create index if not exists projects_couple_id_idx on public.projects (couple_id);
create index if not exists projects_user_id_idx on public.projects (user_id);
create index if not exists project_entries_couple_id_idx on public.project_entries (couple_id);
create index if not exists project_entries_user_id_idx on public.project_entries (user_id);
create index if not exists receipts_couple_id_idx on public.receipts (couple_id);
create index if not exists receipts_user_id_idx on public.receipts (user_id);
create index if not exists workout_logs_couple_id_idx on public.workout_logs (couple_id);
create index if not exists push_subscriptions_user_id_idx on public.push_subscriptions (user_id);
create index if not exists water_logs_user_id_idx on public.water_logs (user_id);
create index if not exists weight_entries_couple_id_idx on public.weight_entries (couple_id);
create index if not exists weight_entries_created_by_idx on public.weight_entries (created_by);
create index if not exists shopping_items_couple_id_idx on public.shopping_items (couple_id);
create index if not exists shopping_items_created_by_idx on public.shopping_items (created_by);
create index if not exists shopping_catalog_created_by_idx on public.shopping_catalog (created_by);
create index if not exists task_items_assigned_to_idx on public.task_items (assigned_to);
create index if not exists task_items_created_by_idx on public.task_items (created_by);
create index if not exists meal_plan_updated_by_idx on public.meal_plan (updated_by);
create index if not exists meal_logs_couple_id_idx on public.meal_logs (couple_id);
create index if not exists meal_logs_created_by_idx on public.meal_logs (created_by);
create index if not exists couple_members_user_id_idx on public.couple_members (user_id);

-- 3. The shared timestamp trigger does not depend on the caller's search_path.
alter function public.update_updated_at_column() set search_path = '';

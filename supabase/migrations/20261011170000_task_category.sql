-- Task category: work shift, appointment, or personal. Applied to project iewlhdcinmktrzepjstc.
alter table public.task_items
  add column category text check (category in ('work', 'appointment', 'personal'));

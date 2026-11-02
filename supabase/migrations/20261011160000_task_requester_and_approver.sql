-- Free-text "who asked" and "who approved" for a task. Applied to project iewlhdcinmktrzepjstc.
alter table public.task_items
  add column requested_by text check (length(requested_by) <= 60),
  add column approved_by text check (length(approved_by) <= 60);

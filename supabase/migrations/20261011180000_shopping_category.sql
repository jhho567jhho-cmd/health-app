-- Shopping item category, so a custom item sits under the category the user picked. Applied to project iewlhdcinmktrzepjstc.
alter table public.shopping_items add column category text check (length(category) <= 60);

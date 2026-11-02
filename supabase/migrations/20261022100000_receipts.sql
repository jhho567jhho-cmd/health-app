-- Receipts: a private storage bucket for the photos, plus one row per receipt shared by both partners. Applied to project iewlhdcinmktrzepjstc.
insert into storage.buckets (id, name, public) values ('receipts', 'receipts', false) on conflict (id) do nothing;

create table public.receipts (
  id uuid primary key default gen_random_uuid(),
  couple_id uuid not null references public.couples(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  amount numeric(10,2) check (amount >= 0 and amount < 100000),
  receipt_date date not null,
  note text check (length(note) <= 200),
  file_path text not null check (length(file_path) <= 300),
  created_at timestamptz not null default now()
);

alter table public.receipts enable row level security;

create policy "members read receipts" on public.receipts for select
  using (public.is_couple_member(couple_id));

create policy "members add own receipts" on public.receipts for insert
  with check (public.is_couple_member(couple_id) and user_id = auth.uid());

create policy "members delete own receipts" on public.receipts for delete
  using (user_id = auth.uid());

create policy "couple reads receipt files" on storage.objects for select
  using (bucket_id = 'receipts' and public.is_couple_member(((storage.foldername(name))[1])::uuid));

create policy "couple uploads receipt files" on storage.objects for insert
  with check (bucket_id = 'receipts' and public.is_couple_member(((storage.foldername(name))[1])::uuid) and owner = auth.uid());

create policy "owner deletes receipt files" on storage.objects for delete
  using (bucket_id = 'receipts' and owner = auth.uid());

alter publication supabase_realtime add table public.receipts;

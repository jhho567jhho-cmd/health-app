-- סכמת מסד הנתונים של דרופשיפינג משותף.
-- מריצים פעם אחת ב-Supabase: SQL Editor -> New query -> Run.

create table if not exists public.products (
  id               uuid primary key default gen_random_uuid(),
  name             text not null,
  source_url       text,
  supplier         text,                       -- AliExpress / eBay / אחר
  cost             numeric(10,2) not null default 0,  -- מחיר ספק (כולל משלוח מהספק)
  sale_price       numeric(10,2) not null default 0,  -- מחיר מכירה ללקוח
  platform_fee_pct numeric(5,2)  not null default 0,  -- עמלת פלטפורמה באחוזים
  status           text not null default 'idea'
                   check (status in ('idea', 'checking', 'listed', 'sold', 'dropped')),
  notes            text,
  created_by       uuid references auth.users (id) default auth.uid(),
  created_at       timestamptz not null default now(),
  updated_at       timestamptz not null default now()
);

create table if not exists public.orders (
  id               uuid primary key default gen_random_uuid(),
  product_id       uuid references public.products (id) on delete set null,
  product_name     text not null,
  sale_price       numeric(10,2) not null default 0,  -- כמה שילם הלקוח
  cost             numeric(10,2) not null default 0,  -- כמה שילמנו לספק (כולל משלוח)
  platform_fee_pct numeric(5,2)  not null default 0,
  status           text not null default 'ordered'
                   check (status in ('ordered', 'shipped', 'delivered', 'returned', 'cancelled')),
  supplier_order_id text,
  tracking_number  text,
  ordered_at       date not null default current_date,
  notes            text,
  created_by       uuid references auth.users (id) default auth.uid(),
  created_at       timestamptz not null default now()
);

-- רק משתמשים מחוברים (שניכם) יכולים לקרוא ולכתוב.
alter table public.products enable row level security;
alter table public.orders   enable row level security;

drop policy if exists "shared access products" on public.products;
create policy "shared access products" on public.products
  for all to authenticated using (true) with check (true);

drop policy if exists "shared access orders" on public.orders;
create policy "shared access orders" on public.orders
  for all to authenticated using (true) with check (true);

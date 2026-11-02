-- Fuel entries can be a photo of the station screen with no typed amount. The photo lives in the private receipts bucket.
alter table public.fuel_logs alter column amount drop not null;
alter table public.fuel_logs add column photo_path text check (length(photo_path) <= 300);
alter table public.fuel_logs add constraint fuel_logs_amount_or_photo check (amount is not null or photo_path is not null);

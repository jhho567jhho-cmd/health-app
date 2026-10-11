-- NOT YET APPLIED. Run in the Supabase SQL Editor for project iewlhdcinmktrzepjstc.
-- Security advisor: is_couple_member is SECURITY DEFINER and callable without signing in.
-- Signed-in users still need EXECUTE because the RLS policies call it.
revoke execute on function public.is_couple_member(uuid) from public, anon;
grant execute on function public.is_couple_member(uuid) to authenticated;

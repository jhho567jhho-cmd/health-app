# Health App - Project Notes

## Team / People
- **Developer**: Chaim (חיים)
- **Partner**: Devorah (דבורה) - Chaim's wife

## Scope
- The app tracks **general health and fitness** and runs the household day: water, meals and calories, weight, photos, tasks with due dates and owner, a calendar of tasks, and a shared shopping list.
- **Not in scope:** fertility or cycle tracking. Do not add it, and do not use the word "פוריות" for this app.

## Product Principles
- The home screen shows everything the user needs for today, with no scrolling for the essentials.
- Adding data takes as few taps as possible (quick-add buttons, bottom sheets).
- Both partners see the same data once shared storage is connected.

## Project Status
- Repository: `jhho567jhho-cmd/health-app`
- Working branch: `claude/project-summary-5jpnkw`
- Live: https://health-app-web-umber.vercel.app/ (Vercel project `health-app-web`, deployed from this branch)
- Data: Supabase project `iewlhdcinmktrzepjstc`. Tasks, shopping, water, weight and meals sync between both partners; photos and tips stay on each device.
- Sign-in: email + password. Only emails in `public.allowed_members` can join (see `supabase/migrations`). Personal emails are not stored in the repo.
- Schema changes: keep every change as a file in `supabase/migrations/`. The connector's `apply_migration` has worked, but was cancelled in some sessions; if so, the SQL is run in the Supabase SQL Editor.
- `vendor/supabase.js` is supabase-js 2.45.4 (UMD), bundled so the app does not depend on a CDN.

## Important Context
This is a collaborative project between Chaim and his wife Devorah. When working on features, consider both of their perspectives and needs.

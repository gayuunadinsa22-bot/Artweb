# Gayuu — Setup & Deployment

This is a Next.js App Router storefront (TypeScript + Tailwind v4 + Framer Motion) for "Gayuu ♡". It works without Supabase — falling back to built-in demo content — and upgrades to a Supabase-backed admin/dashboard + orders when configured.

## Quick start (local, no Supabase)
1. Install dependencies: `npm i`
2. Run dev: `npm run dev` — open http://localhost:3000
3. Everything (storefront, gallery, shop, commissions) works with the included demo artworks/settings.

## Supabase setup (required for admin + order storage)
1. Create a project at [supabase.com](https://supabase.com).
2. Copy `.env.example` to `.env.local` and fill:
   - `NEXT_PUBLIC_SUPABASE_URL` — your project URL
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY` — anon/public key
   - `SUPABASE_SERVICE_ROLE_KEY` — service role key (server-only, never exposed to the browser)
   - `NEXT_PUBLIC_SITE_URL` — e.g. http://localhost:3000 or your live URL
3. Apply database schema + RLS + storage policies: run the SQL in `supabase/migrations/` in the Supabase SQL editor, in order:
   `20240101000001_initial_schema.sql`, `20240101000002_rls_policies.sql`, `20240101000003_storage.sql`, `20240101000004_homepage_images.sql`, `20240101000005_site_media_bucket.sql`, `20240101000006_about_images.sql`.
   The last three are additive and non-destructive (new nullable columns + the `site-media` bucket). If you skip them, the homepage/About editors still save their text but cannot save uploaded images.
4. Seed local content (artworks, settings, homepage, about, testimonials): run `npx ts-node scripts/seed.ts` (uses the service-role key; non-destructive).
5. Create an admin user: go to Authentication → Users → Add user (email+password). Then in Table Editor → `admin_roles`, insert a row `{ user_id: <new-user-uuid>, role: 'admin' }` (find the UUID from the Users table). Only allow-listed admins can access `/admin`.
6. Start dev: `npm run dev`. Visit `/admin/login` and sign in.
7. Upload artwork images: the `artwork-images` bucket is public-read; uploads go through the admin UI (RLS only allows admins to write).

## Admin dashboard
- Routes live under `/admin/*` (`/admin`, `/admin/artworks`, `/admin/gallery`, `/admin/homepage`, `/admin/about`, `/admin/commissions`, `/admin/testimonials`, `/admin/settings`, `/admin/account`, `/admin/orders`, `/admin/login`).
- Responsive sidebar (Dashboard, Artworks, Gallery, Homepage, About Artist, Commissions, Orders, Testimonials, Site Settings, Account Settings, View Website, Logout).
- Sold originals are not purchasable (availability `sold`).
- Order inquiries are stored in Supabase with statuses `new`, `contacted`, `confirmed`, `completed`, `cancelled`; checkout opens WhatsApp only after a successful save to the database (or falls back honestly if Supabase isn't configured).

## Build & verify
- Type-check: `npx tsc --noEmit`
- Lint: `npx eslint .`
- Build: `npm run build`

If Supabase isn't configured, `npm run build` still succeeds and the site uses built-in content. The build doesn't claim to test live Supabase integration — only that the code compiles and routes are valid.

## Admin edits not showing on the public site
- The storefront reads settings/homepage/About through cached functions tagged `settings`, `homepage` and `about`. Every admin save calls `revalidateStorefront()` (in `src/lib/admin/actions.ts`), which expires those tags with `updateTag` and revalidates the root layout. No redeploy or restart is needed.
- Server Components read the shared `siteSettings` singleton. `getSiteSettings()` applies the database values before returning, so the footer/navbar/metadata see them during the same server render.
- If text saves but images do not, the image columns are missing — apply `20240101000004_homepage_images.sql` / `20240101000006_about_images.sql` and save again. The admin toast names the exact file to run.
- If image uploads fail with a bucket error, apply `20240101000005_site_media_bucket.sql`.

## Notes
- Brand name: "Gayuu ♡". Artist name remains editable (fictional placeholder by default).
- Security: no service-role key in browser, only one authorized admin via `admin_roles`, RLS on every table, server-side auth checks where applicable.
- Non-destructive seeding: the seed script upserts by unique keys and never deletes data.
- Order IDs are client-generated (`AM-XXXX-YYYY`) for readability; the DB stores both `order_id` (unique) and internal `id` (UUID).
- Rate limit (in-memory): orders endpoint limits 5 attempts per IP per 10 minutes (single-instance only).

# Backend production setup

## Required environment

- `APP_ENV=production`
- `DATABASE_URL` — PostgreSQL connection URL (for example, the Supabase **direct** or pooler connection URL). PostgreSQL URLs using `postgres://` or `postgresql://` are normalized to the `psycopg` driver; psycopg's automatic prepared statements are disabled for transaction-pooler compatibility.
- `SUPABASE_URL` — the project URL, such as `https://<project-ref>.supabase.co`. Access tokens are verified against the project issuer, `authenticated` audience, expiry, signed-in role, and Supabase signing keys.
- `SUPABASE_JWT_SECRET` — only when the Supabase project still signs tokens with HS256. For asymmetric Supabase signing keys (ES256/RS256), the backend obtains and caches the project's JWKS; do not use the Supabase service-role key as a JWT secret.
- `FRONTEND_ORIGINS` — comma-separated trusted browser origins if different from the localhost development defaults.

The health endpoint is public. Every other API endpoint requires a valid Supabase user access token (`Authorization: Bearer ...`). The API stores the token subject on each workspace and only returns or mutates resources associated with that subject. Missing/invalid auth or missing production configuration never falls back to anonymous access.

For PostgreSQL requests the API switches each transaction to the `authenticated`
database role and sets the verified user claim. The initializer grants that
role the required table privileges and installs row-level policies, providing
a database-enforced ownership boundary in addition to the API's explicit owner
checks.

## New production database

1. Configure the environment variables above in the hosting provider; do not commit credentials.
2. From `backend`, run `python -m app.init_db` once against the new Supabase PostgreSQL database before serving traffic. This creates the current schema and enables owner-based row-level security policies on every data table. Production application startup does not create or alter tables. Run it with the database owner/administrative connection.
3. Configure the host to serve `app.main:app` (for example, with Uvicorn). Vercel deployments must provide a PostgreSQL `DATABASE_URL`; local SQLite is intentionally rejected when `VERCEL=1`.

Local development defaults to `sqlite:///./flowpilot.local.db`. This is a separate, local-only database; it does not implicitly import the old unauthenticated `flowpilot.db`.

## Existing legacy database

`create_all` does not migrate an existing schema. Back up the database first. For a legacy PostgreSQL database, choose the Supabase user UUID that will own **all** existing workspaces, then run the migration in `migrations/001_owner_scoped_workspaces_postgresql.sql` with that ID set on the same connection. The migration adds ownership and RLS policies for all resource tables. For example, using `psql`:

```text
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -v owner_id=SUPABASE_USER_UUID \
  -f migrations/001_owner_scoped_workspaces_postgresql.sql
```

In the example, replace `SUPABASE_USER_UUID` with the intended Supabase user's UUID (do not put it in source control). The migration deliberately fails if no owner is set. It assigns every legacy workspace and its dependent projects, tasks, workflows, and runs to that one user. If records belong to multiple users, do not run this migration as-is: perform a reviewed, owner-mapped migration before enabling the API. For legacy SQLite files, export/map records into a fresh PostgreSQL schema; this backend does not automatically infer ownership or migrate SQLite data.

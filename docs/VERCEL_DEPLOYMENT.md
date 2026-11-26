# Vercel production deployment

FlowPilot uses two Vercel projects from this monorepo: a Next.js frontend and a
FastAPI backend. Supabase provides authentication and PostgreSQL. No API route
is anonymous except the health check.

## 1. Configure Supabase

Create a Supabase project and keep its database password private. In
**Authentication → URL Configuration**, set the site URL to the frontend's
production domain after Vercel assigns it. Enable email confirmation if
appropriate for your account policy.

Run the schema setup once from `backend/` using a secure administrative
connection:

```bash
python -m pip install -r requirements.txt
python -m app.init_db
```

The database initializer creates the tables and owner-scoped policies. Do not
run the legacy migration against an empty database. If migrating an existing
database, follow [backend/DEPLOYMENT.md](../backend/DEPLOYMENT.md) and review
the ownership mapping first.

## 2. Deploy the API

Import `furqan-git-cloud/flowpilot-ai` as a Vercel project and set its **Root
Directory** to `backend`. Let Vercel detect the Python runtime and install
`backend/requirements.txt`. Add these Production environment variables in the
Vercel project settings:

- `APP_ENV=production`
- `DATABASE_URL` — Supabase PostgreSQL connection URL. Prefer the Supavisor
  transaction pooler URL when deploying serverless functions.
- `SUPABASE_URL` — the Supabase project URL.
- `SUPABASE_JWT_SECRET` — only if the Supabase project still uses HS256 signing.
  Leave unset when using asymmetric signing keys; the API fetches the public
  JWKS instead.
- `FRONTEND_ORIGINS` — the exact frontend production origin, for example
  `https://flowpilot-ai.vercel.app` (no trailing slash).

Do not add Supabase service-role keys or database passwords to frontend
variables, source files, or this repository. After deployment, verify
`https://<api-domain>/api/v1/health` returns `{"status":"ok",...}`.

## 3. Deploy the frontend

Create a second Vercel project from the same Git repository and set its **Root
Directory** to `frontend`. Configure these Production environment variables:

- `NEXT_PUBLIC_API_URL` — the deployed API origin, for example
  `https://flowpilot-api.vercel.app` (no trailing slash).
- `NEXT_PUBLIC_SUPABASE_URL` — the Supabase project URL.
- `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` — the Supabase publishable key. The
  legacy `NEXT_PUBLIC_SUPABASE_ANON_KEY` name is also supported.

Redeploy after changing environment variables. Add the resulting frontend
domain to both `FRONTEND_ORIGINS` in the API project and Supabase's allowed
redirect URLs. Keep preview deployments on separate preview environment
variables and an isolated database; do not point untrusted previews at
production customer data.

## 4. Verify before customer use

1. Sign up and confirm an account, then sign in.
2. Create a workspace and confirm it persists after reload.
3. Use a second account to verify it cannot list, read, or modify the first
   account's workspaces or resources.
4. Confirm expired/invalid tokens are rejected and sign-out clears the UI.
5. Test workflow runs, database backups, and a restore before entering sensitive
   customer data.

This deployment configuration is not itself a claim of completed production
certification. Do not enter sensitive customer data until provider settings,
account isolation, backups, and recovery have been verified in the deployed
environment.

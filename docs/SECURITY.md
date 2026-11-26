# Security status and remaining milestones

The API now verifies Supabase access tokens and applies owner checks to every
workspace, project, task, workflow, workflow run, and analytics request.
PostgreSQL schema initialization also enables owner-scoped row-level policies.
Local development uses SQLite and is not a production deployment.

Before entering sensitive customer data:

1. Configure the production Supabase and Vercel environment using
   [the deployment guide](VERCEL_DEPLOYMENT.md); keep database credentials and
   signing secrets server-side.
2. Verify account isolation with two independent accounts and confirm invalid
   and expired tokens are rejected in the deployed environment.
3. Configure and test automated PostgreSQL backups and a recovery procedure.
4. Configure monitoring, alerting, and rate limiting for the public API.
5. Review audit logging and applicable data-retention requirements.

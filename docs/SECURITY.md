# Security Milestones

This MVP is a local development implementation, not production-ready multi-user SaaS.
It currently has no authentication or workspace membership checks. Do not expose its API to the public internet or enter real customer information.

Before public launch:

1. Configure Supabase Auth and verify JWT signatures and claims on every private route.
2. Derive the current user from verified tokens, never from a browser-supplied user ID.
3. Enforce workspace membership and role checks in the backend.
4. Enable PostgreSQL RLS and test isolation with two independent accounts.
5. Rotate secrets, configure HTTPS/CORS, backups and monitoring.
6. Add rate limiting and audit logs.

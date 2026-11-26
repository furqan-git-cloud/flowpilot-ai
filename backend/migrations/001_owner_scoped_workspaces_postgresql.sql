-- Upgrade a legacy FlowPilot PostgreSQL schema. This intentionally refuses to
-- assign existing workspaces without an explicit Supabase user UUID.
SELECT set_config('flowpilot.migration_owner_id', :'owner_id', false);

BEGIN;

ALTER TABLE workspaces ADD COLUMN owner_id VARCHAR;

DO $$
DECLARE
    migration_owner_id TEXT;
    old_constraint RECORD;
BEGIN
    migration_owner_id := current_setting('flowpilot.migration_owner_id', true);
    IF migration_owner_id IS NULL OR btrim(migration_owner_id) = '' THEN
        RAISE EXCEPTION
            'Set flowpilot.migration_owner_id to the Supabase auth.users.id UUID before migrating';
    END IF;

    UPDATE workspaces SET owner_id = migration_owner_id;

    FOR old_constraint IN
        SELECT conname
        FROM pg_constraint
        WHERE conrelid = 'workspaces'::regclass
          AND contype = 'u'
          AND pg_get_constraintdef(oid) = 'UNIQUE (slug)'
    LOOP
        EXECUTE format('ALTER TABLE workspaces DROP CONSTRAINT %I', old_constraint.conname);
    END LOOP;
END
$$;

ALTER TABLE workspaces ALTER COLUMN owner_id SET NOT NULL;
CREATE INDEX ix_workspaces_owner_id ON workspaces (owner_id);
ALTER TABLE workspaces
    ADD CONSTRAINT uq_workspaces_owner_slug UNIQUE (owner_id, slug);

ALTER TABLE public.workspaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workflows ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workflow_runs ENABLE ROW LEVEL SECURITY;
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.workspaces TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.projects TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.tasks TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.workflows TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.workflow_runs TO authenticated;

CREATE POLICY flowpilot_owner_access ON public.workspaces
    FOR ALL USING (owner_id = (select auth.uid())::text)
    WITH CHECK (owner_id = (select auth.uid())::text);
CREATE POLICY flowpilot_owner_access ON public.projects
    FOR ALL USING (exists (
        select 1 from public.workspaces w
        where w.id = workspace_id and w.owner_id = (select auth.uid())::text
    ))
    WITH CHECK (exists (
        select 1 from public.workspaces w
        where w.id = workspace_id and w.owner_id = (select auth.uid())::text
    ));
CREATE POLICY flowpilot_owner_access ON public.tasks
    FOR ALL USING (exists (
        select 1 from public.workspaces w
        where w.id = workspace_id and w.owner_id = (select auth.uid())::text
    ))
    WITH CHECK (exists (
        select 1 from public.workspaces w
        where w.id = workspace_id and w.owner_id = (select auth.uid())::text
    ));
CREATE POLICY flowpilot_owner_access ON public.workflows
    FOR ALL USING (exists (
        select 1 from public.workspaces w
        where w.id = workspace_id and w.owner_id = (select auth.uid())::text
    ))
    WITH CHECK (exists (
        select 1 from public.workspaces w
        where w.id = workspace_id and w.owner_id = (select auth.uid())::text
    ));
CREATE POLICY flowpilot_owner_access ON public.workflow_runs
    FOR ALL USING (exists (
        select 1 from public.workspaces w
        where w.id = workspace_id and w.owner_id = (select auth.uid())::text
    ))
    WITH CHECK (exists (
        select 1 from public.workspaces w
        where w.id = workspace_id and w.owner_id = (select auth.uid())::text
    ));

COMMIT;

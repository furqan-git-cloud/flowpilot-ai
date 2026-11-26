from sqlalchemy import inspect, text

from .models import Base, engine


def enable_supabase_row_level_security():
    policies = {
        "workspaces": """
            owner_id = (select auth.uid())::text
        """,
        "projects": """
            exists (
                select 1 from public.workspaces w
                where w.id = workspace_id and w.owner_id = (select auth.uid())::text
            )
        """,
        "tasks": """
            exists (
                select 1 from public.workspaces w
                where w.id = workspace_id and w.owner_id = (select auth.uid())::text
            )
        """,
        "workflows": """
            exists (
                select 1 from public.workspaces w
                where w.id = workspace_id and w.owner_id = (select auth.uid())::text
            )
        """,
        "workflow_runs": """
            exists (
                select 1 from public.workspaces w
                where w.id = workspace_id and w.owner_id = (select auth.uid())::text
            )
        """,
    }
    with engine.begin() as connection:
        connection.execute(text("GRANT USAGE ON SCHEMA public TO authenticated"))
        for table_name, ownership_check in policies.items():
            connection.execute(text(f"ALTER TABLE public.{table_name} ENABLE ROW LEVEL SECURITY"))
            connection.execute(text(
                f"GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.{table_name} TO authenticated"
            ))
            connection.execute(text(f"DROP POLICY IF EXISTS flowpilot_owner_access ON public.{table_name}"))
            connection.execute(text(
                f"CREATE POLICY flowpilot_owner_access ON public.{table_name} "
                f"FOR ALL USING ({ownership_check}) WITH CHECK ({ownership_check})"
            ))


def main():
    Base.metadata.create_all(bind=engine)
    inspector = inspect(engine)
    missing_owner_columns = [
        table_name
        for table_name in ("workspaces",)
        if table_name in inspector.get_table_names()
        and "owner_id" not in {column["name"] for column in inspector.get_columns(table_name)}
    ]
    if missing_owner_columns:
        raise RuntimeError(
            "Existing database schema is missing ownership columns. Apply "
            "migrations/001_owner_scoped_workspaces_postgresql.sql before initializing."
        )
    if engine.dialect.name == "postgresql":
        enable_supabase_row_level_security()
    print("FlowPilot database schema is ready.")


if __name__ == "__main__":
    main()

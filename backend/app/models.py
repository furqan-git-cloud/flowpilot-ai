import os
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, UniqueConstraint, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


def _database_url():
    app_env = os.getenv("APP_ENV", "").lower()
    production = app_env == "production" or os.getenv("VERCEL") == "1"
    database_url = os.getenv("DATABASE_URL")
    if production and not database_url:
        raise RuntimeError("DATABASE_URL must be configured in production")
    if not database_url:
        database_url = "sqlite:///./flowpilot.local.db"
    if database_url.startswith("postgres://"):
        database_url = "postgresql+psycopg://" + database_url[len("postgres://"):]
    elif database_url.startswith("postgresql://"):
        database_url = "postgresql+psycopg://" + database_url[len("postgresql://"):]
    if production and not database_url.startswith("postgresql+psycopg://"):
        raise RuntimeError("Production requires a PostgreSQL DATABASE_URL")
    return database_url


DATABASE_URL = _database_url()
engine_options = {"pool_pre_ping": True}
if DATABASE_URL.startswith("sqlite:"):
    engine_options["connect_args"] = {"check_same_thread": False}
elif DATABASE_URL.startswith("postgresql+psycopg://"):
    engine_options["connect_args"] = {"prepare_threshold": 0}
engine = create_engine(DATABASE_URL, **engine_options)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def uid():
    return str(uuid4())


class Workspace(Base):
    __tablename__ = "workspaces"
    __table_args__ = (UniqueConstraint("owner_id", "slug", name="uq_workspaces_owner_slug"),)
    id = Column(String, primary_key=True, default=uid)
    owner_id = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Project(Base):
    __tablename__ = "projects"
    id = Column(String, primary_key=True, default=uid)
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, default="")
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)


class Task(Base):
    __tablename__ = "tasks"
    id = Column(String, primary_key=True, default=uid)
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False)
    project_id = Column(String, nullable=True)
    title = Column(String, nullable=False)
    status = Column(String, default="todo")
    priority = Column(String, default="medium")
    due_date = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Workflow(Base):
    __tablename__ = "workflows"
    id = Column(String, primary_key=True, default=uid)
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False)
    name = Column(String, nullable=False)
    status = Column(String, default="draft")
    definition = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"
    id = Column(String, primary_key=True, default=uid)
    workflow_id = Column(String, ForeignKey("workflows.id"), nullable=False)
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False)
    status = Column(String, default="queued")
    output = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

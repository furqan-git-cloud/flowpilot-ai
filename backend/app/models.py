from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from uuid import uuid4

DATABASE_URL = "sqlite:///./flowpilot.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def uid():
    return str(uuid4())


class Workspace(Base):
    __tablename__ = "workspaces"
    id = Column(String, primary_key=True, default=uid)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False)
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

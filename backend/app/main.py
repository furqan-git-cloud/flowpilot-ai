from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
import json
import os
import re

from .models import Base, engine, SessionLocal, Workspace, Project, Task, Workflow, WorkflowRun
from .schemas import (WorkspaceCreate, ProjectCreate, ProjectUpdate, TaskCreate, TaskUpdate,
                      WorkflowCreate, WorkflowUpdate, WorkflowStep, WorkflowRunRequest, PromptRequest)

Base.metadata.create_all(bind=engine)
app = FastAPI(title="FlowPilot AI API", version="0.1.0")
frontend_origins = os.getenv("FRONTEND_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
app.add_middleware(CORSMiddleware, allow_origins=[origin.strip() for origin in frontend_origins.split(",") if origin.strip()], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def slugify(value: str):
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "workspace"


@app.get("/api/v1/health")
def health():
    return {"status": "ok", "service": "flowpilot-ai"}


@app.get("/api/v1/workspaces")
def list_workspaces(db: Session = Depends(get_db)):
    return db.query(Workspace).all()


@app.post("/api/v1/workspaces", status_code=201)
def create_workspace(body: WorkspaceCreate, db: Session = Depends(get_db)):
    workspace = Workspace(name=body.name, slug=slugify(body.name))
    db.add(workspace)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(409, "A workspace with this name already exists") from error
    db.refresh(workspace)
    return workspace


@app.get("/api/v1/projects")
def list_projects(workspace_id: str = Query(...), db: Session = Depends(get_db)):
    return db.query(Project).filter(Project.workspace_id == workspace_id).all()


@app.post("/api/v1/projects", status_code=201)
def create_project(body: ProjectCreate, db: Session = Depends(get_db)):
    if not db.get(Workspace, body.workspace_id):
        raise HTTPException(404, "Workspace not found")
    item = Project(workspace_id=body.workspace_id, name=body.name, description=body.description)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.patch("/api/v1/projects/{item_id}")
def update_project(item_id: str, body: ProjectUpdate, db: Session = Depends(get_db)):
    item = db.get(Project, item_id)
    if not item:
        raise HTTPException(404, "Project not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@app.get("/api/v1/tasks")
def list_tasks(workspace_id: str = Query(...), db: Session = Depends(get_db)):
    return db.query(Task).filter(Task.workspace_id == workspace_id).all()


@app.post("/api/v1/tasks", status_code=201)
def create_task(body: TaskCreate, db: Session = Depends(get_db)):
    if not db.get(Workspace, body.workspace_id):
        raise HTTPException(404, "Workspace not found")
    if body.project_id:
        project = db.get(Project, body.project_id)
        if not project or project.workspace_id != body.workspace_id:
            raise HTTPException(400, "Project must belong to the selected workspace")
    item = Task(workspace_id=body.workspace_id, project_id=body.project_id, title=body.title,
                priority=body.priority, due_date=body.due_date)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.patch("/api/v1/tasks/{item_id}")
def update_task(item_id: str, body: TaskUpdate, db: Session = Depends(get_db)):
    item = db.get(Task, item_id)
    if not item:
        raise HTTPException(404, "Task not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@app.post("/api/v1/ai/generate")
def generate_workflow(body: PromptRequest):
    prompt = body.prompt.lower()
    if "customer" in prompt or "follow" in prompt:
        name = "Customer follow-up"
        titles = ["Review customer context", "Contact the customer", "Record the follow-up outcome"]
    elif "sales" in prompt:
        name = "Sales lead review"
        titles = ["Review new sales lead", "Qualify the opportunity", "Schedule the next sales action"]
    else:
        name = "Process review"
        titles = ["Review the process", "Identify the next action", "Record the outcome"]
    steps = [
        {"id": f"step_{index}", "action": "create_task", "title": title,
         "priority": "medium", "max_retries": 1}
        for index, title in enumerate(titles, start=1)
    ]
    return {"name": name, "steps": steps, "generated_by": "template"}


@app.get("/api/v1/workflows")
def list_workflows(workspace_id: str = Query(...), db: Session = Depends(get_db)):
    return db.query(Workflow).filter(Workflow.workspace_id == workspace_id).all()


@app.post("/api/v1/workflows", status_code=201)
def create_workflow(body: WorkflowCreate, db: Session = Depends(get_db)):
    if not db.get(Workspace, body.workspace_id):
        raise HTTPException(404, "Workspace not found")
    validate_workflow_projects(body.steps, body.workspace_id, db)
    item = Workflow(workspace_id=body.workspace_id, name=body.name,
                    status="active",
                    definition=json.dumps({"steps": [step.model_dump() for step in body.steps]}))
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def validate_workflow_projects(steps: list[WorkflowStep], workspace_id: str, db: Session):
    for step in steps:
        if step.project_id:
            project = db.get(Project, step.project_id)
            if not project or project.workspace_id != workspace_id:
                raise HTTPException(400, "Workflow projects must belong to the selected workspace")


@app.patch("/api/v1/workflows/{workflow_id}")
def update_workflow(workflow_id: str, body: WorkflowUpdate, db: Session = Depends(get_db)):
    workflow = db.get(Workflow, workflow_id)
    if not workflow:
        raise HTTPException(404, "Workflow not found")
    validate_workflow_projects(body.steps, workflow.workspace_id, db)
    workflow.name = body.name
    workflow.definition = json.dumps({"steps": [step.model_dump() for step in body.steps]})
    db.commit()
    db.refresh(workflow)
    return workflow


@app.post("/api/v1/workflows/{workflow_id}/run", status_code=201)
def run_workflow(workflow_id: str, body: WorkflowRunRequest = WorkflowRunRequest(),
                 db: Session = Depends(get_db)):
    workflow = db.get(Workflow, workflow_id)
    if not workflow:
        raise HTTPException(404, "Workflow not found")
    try:
        definition = json.loads(workflow.definition)
        steps = [WorkflowStep.model_validate(step) for step in definition["steps"]]
    except (json.JSONDecodeError, KeyError, TypeError, ValidationError) as error:
        raise HTTPException(422, "Workflow definition is invalid") from error
    run = WorkflowRun(workflow_id=workflow_id, workspace_id=workflow.workspace_id,
                      status="running", output=json.dumps({"priority": body.priority, "steps": []}))
    db.add(run)
    db.commit()
    db.refresh(run)
    results = []

    for step in steps:
        if step.condition:
            matches = body.priority == step.condition.value
            if step.condition.operator == "not_equals":
                matches = not matches
            if not matches:
                results.append({"step_id": step.id, "title": step.title, "status": "skipped",
                                "attempts": 0, "task_id": None})
                run.output = json.dumps({"priority": body.priority, "steps": results})
                db.commit()
                continue

        task = None
        last_error = None
        attempts = 0
        for attempts in range(1, step.max_retries + 2):
            try:
                with db.begin_nested():
                    task = Task(workspace_id=workflow.workspace_id, project_id=step.project_id,
                                title=step.title, priority=step.priority)
                    db.add(task)
                    db.flush()
                last_error = None
                break
            except SQLAlchemyError as error:
                last_error = error

        if last_error:
            results.append({"step_id": step.id, "title": step.title, "status": "failed",
                            "attempts": attempts, "task_id": None,
                            "error": f"Task creation failed ({type(last_error).__name__})"})
            run.status = "failed"
            run.output = json.dumps({"priority": body.priority, "steps": results})
            db.commit()
            return run

        results.append({"step_id": step.id, "title": step.title, "status": "succeeded",
                        "attempts": attempts, "task_id": task.id if task else None})
        run.output = json.dumps({"priority": body.priority, "steps": results})
        db.commit()

    run.status = "succeeded"
    run.output = json.dumps({"priority": body.priority, "steps": results})
    db.commit()
    db.refresh(run)
    return run


@app.get("/api/v1/workflows/{workflow_id}/runs")
def workflow_runs(workflow_id: str, db: Session = Depends(get_db)):
    if not db.get(Workflow, workflow_id):
        raise HTTPException(404, "Workflow not found")
    return db.query(WorkflowRun).filter(WorkflowRun.workflow_id == workflow_id).order_by(
        WorkflowRun.created_at.desc()
    ).all()


@app.get("/api/v1/analytics/overview")
def analytics(workspace_id: str = Query(...), db: Session = Depends(get_db)):
    return {
        "projects": db.query(Project).filter(Project.workspace_id == workspace_id).count(),
        "tasks": db.query(Task).filter(Task.workspace_id == workspace_id).count(),
        "workflows": db.query(Workflow).filter(Workflow.workspace_id == workspace_id).count(),
        "completed_tasks": db.query(Task).filter(Task.workspace_id == workspace_id, Task.status == "done").count(),
    }

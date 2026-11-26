from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class InputModel(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


class WorkspaceCreate(InputModel):
    name: str = Field(min_length=2, max_length=100)


class ProjectCreate(InputModel):
    workspace_id: str
    name: str = Field(min_length=2, max_length=100)
    description: str = Field(default="", max_length=2000)


class ProjectUpdate(InputModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=2000)
    status: Literal["active", "archived"] | None = None


class TaskCreate(InputModel):
    workspace_id: str
    title: str = Field(min_length=1, max_length=200)
    project_id: str | None = None
    priority: Literal["low", "medium", "high"] = "medium"
    due_date: str | None = Field(default=None, max_length=40)


class TaskUpdate(InputModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    status: Literal["todo", "in_progress", "done"] | None = None
    priority: Literal["low", "medium", "high"] | None = None
    due_date: str | None = Field(default=None, max_length=40)


class WorkflowCondition(InputModel):
    field: Literal["run_priority"]
    operator: Literal["equals", "not_equals"] = "equals"
    value: Literal["low", "medium", "high"]


class WorkflowStep(InputModel):
    id: str = Field(default_factory=lambda: str(uuid4()), min_length=1, max_length=64)
    action: Literal["create_task"]
    title: str = Field(min_length=1, max_length=200)
    priority: Literal["low", "medium", "high"] = "medium"
    project_id: str | None = None
    max_retries: int = Field(default=0, ge=0, le=3)
    condition: WorkflowCondition | None = None


class WorkflowCreate(InputModel):
    workspace_id: str
    name: str = Field(min_length=2, max_length=100)
    steps: list[WorkflowStep] = Field(min_length=1, max_length=20)


class WorkflowUpdate(InputModel):
    name: str = Field(min_length=2, max_length=100)
    steps: list[WorkflowStep] = Field(min_length=1, max_length=20)


class WorkflowRunRequest(InputModel):
    priority: Literal["low", "medium", "high"] = "medium"


class PromptRequest(InputModel):
    prompt: str = Field(min_length=3, max_length=1000)

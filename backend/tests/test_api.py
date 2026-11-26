import json

from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_workspaces_and_projects():
    name = f"Acme {uuid4().hex[:8]}"
    response = client.post("/api/v1/workspaces", json={"name": name})
    assert response.status_code == 201
    workspace = response.json()
    assert workspace["slug"]

    project_response = client.post("/api/v1/projects", json={"workspace_id": workspace["id"], "name": "Launch"})
    assert project_response.status_code == 201
    project = project_response.json()
    assert project["name"] == "Launch"

    duplicate = client.post("/api/v1/workspaces", json={"name": name})
    assert duplicate.status_code == 409


def test_task_validation_and_workspace_isolation():
    first = client.post("/api/v1/workspaces", json={"name": f"First Team {uuid4().hex[:8]}"}).json()
    second = client.post("/api/v1/workspaces", json={"name": f"Second Team {uuid4().hex[:8]}"}).json()
    project = client.post(
        "/api/v1/projects",
        json={"workspace_id": first["id"], "name": "Private project"},
    ).json()

    mismatched_project = client.post(
        "/api/v1/tasks",
        json={
            "workspace_id": second["id"],
            "project_id": project["id"],
            "title": "Should not cross workspaces",
        },
    )
    assert mismatched_project.status_code == 400

    invalid_priority = client.post(
        "/api/v1/tasks",
        json={"workspace_id": first["id"], "title": "Invalid priority", "priority": "urgent"},
    )
    assert invalid_priority.status_code == 422


def test_workflow_action_is_allowlisted():
    workspace = client.post("/api/v1/workspaces", json={"name": f"Workflow Team {uuid4().hex[:8]}"}).json()
    response = client.post(
        "/api/v1/workflows",
        json={
            "workspace_id": workspace["id"],
            "name": "Unsafe workflow",
            "steps": [{"action": "execute_code", "title": "Do something"}],
        },
    )
    assert response.status_code == 422


def test_workflow_run_creates_tasks_and_can_be_reused():
    workspace = client.post("/api/v1/workspaces", json={"name": f"Run Team {uuid4().hex[:8]}"}).json()
    workflow = client.post(
        "/api/v1/workflows",
        json={
            "workspace_id": workspace["id"],
            "name": "Follow-up workflow",
            "steps": [
                {"action": "create_task", "title": "Review customer", "priority": "high", "max_retries": 1},
                {
                    "action": "create_task",
                    "title": "Escalate high priority",
                    "condition": {"field": "run_priority", "operator": "equals", "value": "high"},
                },
            ],
        },
    ).json()

    run = client.post(f"/api/v1/workflows/{workflow['id']}/run", json={"priority": "medium"})
    assert run.status_code == 201
    assert run.json()["status"] == "succeeded"
    output = json.loads(run.json()["output"])
    assert [step["status"] for step in output["steps"]] == ["succeeded", "skipped"]
    tasks = client.get(f"/api/v1/tasks?workspace_id={workspace['id']}").json()
    assert [task["title"] for task in tasks] == ["Review customer"]
    assert tasks[0]["priority"] == "high"

    second_run = client.post(f"/api/v1/workflows/{workflow['id']}/run", json={"priority": "high"})
    assert second_run.status_code == 201
    assert second_run.json()["status"] == "succeeded"
    history = client.get(f"/api/v1/workflows/{workflow['id']}/runs")
    assert history.status_code == 200
    assert len(history.json()) == 2
    assert len(client.get(f"/api/v1/tasks?workspace_id={workspace['id']}").json()) == 3


def test_workflow_retries_are_bounded():
    workspace = client.post("/api/v1/workspaces", json={"name": f"Retry Team {uuid4().hex[:8]}"}).json()
    response = client.post(
        "/api/v1/workflows",
        json={
            "workspace_id": workspace["id"],
            "name": "Invalid retries",
            "steps": [{"action": "create_task", "title": "Create task", "max_retries": 4}],
        },
    )
    assert response.status_code == 422


def test_workflow_update_and_project_assignment():
    workspace = client.post("/api/v1/workspaces", json={"name": f"Project Workflow {uuid4().hex[:8]}"}).json()
    project = client.post(
        "/api/v1/projects",
        json={"workspace_id": workspace["id"], "name": "Customer success"},
    ).json()
    workflow = client.post(
        "/api/v1/workflows",
        json={
            "workspace_id": workspace["id"],
            "name": "Initial workflow",
            "steps": [{"action": "create_task", "title": "Initial task"}],
        },
    ).json()

    updated = client.patch(
        f"/api/v1/workflows/{workflow['id']}",
        json={
            "name": "Customer onboarding",
            "steps": [{
                "action": "create_task",
                "title": "Prepare onboarding",
                "project_id": project["id"],
                "condition": {"field": "run_priority", "operator": "not_equals", "value": "low"},
            }],
        },
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Customer onboarding"

    run = client.post(f"/api/v1/workflows/{workflow['id']}/run", json={"priority": "high"})
    assert run.status_code == 201
    tasks = client.get(f"/api/v1/tasks?workspace_id={workspace['id']}").json()
    assert tasks[0]["project_id"] == project["id"]
    assert tasks[0]["title"] == "Prepare onboarding"

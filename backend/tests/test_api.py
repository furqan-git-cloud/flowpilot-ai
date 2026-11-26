import base64
import json
import time
from uuid import uuid4

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth import get_current_user
from app.main import app, get_db, set_database_user_claim
from app.models import Base, _database_url


@pytest.fixture
def auth_user():
    return {"sub": str(uuid4()), "role": "authenticated"}


@pytest.fixture
def client(auth_user):
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=test_engine)
    test_session = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    def override_get_db():
        db = test_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: auth_user
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    test_engine.dispose()


@pytest.fixture
def raw_client(client):
    user_dependency = app.dependency_overrides.pop(get_current_user)
    try:
        yield client
    finally:
        app.dependency_overrides[get_current_user] = user_dependency


def test_health_is_public(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_all_non_health_routes_require_a_verified_bearer_token(raw_client, monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://unit-test.supabase.co")
    monkeypatch.setenv("SUPABASE_JWT_SECRET", "test-signing-secret-not-for-production")
    assert raw_client.get("/api/v1/workspaces").status_code == 401
    assert raw_client.post("/api/v1/ai/generate", json={"prompt": "make a task"}).status_code == 401

    now = int(time.time())
    valid_token = jwt.encode(
        {
            "sub": str(uuid4()),
            "role": "authenticated",
            "aud": "authenticated",
            "iss": "https://unit-test.supabase.co/auth/v1",
            "iat": now,
            "exp": now + 60,
        },
        "test-signing-secret-not-for-production",
        algorithm="HS256",
    )
    assert raw_client.get(
        "/api/v1/workspaces", headers={"Authorization": f"Bearer {valid_token}"}
    ).status_code == 200

    invalid_claims_token = jwt.encode(
        {
            "sub": str(uuid4()),
            "role": "authenticated",
            "is_anonymous": True,
            "aud": "authenticated",
            "iss": "https://unit-test.supabase.co/auth/v1",
            "iat": now,
            "exp": now + 60,
        },
        "test-signing-secret-not-for-production",
        algorithm="HS256",
    )
    assert raw_client.get(
        "/api/v1/workspaces", headers={"Authorization": f"Bearer {invalid_claims_token}"}
    ).status_code == 401


def test_asymmetric_supabase_jwks_token_is_verified(raw_client, monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://unit-test.supabase.co")
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_numbers = private_key.public_key().public_numbers()

    def base64url_integer(value):
        size = (value.bit_length() + 7) // 8
        return base64.urlsafe_b64encode(value.to_bytes(size, "big")).rstrip(b"=").decode()

    jwk = {
        "kty": "RSA",
        "kid": "unit-test-key",
        "use": "sig",
        "alg": "RS256",
        "n": base64url_integer(public_numbers.n),
        "e": base64url_integer(public_numbers.e),
    }
    monkeypatch.setattr("app.auth._jwks_for", lambda url: {"keys": [jwk]})
    now = int(time.time())
    token = jwt.encode(
        {
            "sub": str(uuid4()),
            "role": "authenticated",
            "aud": "authenticated",
            "iss": "https://unit-test.supabase.co/auth/v1",
            "iat": now,
            "exp": now + 60,
        },
        private_key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        ),
        algorithm="RS256",
        headers={"kid": "unit-test-key"},
    )
    response = raw_client.get("/api/v1/workspaces", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


def test_production_database_configuration_is_fail_closed(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("VERCEL", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(RuntimeError, match="DATABASE_URL"):
        _database_url()

    monkeypatch.setenv("DATABASE_URL", "sqlite:///./unsafe.db")
    with pytest.raises(RuntimeError, match="PostgreSQL"):
        _database_url()

    monkeypatch.setenv("DATABASE_URL", "postgresql://db.example/flowpilot")
    assert _database_url() == "postgresql+psycopg://db.example/flowpilot"


def test_postgres_transactions_use_authenticated_role_and_owner_claim():
    statements = []

    class Connection:
        dialect = type("Dialect", (), {"name": "postgresql"})()

        def execute(self, statement, parameters=None):
            statements.append((statement.text, parameters))

    session = type("SessionState", (), {"info": {"auth_user_id": str(uuid4())}})()
    set_database_user_claim(session, None, Connection())

    assert statements[0][0] == "SET LOCAL ROLE authenticated"
    assert "request.jwt.claim.sub" in statements[1][0]
    assert statements[1][1] == {"owner_id": session.info["auth_user_id"]}


def test_workspaces_and_projects(client):
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


def test_workspace_slugs_are_unique_per_owner(client, auth_user):
    first = client.post("/api/v1/workspaces", json={"name": "Same name"})
    auth_user["sub"] = str(uuid4())
    second = client.post("/api/v1/workspaces", json={"name": "Same name"})
    assert first.status_code == second.status_code == 201


def test_task_validation_and_workspace_isolation(client):
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


def test_workflow_action_is_allowlisted(client):
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


def test_workflow_run_creates_tasks_and_can_be_reused(client):
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


def test_workflow_retries_are_bounded(client):
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


def test_workflow_update_and_project_assignment(client):
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


def test_owner_scope_covers_every_resource_and_operation(client, auth_user):
    workspace = client.post("/api/v1/workspaces", json={"name": "Account A"}).json()
    project = client.post(
        "/api/v1/projects", json={"workspace_id": workspace["id"], "name": "Private project"}
    ).json()
    task = client.post(
        "/api/v1/tasks",
        json={"workspace_id": workspace["id"], "project_id": project["id"], "title": "Private task"},
    ).json()
    workflow = client.post(
        "/api/v1/workflows",
        json={
            "workspace_id": workspace["id"],
            "name": "Private workflow",
            "steps": [{"action": "create_task", "title": "Generated task"}],
        },
    ).json()
    assert client.post(f"/api/v1/workflows/{workflow['id']}/run").status_code == 201
    account_a = auth_user["sub"]

    auth_user["sub"] = str(uuid4())
    assert client.get("/api/v1/workspaces").json() == []
    assert client.get(f"/api/v1/projects?workspace_id={workspace['id']}").status_code == 404
    assert client.get(f"/api/v1/tasks?workspace_id={workspace['id']}").status_code == 404
    assert client.get(f"/api/v1/workflows?workspace_id={workspace['id']}").status_code == 404
    assert client.get(f"/api/v1/analytics/overview?workspace_id={workspace['id']}").status_code == 404
    assert client.patch(f"/api/v1/projects/{project['id']}", json={"name": "Stolen"}).status_code == 404
    assert client.patch(f"/api/v1/tasks/{task['id']}", json={"title": "Stolen"}).status_code == 404
    assert client.patch(
        f"/api/v1/workflows/{workflow['id']}",
        json={"name": "Stolen", "steps": [{"action": "create_task", "title": "Stolen"}]},
    ).status_code == 404
    assert client.post(f"/api/v1/workflows/{workflow['id']}/run").status_code == 404
    assert client.get(f"/api/v1/workflows/{workflow['id']}/runs").status_code == 404
    assert client.post(
        "/api/v1/projects", json={"workspace_id": workspace["id"], "name": "Intrusion"}
    ).status_code == 404
    assert client.post(
        "/api/v1/tasks", json={"workspace_id": workspace["id"], "title": "Intrusion"}
    ).status_code == 404
    assert client.post(
        "/api/v1/workflows",
        json={
            "workspace_id": workspace["id"],
            "name": "Intrusion",
            "steps": [{"action": "create_task", "title": "Intrusion"}],
        },
    ).status_code == 404
    assert client.post("/api/v1/workspaces", json={"name": "Account A"}).status_code == 201
    auth_user["sub"] = account_a

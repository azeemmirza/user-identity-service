import pytest
from faker import Faker
from fastapi.testclient import TestClient

from src.main import bootstrap
from tests.conftest import integration


fake = Faker()


@pytest.fixture(scope="module")
def client():
    app = bootstrap()
    return TestClient(app)


def _email() -> str:
    return fake.unique.email()


def _password() -> str:
    return "Str0ngP@ssw0rd!"


def _register_payload(email: str | None = None) -> dict:
    password = _password()
    return {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": email or _email(),
        "password": password,
        "confirm_password": password,
    }


def _register_user(client: TestClient, email: str | None = None) -> dict:
    payload = _register_payload(email)
    response = client.post("/auth/register", json=payload)
    assert response.status_code in (200, 201)
    return response.json()


def _login_user(client: TestClient, email: str, password: str | None = None) -> dict:
    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password or _password(),
        },
    )
    assert response.status_code == 200
    return response.json()


def _auth_headers(access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}


@integration
def test_register_creates_user_successfully(client: TestClient) -> None:
    payload = _register_payload()
    response = client.post("/auth/register", json=payload)

    assert response.status_code in (200, 201)
    body = response.json()
    assert body["user"]["email"] == payload["email"].lower()
    assert body["tokens"]["access_token"]
    assert body["tokens"]["refresh_token"]
    assert body["session"]["id"]


@integration
def test_register_validation_error_on_mismatched_passwords(client: TestClient) -> None:
    payload = _register_payload()
    payload["confirm_password"] = "DifferentP@ssw0rd!"

    response = client.post("/auth/register", json=payload)

    assert response.status_code == 400


@integration
def test_register_duplicate_email_returns_conflict(client: TestClient) -> None:
    email = _email()
    payload = _register_payload(email)

    first_response = client.post("/auth/register", json=payload)
    second_response = client.post("/auth/register", json=payload)

    assert first_response.status_code in (200, 201)
    assert second_response.status_code == 409


@integration
def test_login_returns_token_bundle_and_user_summary(client: TestClient) -> None:
    registration = _register_user(client)

    response = client.post(
        "/auth/login",
        json={
            "email": registration["user"]["email"],
            "password": _password(),
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["user"]["email"] == registration["user"]["email"]
    assert body["tokens"]["token_type"] == "bearer"


@integration
def test_refresh_rotates_refresh_token_and_rejects_old_token(client: TestClient) -> None:
    registration = _register_user(client)
    original_refresh = registration["tokens"]["refresh_token"]

    refresh_response = client.post(
        "/auth/token",
        json={"refresh_token": original_refresh},
    )

    assert refresh_response.status_code == 200
    rotated_refresh = refresh_response.json()["tokens"]["refresh_token"]
    assert rotated_refresh != original_refresh

    replay_response = client.post(
        "/auth/token",
        json={"refresh_token": original_refresh},
    )

    assert replay_response.status_code == 401


@integration
def test_logout_revokes_session_and_blocks_future_refresh(client: TestClient) -> None:
    registration = _register_user(client)
    refresh_token = registration["tokens"]["refresh_token"]

    logout_response = client.post(
        "/auth/logout",
        json={"refresh_token": refresh_token},
    )
    assert logout_response.status_code == 200

    refresh_response = client.post(
        "/auth/token",
        json={"refresh_token": refresh_token},
    )
    assert refresh_response.status_code == 401


@integration
def test_authenticated_user_and_session_endpoints_return_current_identity(client: TestClient) -> None:
    registration = _register_user(client)
    access_token = registration["tokens"]["access_token"]

    me_response = client.get("/users/me", headers=_auth_headers(access_token))
    sessions_response = client.get("/sessions/", headers=_auth_headers(access_token))

    assert me_response.status_code == 200
    assert me_response.json()["email"] == registration["user"]["email"]
    assert sessions_response.status_code == 200
    assert any(item["id"] == registration["session"]["id"] for item in sessions_response.json())


@integration
def test_revoke_specific_session_marks_it_inactive(client: TestClient) -> None:
    registration = _register_user(client)
    first_session_id = registration["session"]["id"]
    second_login = _login_user(client, registration["user"]["email"])
    access_token = second_login["tokens"]["access_token"]

    revoke_response = client.delete(
        f"/sessions/{first_session_id}",
        headers=_auth_headers(access_token),
    )
    session_response = client.get(
        f"/sessions/{first_session_id}",
        headers=_auth_headers(access_token),
    )

    assert revoke_response.status_code == 200
    assert session_response.status_code == 200
    assert session_response.json()["revoked_at"] is not None


@integration
def test_cross_user_session_revocation_is_rejected(client: TestClient) -> None:
    first_user = _register_user(client)
    second_user = _register_user(client)
    first_access_token = first_user["tokens"]["access_token"]
    second_session_id = second_user["session"]["id"]

    response = client.delete(
        f"/sessions/{second_session_id}",
        headers=_auth_headers(first_access_token),
    )

    assert response.status_code == 403


@integration
def test_forgot_password_returns_same_message_for_known_and_unknown_email(client: TestClient) -> None:
    registration = _register_user(client)
    known_response = client.post(
        "/auth/password/forgot",
        json={"email": registration["user"]["email"]},
    )
    unknown_response = client.post(
        "/auth/password/forgot",
        json={"email": _email()},
    )

    assert known_response.status_code == 200
    assert unknown_response.status_code == 200
    assert known_response.json() == unknown_response.json()


@integration
def test_reset_password_updates_credentials_and_invalidates_existing_sessions(client: TestClient) -> None:
    registration = _register_user(client)
    email = registration["user"]["email"]
    forgot_response = client.post(
        "/auth/password/forgot",
        json={"email": email},
    )
    reset_token = forgot_response.headers["X-Debug-Reset-Token"]
    old_refresh_token = registration["tokens"]["refresh_token"]

    reset_response = client.post(
        "/auth/password/reset",
        json={
            "token": reset_token,
            "password": "N3wStr0ngP@ss!",
            "confirm_password": "N3wStr0ngP@ss!",
        },
    )
    reused_response = client.post(
        "/auth/password/reset",
        json={
            "token": reset_token,
            "password": "An0therStr0ngP@ss!",
            "confirm_password": "An0therStr0ngP@ss!",
        },
    )
    old_refresh_response = client.post(
        "/auth/token",
        json={"refresh_token": old_refresh_token},
    )
    old_login_response = client.post(
        "/auth/login",
        json={"email": email, "password": _password()},
    )
    new_login_response = client.post(
        "/auth/login",
        json={"email": email, "password": "N3wStr0ngP@ss!"},
    )

    assert reset_response.status_code == 200
    assert reused_response.status_code == 400
    assert old_refresh_response.status_code == 401
    assert old_login_response.status_code == 401
    assert new_login_response.status_code == 200

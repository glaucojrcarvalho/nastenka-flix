from fastapi.testclient import TestClient

from app.main import app


def test_root_healthcheck() -> None:
    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"


def test_login_and_protected_series_list() -> None:
    with TestClient(app) as client:
        login_response = client.post(
            "/api/auth/login",
            json={"username": "viewer", "password": "changeme"},
        )

        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        unauthorized_response = client.get("/api/series/")
        assert unauthorized_response.status_code == 401

        authorized_response = client.get(
            "/api/series/",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert authorized_response.status_code == 200
    assert isinstance(authorized_response.json(), list)
    assert len(authorized_response.json()) > 0

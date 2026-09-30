from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app

settings = get_settings()


def test_no_token_returns_401():
    with TestClient(app) as client:
        response = client.get("/api/auth/me")
        assert response.status_code == 401
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "UNAUTHORIZED"


def test_viewer_access_admin_returns_403():
    with TestClient(app) as client:
        # Login as viewer
        login_res = client.post(
            "/api/auth/login",
            json={"email": settings.SEED_VIEWER_EMAIL, "password": settings.SEED_VIEWER_PASSWORD},
        )
        assert login_res.status_code == 200

        # Attempt to access admin users endpoint
        admin_res = client.get("/api/admin/users")
        assert admin_res.status_code == 403
        data = admin_res.json()
        assert "error" in data
        assert data["error"]["code"] == "FORBIDDEN"


def test_admin_access_admin_returns_200():
    with TestClient(app) as client:
        # Login as admin
        login_res = client.post(
            "/api/auth/login",
            json={"email": settings.SEED_ADMIN_EMAIL, "password": settings.SEED_ADMIN_PASSWORD},
        )
        assert login_res.status_code == 200

        # Access admin users endpoint
        admin_res = client.get("/api/admin/users")
        assert admin_res.status_code == 200
        users = admin_res.json()
        assert isinstance(users, list)
        assert len(users) >= 3


def test_cookie_login_flow():
    with TestClient(app) as client:
        # Login sets httpOnly cookie
        login_res = client.post(
            "/api/auth/login",
            json={"email": settings.SEED_ADMIN_EMAIL, "password": settings.SEED_ADMIN_PASSWORD},
        )
        assert login_res.status_code == 200
        assert settings.COOKIE_NAME in client.cookies

        # /me succeeds using the cookie only
        me_res = client.get("/api/auth/me")
        assert me_res.status_code == 200
        me_data = me_res.json()
        assert me_data["email"] == settings.SEED_ADMIN_EMAIL
        assert me_data["role"] == "admin"

        # Logout deletes cookie
        logout_res = client.post("/api/auth/logout")
        assert logout_res.status_code == 200
        me_after_logout = client.get("/api/auth/me")
        assert me_after_logout.status_code == 401


def test_admin_user_crud_and_conflict():
    with TestClient(app) as client:
        # Login as admin
        client.post(
            "/api/auth/login",
            json={"email": settings.SEED_ADMIN_EMAIL, "password": settings.SEED_ADMIN_PASSWORD},
        )

        # Create new user
        new_email = "newuser@playnepse.local"
        create_res = client.post(
            "/api/admin/users",
            json={"email": new_email, "password": "newpassword123", "role": "analyst"},
        )
        assert create_res.status_code in (201, 409)

        # Attempt duplicate email
        dup_res = client.post(
            "/api/admin/users",
            json={"email": settings.SEED_ADMIN_EMAIL, "password": "password", "role": "viewer"},
        )
        assert dup_res.status_code == 409
        dup_data = dup_res.json()
        assert dup_data["error"]["code"] == "CONFLICT"


def test_token_endpoint_swagger_flow():
    with TestClient(app) as client:
        token_res = client.post(
            "/api/auth/token",
            data={"username": settings.SEED_ADMIN_EMAIL, "password": settings.SEED_ADMIN_PASSWORD},
        )
        assert token_res.status_code == 200
        token_data = token_res.json()
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"

        # Use bearer token in Authorization header
        me_res = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token_data['access_token']}"},
        )
        assert me_res.status_code == 200
        assert me_res.json()["email"] == settings.SEED_ADMIN_EMAIL

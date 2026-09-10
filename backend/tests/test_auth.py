from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings


def test_registration_and_login(client):
    response = client.post(
        "/auth/register",
        json={"email": "person@example.com", "password": "Password123!"},
    )
    assert response.status_code == 201
    assert response.json()["email"] == "person@example.com"

    login = client.post(
        "/auth/login",
        data={"username": "person@example.com", "password": "Password123!"},
    )
    assert login.status_code == 200
    assert login.json()["token_type"] == "bearer"


def test_duplicate_and_invalid_registration(client):
    payload = {"email": "person@example.com", "password": "Password123!"}
    assert client.post("/auth/register", json=payload).status_code == 201
    assert client.post("/auth/register", json=payload).status_code == 409
    assert client.post(
        "/auth/register",
        json={"email": "invalid", "password": "short"},
    ).status_code == 422


def test_invalid_login_and_token(client):
    client.post(
        "/auth/register",
        json={"email": "person@example.com", "password": "Password123!"},
    )
    wrong_password = client.post(
        "/auth/login",
        data={"username": "person@example.com", "password": "wrong-password"},
    )
    assert wrong_password.status_code == 401
    nonexistent = client.post(
        "/auth/login",
        data={"username": "missing@example.com", "password": "Password123!"},
    )
    assert nonexistent.status_code == 401
    assert client.get("/expenses", headers={"Authorization": "Bearer invalid"}).status_code == 401


def test_expired_token_is_rejected(client):
    token = jwt.encode(
        {"sub": "1", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    response = client.get("/expenses", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401

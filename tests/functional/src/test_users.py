import pytest
from http import HTTPStatus


@pytest.mark.parametrize("user_data, expected_status", [
    ({
        "email": "user@test.com",
        "password": "password",
        "username": "testuser"
    }, HTTPStatus.OK),
    ({"email": "invalid-email", "password": "password", "username": "testuser"}, HTTPStatus.UNPROCESSABLE_ENTITY),
    ({"email": "user@test.com", "password": "password"}, HTTPStatus.UNPROCESSABLE_ENTITY),
])
@pytest.mark.asyncio
async def test_register_user(make_post_request, user_data, expected_status):
    path = "/users/register"
    response = await make_post_request(path=path, body=user_data)
    body, status, _ = response

    assert status == expected_status

    if status == HTTPStatus.OK:
        assert body["email"] == user_data["email"]
        assert body["username"] == user_data["username"]


@pytest.mark.parametrize("login_data, expected_status", [
    ({"username": "testuser", "password": "password",}, HTTPStatus.OK),
    ({"username": "nonexistent_user", "password": "password"}, HTTPStatus.UNAUTHORIZED),
    ({"username": "testuser", "password": "wrongpassword"}, HTTPStatus.UNAUTHORIZED),
    ({"password": "password"}, HTTPStatus.UNPROCESSABLE_ENTITY),
    ({"username": "testuser"}, HTTPStatus.UNPROCESSABLE_ENTITY),
])
@pytest.mark.asyncio
async def test_login_user(make_post_request, create_user, login_data, expected_status):
    await create_user(email="user@test.com", password="password", username="testuser")

    path = "/users/token"
    body, status, _ = await make_post_request(path=path, data=login_data)

    assert status == expected_status

    if status == HTTPStatus.OK:
        assert "access_token" in body

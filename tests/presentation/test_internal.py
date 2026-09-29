from httpx import AsyncClient


async def test_get_user_success(client: AsyncClient) -> None:
    await client.post(
        "/auth/register",
        json={"name": "Alice", "email": "alice@test.com", "password": "password123"},
    )

    resp = await client.get("/internal/users/1")

    assert resp.status_code == 200
    data = resp.json()
    assert data["user_id"] == 1
    assert data["name"] == "Alice"
    assert data["email"] == "alice@test.com"


async def test_get_user_not_found(client: AsyncClient) -> None:
    resp = await client.get("/internal/users/999")

    assert resp.status_code == 404
    assert resp.json()["detail"] == "User not found"


async def test_delete_user_success(client: AsyncClient) -> None:
    await client.post(
        "/auth/register",
        json={"name": "Alice", "email": "alice@test.com", "password": "password123"},
    )

    resp = await client.delete("/internal/users/1")
    assert resp.status_code == 204

    resp = await client.get("/internal/users/1")
    assert resp.status_code == 404


async def test_delete_user_not_found(client: AsyncClient) -> None:
    resp = await client.delete("/internal/users/999")

    assert resp.status_code == 404
    assert resp.json()["detail"] == "User not found"

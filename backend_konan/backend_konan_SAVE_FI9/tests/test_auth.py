import pytest
@pytest.mark.anyio
async def test_login_validation(client):
    r = await client.post("/auth/login", json={"email":"x@x.tn","password":"pass"})
    assert r.status_code in (200, 401, 422)

@pytest.mark.anyio
async def test_me_requires_auth(client):
    r = await client.get("/auth/me")
    assert r.status_code in (401, 403)

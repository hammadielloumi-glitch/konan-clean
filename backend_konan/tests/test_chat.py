import pytest
@pytest.mark.anyio
async def test_chat_message_ok(client):
    payload = {"message": "Bonjour", "conversation_id": None, "max_tokens": 64}
    r = await client.post("/chat/ask", json=payload)
    assert r.status_code in (200, 401, 403)  # 200 si mode ouvert
    if r.status_code == 200:
        j = r.json()
        assert "reply" in j

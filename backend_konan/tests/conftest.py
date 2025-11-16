import os, pytest, asyncio
from httpx import AsyncClient
from app.main import app

BASE = os.getenv("TEST_BASE", "http://konan_backend:8000")

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

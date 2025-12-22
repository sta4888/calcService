import pytest
from httpx import AsyncClient

from main import app
from infrastructure.db.session import async_session
from infrastructure.db.models import MemberDB, MemberStatsDB


@pytest.mark.asyncio
async def test_user_structure_endpoint():
    async with async_session() as session:
        async with session.begin():
            root = MemberDB(user_id=10)
            root.stats = MemberStatsDB(lo=200)

            child = MemberDB(user_id=11, referrer=root)
            child.stats = MemberStatsDB(lo=30)

            session.add_all([root, child])

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/users/10/structure")

    assert response.status_code == 200

    body = response.json()
    assert body["error"] is False

    data = body["data"]
    assert data["user_id"] == 10
    assert len(data["team"]) == 1
    assert data["team"][0]["user_id"] == 11
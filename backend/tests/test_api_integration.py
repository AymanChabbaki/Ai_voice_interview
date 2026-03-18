import pandas as pd
import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_categories_returns_503_when_questions_missing(app_module):
    app_module.df_questions = None

    transport = ASGITransport(app=app_module.app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/categories")

    assert response.status_code == 503


@pytest.mark.asyncio
async def test_categories_returns_data_when_questions_loaded(app_module):
    app_module.df_questions = pd.DataFrame(
        {
            "Category": ["Python", "Python", "DevOps"],
            "Difficulty": ["Easy", "Medium", "Hard"],
        }
    )

    transport = ASGITransport(app=app_module.app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/categories")

    assert response.status_code == 200
    data = response.json()
    assert data["total_categories"] == 2
    assert "Python" in data["top_categories"]


@pytest.mark.asyncio
async def test_register_returns_422_for_invalid_payload(app_module):
    transport = ASGITransport(app=app_module.app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/register",
            json={
                "username": "ab",
                "email": "not-an-email",
                "password": "123",
                "name": "x",
            },
        )

    assert response.status_code == 422

import pytest
from httpx import AsyncClient, ASGITransport
from src.server.main import app
from src.server.core.database import db

# Base URL for tests
BASE_URL = "http://testserver/api/v1"

@pytest.fixture
async def client():
    # Clean DB before tests
    await db.users.delete_many({})
    await db.collaboration_requests.delete_many({})
    await db.meetings.delete_many({})
    await db.documents.delete_many({})
    await db.transactions.delete_many({})
    await db.otp_records.delete_many({})

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_full_lifecycle(client):
    # 1. Register Investor
    res = await client.post("/api/v1/auth/register", json={
        "name": "Investor", "email": "inv@test.com", "password": "password", "role": "investor",
        "investmentInterests": ["Tech"], "investmentStage": ["Seed"], "portfolioCompanies": [],
        "totalInvestments": 0, "minimumInvestment": 1000.0, "maximumInvestment": 5000.0
    })
    assert res.status_code == 200
    inv_token = res.json()["access_token"]
    
    # 2. Register Entrepreneur
    res = await client.post("/api/v1/auth/register", json={
        "name": "Entrep", "email": "ent@test.com", "password": "password", "role": "entrepreneur",
        "startupName": "TestAI", "pitchSummary": "Pitch", "fundingNeeded": 100000.0,
        "industry": "Tech", "location": "NY", "foundedYear": 2023, "teamSize": 5
    })
    assert res.status_code == 200
    ent_token = res.json()["access_token"]

    # 3. Get Investor ID
    res = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {inv_token}"})
    inv_id = res.json()["id"]

    # 4. Get Entrep ID
    res = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {ent_token}"})
    ent_id = res.json()["id"]

    # 5. Collaboration Request
    res = await client.post("/api/v1/collaboration/request", 
        json={"receiver_id": ent_id, "pitch_message": "Hi"},
        headers={"Authorization": f"Bearer {inv_token}"}
    )
    assert res.status_code == 200
    req_id = res.json()["_id"]

    # 6. Accept Request
    res = await client.patch(f"/api/v1/collaboration/request/{req_id}/status",
        json={"status": "accepted"},
        headers={"Authorization": f"Bearer {ent_token}"}
    )
    assert res.status_code == 200

    # 7. Schedule Meeting
    from datetime import datetime, timedelta
    start = datetime.utcnow() + timedelta(days=1)
    end = start + timedelta(hours=1)
    res = await client.post("/api/v1/meetings/",
        json={
            "title": "Pitch", "invitee_id": ent_id,
            "start_time": start.isoformat(), "end_time": end.isoformat()
        },
        headers={"Authorization": f"Bearer {inv_token}"}
    )
    assert res.status_code == 200
    
    # 8. Payments
    res = await client.post("/api/v1/payments/transfer",
        json={"recipient_id": ent_id, "amount": 100.0},
        headers={"Authorization": f"Bearer {inv_token}"}
    )
    assert res.status_code == 200

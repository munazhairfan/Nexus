import asyncio
import httpx
import uuid

BASE_URL = "http://localhost:8001/api/v1"

async def run_chaos():
    limits = httpx.Limits(max_keepalive_connections=20, max_connections=100)
    async with httpx.AsyncClient(base_url=BASE_URL, limits=limits, timeout=30.0) as client:
        # Auth helper
        reg_data = {"name": "Test", "email": f"test{uuid.uuid4()}@test.com", "password": "password", "role": "investor", "investmentInterests": ["Tech"], "investmentStage": ["Seed"], "portfolioCompanies": [], "totalInvestments": 0, "minimumInvestment": 1000.0, "maximumInvestment": 5000.0}
        await client.post("/auth/register", json=reg_data)
        res = await client.post("/auth/login", json={"email": reg_data["email"], "password": "password", "role": "investor"})
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Race condition attack
        print("Running race condition attack...")
        tasks = [client.post("/meetings/", json={
            "title": "Race Meeting", "invitee_id": "6a53d4eb638592b95124e8c1",
            "start_time": "2026-07-15T10:00:00Z", "end_time": "2026-07-15T11:00:00Z"
        }, headers=headers) for _ in range(10)]
        results = await asyncio.gather(*tasks)
        successes = [r for r in results if r.status_code == 200]
        rejects = [r for r in results if r.status_code in [400, 409]]
        print(f"Race condition: {len(successes)} successful, {len(rejects)} rejected (Expected: 1 succ, 9 rej)")

        # 2. Rate limiting attack
        print("Running rate limiting attack...")
        rate_results = []
        for _ in range(70):
            res = await client.get("/auth/me", headers=headers)
            rate_results.append(res.status_code)
            await asyncio.sleep(0.02) # Micro-throttle
        
        passed = rate_results.count(200)
        blocked = rate_results.count(429)
        print(f"Rate limiting: {passed} passed, {blocked} blocked (Expected: 60 pass, 10 block)")

        # 3. Malformed ID injection
        print("Running malformed ID injection...")
        res = await client.patch("/collaboration/request/invalid-id/status", json={"status": "accepted"}, headers=headers)
        print(f"Malformed ID: {res.status_code} (Expected: 400 or 404)")

if __name__ == "__main__":
    asyncio.run(run_chaos())

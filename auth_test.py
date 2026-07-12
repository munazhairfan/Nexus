import httpx
import asyncio

async def main():
    async with httpx.AsyncClient() as client:
        # Register
        reg_data = {"name": "Investor", "email": "inv@test.com", "password": "password", "role": "investor", "investmentInterests": ["Tech"], "investmentStage": ["Seed"], "portfolioCompanies": [], "totalInvestments": 0, "minimumInvestment": 1000.0, "maximumInvestment": 5000.0}
        await client.post("http://localhost:8000/api/v1/auth/register", json=reg_data)
        
        # Login
        login_data = {"email": "inv@test.com", "password": "password", "role": "investor"}
        res = await client.post("http://localhost:8000/api/v1/auth/login", json=login_data)
        print(res.json()["access_token"])

asyncio.run(main())

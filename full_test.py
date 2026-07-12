import httpx
import asyncio

async def main():
    async with httpx.AsyncClient(base_url="http://localhost:8001") as client:
        # Auth
        reg_data = {"name": "Investor", "email": "inv2@test.com", "password": "password", "role": "investor", "investmentInterests": ["Tech"], "investmentStage": ["Seed"], "portfolioCompanies": [], "totalInvestments": 0, "minimumInvestment": 1000.0, "maximumInvestment": 5000.0}
        await client.post("/api/v1/auth/register", json=reg_data)
        
        login_data = {"email": "inv2@test.com", "password": "password", "role": "investor"}
        res = await client.post("/api/v1/auth/login", json=login_data)
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2FA
        await client.post("/api/v1/security/2fa/generate", headers=headers)
        print("2FA generated")
        
        # Doc Firewall
        # Upload as Investor
        files = {"file": ("test.pdf", b"pdfcontent", "application/pdf")}
        res = await client.post("/api/v1/documents/upload", files=files, headers=headers)
        doc_id = res.json()["_id"]
        
        # Access as another user (fails)
        res = await client.get(f"/api/v1/documents/view/{doc_id}", headers={"Authorization": "Bearer fake"})
        print(f"Unauthorized access check: {res.status_code}")
        
        # Payments
        # Deposit
        await client.post("/api/v1/payments/deposit", json={"amount": 150.0}, headers=headers)
        # Transfer Fail
        res = await client.post("/api/v1/payments/transfer", json={"recipient_id": "fake", "amount": 999.0}, headers=headers)
        print(f"Transfer fail check: {res.status_code}")

asyncio.run(main())

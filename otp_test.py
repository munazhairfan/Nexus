import httpx
import asyncio

async def main():
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2YTUzZDczNjM0NDIyMjdlYmVhYzAyZTYiLCJyb2xlIjoiaW52ZXN0b3IiLCJleHAiOjE3ODM4ODQzODJ9.qpoG9c0Wg3MXcHDlEErK7oZBi4cDynfu2LrBrpn-qyM"
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        # Generate 2FA
        await client.post("http://localhost:8000/api/v1/security/2fa/generate", headers=headers)
        print("2FA generated")

asyncio.run(main())

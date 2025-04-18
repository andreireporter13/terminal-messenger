import httpx

async def test_request():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/register/",
            json={"username": "ion", "password": "parola123"}
        )
        print(response.status_code)
        print(response.text)

import asyncio
asyncio.run(test_request())

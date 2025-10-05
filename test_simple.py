import asyncio
import aiohttp
import json

async def test_single():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://ads-checker-api.onrender.com/api/v1/no-api/analyze/rockler.com') as resp:
            result = await resp.json()
            print("Status:", resp.status)
            print("Response:")
            print(json.dumps(result, indent=2))

asyncio.run(test_single())
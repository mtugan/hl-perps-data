# Data fetching
import requests
import asyncio
import aiohttp

# Data processiong
import json

# Time
from datetime import datetime


async def make_request(session, url, headers, data):
    async with session.post(url, headers=headers, json=data) as response:
        return await response.text()


def fetch_hyperliquid_universe():
    url = "https://api.hyperliquid.xyz/info"
    header_data = {"Content-Type": "application/json"}
    request_data = {"type": "meta"}
    return json.loads(requests.post(url, headers=header_data, json=request_data).text)


def fetch_hyperliquid_tokens(hl_universe_reponse):
    return [coin["name"] for coin in hl_universe_reponse["universe"]]


async def _fetch_hyperliquid_historical_funding(coins, start_times, end_times=[]):
    if len(coins) != len(start_times):
        raise Exception("Coins / times must be same len")

    if len(end_times) != 0 and len(end_times) != len(start_times):
        raise Exception("Len times must be equal len coins")

    if len(end_times) == 0:
        timestamp = datetime.now().timestamp()
        end_times = [timestamp for _ in start_times]

    url = "https://api.hyperliquid.xyz/info"

    async with aiohttp.ClientSession() as session:
        tasks = []

        for i in range(len(coins)):
            # Rate limit 1200 per minute, means 50 ms per
            # We could do faster but let's keep it like this

            await asyncio.sleep(0.05)

            tasks.append(
                asyncio.ensure_future(
                    make_request(
                        session,
                        url,
                        {"Content-Type": "application/json"},
                        {
                            "type": "fundingHistory",
                            "coin": coins[i],
                            "startTime": int(start_times[i] * 1000),
                            "endTime": int(end_times[i] * 1000),
                        },
                    )
                )
            )

        responses = await asyncio.gather(*tasks)

    return [json.loads(response) for response in responses]


def fetch_hyperliquid_historical_funding(coins, start_times, end_times=[]):
    return asyncio.run(
        _fetch_hyperliquid_historical_funding(coins, start_times, end_times)
    )

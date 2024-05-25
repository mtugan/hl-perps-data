import sys

# Data fetching
import requests
import asyncio
import aiohttp

# Data processing
import json

# Time
from datetime import datetime


async def _async_coroutine(session, url, headers, data, callback=lambda: _):
    async with session.post(url, headers=headers, json=data) as response:
        response = await response.text()
        callback()
        return response


def fetch_hyperliquid_universe():
    url = "https://api.hyperliquid.xyz/info"
    header_data = {"Content-Type": "application/json"}
    request_data = {"type": "meta"}
    return json.loads(requests.post(url, headers=header_data, json=request_data).text)


def fetch_hyperliquid_tokens(hl_universe_reponse):
    if not hl_universe_reponse:
        raise Exception(
            "Something went wrong with fetching data from Hyperliquid, error:\n"
            + hl_universe_reponse.text
        )
        sys.exit(0)

    return [coin["name"] for coin in hl_universe_reponse["universe"]]


def fetch_hyperliquid_universe_ctx():
    url = "https://api.hyperliquid.xyz/info"
    header_data = {"Content-Type": "application/json"}
    request_data = {"type": "metaAndAssetCtxs"}
    return json.loads(requests.post(url, headers=header_data, json=request_data).text)


def fetch_hyperliquid_current_funding(hl_universe_ctx_response):
    if not hl_universe_ctx_response:
        raise Exception(
            "Something went wrong with fetching data from Hyperliquid, error\n"
            + hl_universe_ctx_response.text
        )
        sys.exit(0)
    return [rates["funding"] for rates in hl_universe_ctx_response]


async def _fetch_hyperliquid_historical_funding(coins, start_times, end_times=[]):
    if len(coins) != len(start_times):
        raise Exception("Coins / times must be same len")

    if len(end_times) != 0 and len(end_times) != len(start_times):
        raise Exception("Len times must be equal len coins")

    if len(end_times) == 0:
        timestamp = datetime.now().timestamp()
        end_times = [timestamp for _ in start_times]

    # Urls

    url = "https://api.hyperliquid.xyz/info"
    header = {"Content-Type": "application/json"}

    # We need this callback to so we can later correct if HL doesn't answer properly

    responses = None

    response_order = []

    def request_callback(coin):
        return lambda: response_order.append(coin)

    async with aiohttp.ClientSession() as session:
        tasks = []

        for i in range(len(coins)):
            # Rate limit 1200 per minute, means 50 ms per
            # We could do faster but let's keep it like this

            await asyncio.sleep(0.05)

            tasks.append(
                asyncio.ensure_future(
                    _async_coroutine(
                        session,
                        url,
                        header,
                        {
                            "type": "fundingHistory",
                            "coin": coins[i],
                            "startTime": int(start_times[i] * 1000),
                            "endTime": int(end_times[i] * 1000),
                        },
                        request_callback(
                            coins[i]
                        ),  # Returns the callback function here
                    )
                )
            )

        responses = await asyncio.gather(*tasks)

    responses = [json.loads(response) for response in responses]

    # We need to sort the coins
    funding_data = [None] * len(coins)

    # We need a key map for it
    kmap = {value: index for index, value in enumerate(coins)}

    # Now we need to build the array, and also HL sometimes doesn't return values properly
    # so we need to refetch

    responses_index = 0

    while responses_index < len(responses):
        token_data = responses[responses_index]

        if token_data:
            funding_data[kmap[token_data[0]["coin"]]] = token_data
            responses_index += 1
        else:
            responses[responses_index] = json.loads(
                requests.post(
                    url,
                    headers=header,
                    json={
                        "type": "fundingHistory",
                        "coin": response_order[responses_index],
                        "startTime": int(start_times[i] * 1000),
                        "endTime": int(end_times[i] * 1000),
                    },
                ).text
            )

    return funding_data


def fetch_hyperliquid_historical_funding(coins, start_times, end_times=[]):
    return asyncio.run(
        _fetch_hyperliquid_historical_funding(coins, start_times, end_times)
    )

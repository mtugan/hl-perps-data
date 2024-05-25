import json

# Plotting
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Time
from datetime import datetime

# Hyperliquid fn
from fetch import (
    fetch_hyperliquid_historical_funding,
    fetch_hyperliquid_tokens,
    fetch_hyperliquid_universe,
)

tokens = fetch_hyperliquid_tokens(fetch_hyperliquid_universe())

start_time_timestamp = datetime.now().timestamp() - 24 * 60 * 60

historical_funding_data = fetch_hyperliquid_historical_funding(
    tokens, [start_time_timestamp for _ in tokens]
)

# Create the chart
fig, ax = plt.subplots(figsize=(24, 12))

for c in range(len(historical_funding_data)):
    funding_data_coin = historical_funding_data[c]

    if funding_data_coin:
        ax.plot(
            [datetime.fromtimestamp(t["time"] / 1000) for t in funding_data_coin],
            [float(t["fundingRate"]) for t in funding_data_coin],
            label=funding_data_coin[0]["coin"],
        )

# Label chart
ax.set_title("Hyperliquid Funding Rates")
ax.set_xlabel("Time")
ax.set_ylabel("Funding Rate")

# Format x axis to display dates
date_format = mdates.DateFormatter("%m/%d %H:%M")
ax.xaxis.set_major_formatter(date_format)
plt.xticks(rotation=45)

# Add a legend
ax.legend()

# Adjust layout and display chart
plt.tight_layout()
plt.show()

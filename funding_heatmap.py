import json
import math
import numpy as np

# Plotting
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter

# Time
from datetime import datetime

# Hyperliquid fn
from functions import (
    fetch_hyperliquid_historical_funding,
    fetch_hyperliquid_tokens,
    fetch_hyperliquid_universe_ctx,
    fetch_hyperliquid_current_funding,
)


def format_percentage(value, pos):
    return f"{value:.5%}"


def create_heatmap(historical_funding_data, tokens, max_tokens_per_window=25):
    # We will need multiple windows because we can't fit all tokens nicely on one
    figures = []

    num_windows = math.ceil(len(tokens) / max_tokens_per_window)

    # Calculate the standard deviation of funding rates
    all_funding_rates = [
        float(t["fundingRate"])
        for token_data in historical_funding_data
        if token_data
        for t in token_data
    ]

    stdev = np.std(all_funding_rates)

    # Start building the heatmaps

    for window in range(num_windows):
        # Start index of individual heatmap
        start_index = window * max_tokens_per_window

        # EXCLUSIVE end index of individual heatmap
        end_index = min((window + 1) * max_tokens_per_window, len(tokens))

        # The tokens are our y ticks
        y_ticks = tokens[start_index:end_index]

        # Funding rates our heat
        heat_values = []

        # X ticks will is unix timestamp
        x_ticks = []

        # Sometimes hyperliquid returns something malformed or nothing we just fetch for those again
        for token_data in historical_funding_data[start_index:end_index]:
            heat_values.append([float(t["fundingRate"]) for t in token_data])
            x_ticks = [datetime.fromtimestamp(t["time"] / 1000) for t in token_data]

        # Get new subplot and add figure
        fig, ax = plt.subplots(figsize=(24, 12))
        figures.append(fig)  # Store the figure reference

        # Create heatmap
        im = ax.imshow(
            heat_values, cmap="RdYlGn", vmin=-stdev, vmax=stdev, aspect="auto"
        )

        # Set x axis ticks
        ax.set_xticks(range(len(x_ticks)))
        ax.set_xticklabels(
            [date.strftime("%H:%M %d %b") for date in x_ticks],
            rotation=45,
            ha="right",
            fontsize=8,
        )

        # Set y axis ticks
        ax.set_yticks(range(len(y_ticks)))
        ax.set_yticklabels(y_ticks)

        # Set colour style
        cbar = ax.figure.colorbar(im, ax=ax, format=FuncFormatter(format_percentage))

        # y label
        cbar.ax.set_ylabel("Funding Rate", rotation=-90, va="bottom")

        # Title
        ax.set_title(f"Hyperliquid Funding Rates - Window {window + 1}")

        # Layout
        fig.tight_layout()

        # For each heatmap box style & add text
        for i in range(len(y_ticks)):
            for j in range(len(x_ticks)):
                if i < len(heat_values) and j < len(heat_values[i]):
                    text = ax.text(
                        j,
                        i,
                        f"{heat_values[i][j]:.5%}",
                        ha="center",
                        va="center",
                        color="black",
                        fontsize=6,
                    )

        # Save fig move onto next
        plt.savefig("funding_heatmap_" + f"{window}" + ".png")

    plt.show()  # Display all the heatmaps at once


# Fetch market data
hyperliquid_universe_ctx = fetch_hyperliquid_universe_ctx()

# Assign tokens and current funding

tokens = fetch_hyperliquid_tokens(hyperliquid_universe_ctx[0])

hyperliquid_current_funding = fetch_hyperliquid_current_funding(
    hyperliquid_universe_ctx[1]
)

# Set start time

current_time = datetime.now().timestamp()

start_time = current_time - 24 * 60 * 60

historical_funding_data = fetch_hyperliquid_historical_funding(
    tokens, [start_time for _ in tokens]
)

# Add to the historical funding data current values

for i in range(len(historical_funding_data)):
    # We don't need premium
    historical_funding_data[i].append(
        {
            "coin": historical_funding_data[i][0]["coin"],
            "fundingRate": hyperliquid_current_funding[i],
            "time": int(current_time * 1000),
        }
    )

create_heatmap(historical_funding_data, tokens)

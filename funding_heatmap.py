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
    fetch_hyperliquid_universe,
)


def format_percentage(value, pos):
    return f"{value:.5%}"


def create_heatmap(
    historical_funding_data, tokens, start_time, max_tokens_per_window=25
):
    # Calculate the standard deviation of absolute funding rates
    all_funding_rates = [
        abs(float(t["fundingRate"]))
        for token_data in historical_funding_data
        if token_data
        for t in token_data
    ]

    figures = []

    num_windows = math.ceil(len(tokens) / max_tokens_per_window)

    stdev = np.std(all_funding_rates)

    for window in range(num_windows):
        start_index = window * max_tokens_per_window

        end_index = min((window + 1) * max_tokens_per_window, len(tokens))

        index = start_index

        current_tokens = tokens[start_index:end_index]

        y_ticks = current_tokens

        data = []

        x_ticks = []

        while index < end_index:
            token_data = historical_funding_data[index]
            if token_data:
                data.append([float(t["fundingRate"]) for t in token_data])
                x_ticks = [datetime.fromtimestamp(t["time"] / 1000) for t in token_data]
                index += 1
            else:
                historical_funding_data[index] = fetch_hyperliquid_historical_funding(
                    [tokens[index]], [start_time]
                )[0]

        fig, ax = plt.subplots(figsize=(24, 12))
        figures.append(fig)  # Store the figure reference

        im = ax.imshow(data, cmap="RdYlGn", vmin=-stdev, vmax=stdev, aspect="auto")

        ax.set_xticks(range(len(x_ticks)))
        ax.set_xticklabels(
            [date.strftime("%H:00 %d %b") for date in x_ticks],
            rotation=45,
            ha="right",
            fontsize=8,
        )

        ax.set_yticks(range(len(y_ticks)))
        ax.set_yticklabels(y_ticks)

        cbar = ax.figure.colorbar(im, ax=ax, format=FuncFormatter(format_percentage))
        cbar.ax.set_ylabel("Funding Rate", rotation=-90, va="bottom")

        ax.set_title(f"Hyperliquid Funding Rates - Window {window + 1}")
        fig.tight_layout()

        for i in range(len(y_ticks)):
            for j in range(len(x_ticks)):
                if i < len(data) and j < len(data[i]):
                    text = ax.text(
                        j,
                        i,
                        f"{data[i][j]:.4%}",
                        ha="center",
                        va="center",
                        color="black",
                        fontsize=6,
                    )

        plt.savefig("funding_heatmap_" + f"{window}" + ".png")

    plt.show()  # Display all the heatmaps at once


tokens = fetch_hyperliquid_tokens(fetch_hyperliquid_universe())

start_time = datetime.now().timestamp() - 24 * 60 * 60

historical_funding_data = fetch_hyperliquid_historical_funding(
    tokens, [start_time for _ in tokens]
)

create_heatmap(historical_funding_data, tokens, start_time)

import yfinance as yf
import streamlit as st
import numpy as np
from matplotlib.figure import Figure
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

@st.cache_data(ttl=3600)


def get_history_prices(symbol: str, period: str = "2y") -> np.ndarray:
    hist = yf.Ticker(symbol).history(period=period, auto_adjust=True)
    if hist.empty:
        raise ValueError(f"No data returned for '{symbol}'")
    return hist["Close"].dropna().to_numpy()

def historical_vol(prices: np.ndarray, window: int) -> float:
    if window < 2:
        raise ValueError("Window must be at least 2 days.")
    if len(prices) < window + 1:
        raise ValueError(f"Only {len(prices)} prices available; need {window + 1}.")
    prices = prices[-(window + 1):]
    return np.diff(np.log(prices)).std(ddof=1) * np.sqrt(252)

PNL_CMAP = LinearSegmentedColormap.from_list("pnl", ["#d62728", "white", "#2ca02c"], N=256)

PNL_CMAP_VAR = LinearSegmentedColormap.from_list("pnl_var", ["#ffc20a", "white", "#0c7bdc"], N=256)

def annotated_heatmap(data, title, x_vals, y_vals, xlabel, ylabel, cbar_label,
                      cmap, fmt="{:.2f}", center=None):
    """data shape: (len(y_vals), len(x_vals)): rows = y, columns = x.
    If center is given (e.g. 0 for P&L), that value gets the colormap's midpoint color."""
    fig = Figure(figsize=(9, 6))  # was: fig, ax = plt.subplots(figsize=(9, 6))
    ax = fig.subplots()

    norm = None
    if center is not None:
        # TwoSlopeNorm needs vmin < center < vmax, so nudge the ends if the data is one-sided
        eps = 1e-9
        vmin = min(float(data.min()), center - eps)
        vmax = max(float(data.max()), center + eps)
        norm = TwoSlopeNorm(vcenter=center, vmin=vmin, vmax=vmax)

    im = ax.imshow(data, origin="lower", aspect="auto", cmap=cmap, norm=norm)

    ax.set_title(title)
    ax.set_xticks(range(len(x_vals)))
    ax.set_xticklabels([f"{v:.2f}" for v in x_vals])
    ax.set_yticks(range(len(y_vals)))
    ax.set_yticklabels([f"{v:.2f}" for v in y_vals])

    ax.set_xlabel(xlabel, fontsize=14)
    ax.set_ylabel(ylabel, fontsize=14)
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label(cbar_label, fontsize=14)

    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            r, g, b, _ = im.cmap(im.norm(data[i, j]))        # the cell's actual color
            luminance = 0.299 * r + 0.587 * g + 0.114 * b
            color = "white" if luminance < 0.5 else "black"
            ax.text(j, i, fmt.format(data[i, j]),
                    ha="center", va="center", color=color, fontsize=8)

    fig.tight_layout()
    return fig


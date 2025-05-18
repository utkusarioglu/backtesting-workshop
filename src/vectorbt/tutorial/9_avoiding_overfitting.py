#!/opt/conda/envs/econ/bin/python

import numpy as np
from numba import njit
import vectorbt as vbt
from pathlib import Path
from datetime import datetime, timedelta
import os

vbt.settings["plotting"]["layout"].update(
    {
        "width": 1800,
        "height": 700,
        "template": "plotly_dark",
    }
)

PYTHONPATH = Path(os.environ.get("PYTHONPATH").split(":")[0])
ARTIFACTS_RELPATH = Path("artifacts/charts")
ARTIFACTS_ABSPATH = PYTHONPATH / ARTIFACTS_RELPATH

end_time = datetime.now()
start_time = end_time - timedelta(days=3)

close = vbt.YFData.download(
    # ["BTC-USD", "ETH-USD"],
    ["BTC-USD"],
    missing_index="drop",
    start=start_time,
    end=end_time,
    interval="1m",
).get("Close")

# ANKI DONE
splits, range_indices = close.vbt.range_split(n=100, range_len=1440)


def optimize_rsi(close, window, high, low):
    rsi = (
        vbt.IndicatorFactory.from_talib("RSI")
        .run(close, timeperiod=window)
        .real
    )
    return rsi < low, rsi > high


rsi_ind = vbt.IndicatorFactory(
    class_name="RSI",
    short_name="rsi",
    input_names=["close"],
    param_names=["window", "high", "low"],
    output_names=["entries", "exits"],
).from_apply_func(
    optimize_rsi,
    window=14,
    high=70,
    low=30,
)

step_size = 10
rsi_low = np.arange(10, 45, step=step_size, dtype=int)
rsi_high = np.arange(55, 95, step=step_size, dtype=int)
rsi_window = np.arange(10, 45, step=step_size, dtype=int)

rsi_res = rsi_ind.run(
    splits,
    window=rsi_window,
    low=rsi_low,
    high=rsi_high,
    param_product=True,
)

rsi_entries = rsi_res.entries
rsi_exits = rsi_res.exits
rsi_exits.iloc[-1, :] = True

rsi_pf = vbt.Portfolio.from_signals(
    splits,
    rsi_entries,
    rsi_exits,
    freq="1T",
    fees=1e-3,
)

fig = rsi_pf.total_return().vbt.volume(
    x_level="rsi_high",
    y_level="rsi_low",
    z_level="rsi_window",
    slider_level="split_idx",
)

fig.write_html(
    ARTIFACTS_ABSPATH / f"{Path(__file__).stem}-volume.html",
    post_script="document.body.style.background = '#151515'",
)

# Anki done
grouped = rsi_pf.total_return().groupby(level=["rsi_high", "rsi_low"]).mean()

fig = grouped.vbt.heatmap(x_level="rsi_high", y_level="rsi_low")

fig.write_html(
    ARTIFACTS_ABSPATH / f"{Path(__file__).stem}-heatmap.html",
    post_script="document.body.style.background = '#151515'",
)

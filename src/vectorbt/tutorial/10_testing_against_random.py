#!/opt/conda/envs/econ/bin/python

import numpy as np

# from numba import njit

import vectorbt as vbt
from src.utils.store import Store
from pathlib import Path
import pandas as pd
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

dfs = Store[pd.DataFrame]()

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

splits, range_indices = close.vbt.range_split(n=100, range_len=1440)

#
# RSI INDICATOR
#


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

rsi_res = rsi_ind.run(
    splits,
    window=20,
    low=20,
    high=80,
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

rsi_tr = rsi_pf.total_return()


splits, range_indices = close.vbt.range_split(n=100, range_len=1440)


#
# RANDOM INDICATOR
#
def rand_signal(close: pd.DataFrame):
    return np.random.randint(0, 2, size=close.shape)


rand_ind = vbt.IndicatorFactory(
    class_name="random",
    short_name="rnd",
    input_names=["close"],
    output_names=["value"],
).from_apply_func(rand_signal)

rand_signals = rand_ind.run(splits).value

rand_entries = rand_signals == 0
rand_exits = rand_signals == 1
rand_exits.iloc[-1, :] = True

rand_pf = vbt.Portfolio.from_signals(
    splits,
    entries=rand_entries,
    exits=rand_exits,
    freq="1T",
    # fees=1e-3,
)

rand_tr = rand_pf.total_return()

merged = pd.DataFrame({"rsi": list(rsi_tr), "rand": list(rand_tr)})

print(merged.median())

box = vbt.plotting.Box(
    data=merged,
    trace_names=["rsi", "rand"],
)

box.fig.write_html(
    ARTIFACTS_ABSPATH / f"{Path(__file__).stem}-box.html",
    post_script="document.body.style.background = '#151515'",
)

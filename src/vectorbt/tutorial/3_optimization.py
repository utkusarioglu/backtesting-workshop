#!/opt/conda/envs/econ/bin/python

# ANKI DONE

import os
from numba import njit
import vectorbt as vbt

from pathlib import Path
from datetime import datetime, timedelta
import numpy as np

PYTHONPATH = Path(os.environ.get("PYTHONPATH").split(":")[0])
ARTIFACTS_RELPATH = Path("artifacts/charts")
ARTIFACTS_ABSPATH = PYTHONPATH / ARTIFACTS_RELPATH
FILENAME = Path(__file__).stem

vbt.settings["plotting"]["layout"].update(
    {
        "width": 1800,
        "height": 900,
        "template": "plotly_dark",
    }
)


end_time = datetime.now()
start_time = end_time - timedelta(days=1)

close = vbt.YFData.download(
    ["BTC-USD", "ETH-USD"],
    missing_index="drop",
    start=start_time,
    end=end_time,
    interval="1m",
).get("Close")


@njit
def produce_trend(rsi, rsi_high: int, rsi_low: int):
    trend = np.where(rsi > rsi_high, 1, 0)
    trend = np.where(rsi < rsi_low, -1, trend)
    return trend


def talib_rsi_ind(close, rsi_window: int, rsi_high: int, rsi_low: int):
    rsi = (
        vbt.IndicatorFactory.from_talib("RSI")
        .run(close, rsi_window)
        .real.to_numpy()
    )
    return produce_trend(rsi, rsi_high, rsi_low)


ind = vbt.IndicatorFactory(
    class_name="talib_rsi",
    short_name="tr",
    input_names=["close"],
    param_names=["rsi_window", "rsi_high", "rsi_low"],
    output_names=["value"],
).from_apply_func(
    talib_rsi_ind,
    rsi_window=14,
    rsi_high=70,
    rsi_low=30,
)

signals = ind.run(
    close,
    rsi_window=np.arange(5, 20, step=1, dtype=np.int64),
    rsi_high=np.arange(70, 80, step=1, dtype=np.int64),
    rsi_low=np.arange(20, 30, step=1, dtype=np.int64),
    param_product=True,
)

entries = signals.value == 1
exits = signals.value == -1

pf = vbt.Portfolio.from_signals(close, entries, exits)
tr = pf.total_return()

print("\nSTATS")
print(pf[tr.idxmax()].stats())

pf[tr.idxmax()].plot().write_html(
    ARTIFACTS_ABSPATH / f"{FILENAME}_max.html",
    post_script="document.body.style.background = '#151515'",
)
pf[tr.idxmax()].trades.plot_pnl().write_html(
    ARTIFACTS_ABSPATH / f"{FILENAME}_pnl.html",
    post_script="document.body.style.background = '#151515'",
)
pf[tr.idxmax()].plot_cum_returns().write_html(
    ARTIFACTS_ABSPATH / f"{FILENAME}_cum_returns.html",
    post_script="document.body.style.background = '#151515'",
)

print("\nORDERS RECORDS")
print(pf.orders.records_arr)

print("\nTRADES RECORDS")
print(pf.trades.records_arr)

# OPTIMIZATION

from numba import njit
from src.utils.db import Db
import vectorbt as vbt
from src.utils.store import Store
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta

# import matplotlib.pyplot as plt
import numpy as np

ARTIFACTS_RELPATH = Path("artifacts/charts")
db = Db("vectorbt/tutorial")

dfs = Store[pd.DataFrame]()
inds = Store[vbt.indicators.IndicatorBase]()
signals = Store[any]()
pfs = Store[vbt.Portfolio]()
trs = Store[any]()
views = Store[any]()

end_time = datetime.now()
start_time = end_time - timedelta(days=1)

dfs.latest = "BTC-USD-Close", pd.DataFrame(
    vbt.YFData.download(
        ["BTC-USD", "ETH-USD"],
        missing_index="drop",
        start=start_time,
        end=end_time,
        interval="1m",
    ).get("Close")
)
dfs.latest

talib_rsi = vbt.IndicatorFactory.from_talib("RSI")


@njit
def produce_trend(rsi, rsi_high: int, rsi_low: int):
    trend = np.where(rsi > rsi_high, 1, 0)
    trend = np.where(rsi < rsi_low, -1, trend)
    return trend


def talib_rsi_ind(close, rsi_window: int, rsi_high: int, rsi_low: int):
    rsi = talib_rsi.run(close, rsi_window).real.to_numpy()
    return produce_trend(rsi, rsi_high, rsi_low)


ind = vbt.IndicatorFactory(
    class_name="talib_rsi",
    short_name="tr",
    input_names=["close"],
    param_names=["rsi_window", "rsi_high", "rsi_low"],
    output_names=["value"],
).from_apply_func(talib_rsi_ind, rsi_window=14, rsi_high=70, rsi_low=30)

signals = ind.run(
    dfs.latest,
    rsi_window=np.arange(5, 20, step=1, dtype=np.int64),
    rsi_high=np.arange(70, 80, step=1, dtype=np.int64),
    rsi_low=np.arange(20, 30, step=1, dtype=np.int64),
    param_product=True,
)

entries = signals.value == 1
exits = signals.value == -1

pf = vbt.Portfolio.from_signals(dfs.latest, entries, exits)
tr = pf.total_return()
print("\nSTATS")
print(pf[tr.idxmax()].stats())

pf[tr.idxmax()].plot().write_html(ARTIFACTS_RELPATH / "max.html")
pf[tr.idxmax()].trades.plot_pnl().write_html(ARTIFACTS_RELPATH / "pnl.html")
pf[tr.idxmax()].plot_cum_returns().write_html(
    ARTIFACTS_RELPATH / "cum_returns.html"
)

print("\nORDERS RECORDS")
print(pf.orders.records_arr)

print("\nTRADES RECORDS")
print(pf.trades.records_arr)

#!/opt/conda/envs/econ/bin/python

# ANKI DONE

import numpy as np
from numba import njit
import vectorbt as vbt
from src.utils.store import Store
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta
import os

vbt.settings["plotting"]["layout"].update(
    {
        "width": 1800,
        "height": 900,
        "template": "plotly_dark",
    }
)

PYTHONPATH = Path(os.environ.get("PYTHONPATH").split(":")[0])
ARTIFACTS_RELPATH = Path("artifacts/charts")
ARTIFACTS_ABSPATH = PYTHONPATH / ARTIFACTS_RELPATH
FILENAME = Path(__file__).stem

end_time = datetime.now()
start_time = end_time - timedelta(days=1)

df = pd.DataFrame(
    vbt.YFData.download(
        # ["BTC-USD", "ETH-USD"],
        ["BTC-USD"],
        missing_index="drop",
        start=start_time,
        end=end_time,
        interval="1m",
    ).get("Close")
)

talib_rsi = vbt.IndicatorFactory.from_talib("RSI")
# talib_ma = vbt.IndicatorFactory.from_talib("MA")
# ma_short = talib_ma.run(dfs.latest, timeperiod=[50, 100, 200])


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
    df,
    rsi_window=[14, 20],
    rsi_high=[80, 70],
    rsi_low=[20, 30],
    # param_product=True,
)

entries = signals.value == 1
exits = signals.value == -1

pf = vbt.Portfolio.from_signals(df, entries, exits)

pf[pf.total_return().idxmax()].plot(
    subplots=[
        "drawdowns",
        "gross_exposure",
        "trades",
    ]
).write_html(
    ARTIFACTS_ABSPATH / f"{FILENAME}.html",
    post_script="document.body.style.background = '#151515'",
)

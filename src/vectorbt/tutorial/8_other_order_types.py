#!/opt/conda/envs/econ/bin/python

# ANKI DONE

import numpy as np
from numba import njit
import vectorbt as vbt
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta
import os

vbt.settings["plotting"]["layout"].update(
    {
        "width": 1840,
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


@njit
def produce_long_trend(rsi, rsi_high: int, rsi_low: int):
    trend = np.where(rsi > rsi_high, 1, 0)
    trend = np.where(rsi < rsi_low, -1, trend)
    return trend


@njit
def produce_short_trend(close, ma):
    trend = np.where(ma > close, 1, 0)
    trend = np.where(ma < close, -1, trend)
    return trend


def long_short_ind(
    close,
    rsi_window: int,
    rsi_high: int,
    rsi_low: int,
    ma_window: int,
):
    rsi = (
        vbt.IndicatorFactory.from_talib("RSI")
        .run(close, rsi_window)
        .real.to_numpy()
    )
    ma = (
        vbt.IndicatorFactory.from_talib("MA")
        .run(close, ma_window)
        .real.to_numpy()
    )
    return (
        produce_long_trend(rsi, rsi_high, rsi_low),
        produce_short_trend(close, ma),
    )


ind = vbt.IndicatorFactory(
    class_name="talib_rsi",
    short_name="tr",
    input_names=["close"],
    param_names=["rsi_window", "rsi_high", "rsi_low", "ma_window"],
    output_names=["long", "short"],
).from_apply_func(
    long_short_ind,
    rsi_window=14,
    rsi_high=70,
    rsi_low=30,
    ma_window=40,
)

STEP = 10
signals = ind.run(
    close,
    rsi_window=np.arange(14, 30, step=STEP, dtype=np.int64),
    rsi_high=np.arange(70, 90, step=STEP, dtype=np.int64),
    rsi_low=np.arange(20, 40, step=STEP, dtype=np.int64),
    ma_window=np.arange(50, 200, step=STEP, dtype=np.int64),
    param_product=True,
)

long_entries = signals.long == 1
long_exits = signals.long == -1
long_exits.iloc[-1, :] = True
short_entries = signals.short == 1
short_exits = signals.short == -1
short_exits.iloc[-1, :] = True

# pf = vbt.Portfolio.from_signals(
#     close,
#     entries=long_entries,
#     exits=long_exits,
#     # Stop loss
#     sl_stop=5e-3,
#     # Trailing stop loss
#     sl_trail=True,
#     # take profit
#     tp_stop=1e-1,
# )

pf = vbt.Portfolio.from_signals(
    close,
    entries=long_entries,
    exits=long_exits,
    # Stop loss
    sl_stop=5e-3,
    # Trailing stop loss
    sl_trail=True,
    # take profit
    tp_stop=1e-2,
    # Reversal on stop exit
    upon_stop_exit=vbt.portfolio.enums.StopExitMode.Reverse,
)

# pf = vbt.Portfolio.from_signals(
#     df,
#     # entries=entries,
#     # exits=exits,
#     short_entries=long_entries,
#     short_exits=long_exits,
#     # Stop loss
#     sl_stop=5e-3,
#     # Trailing stop loss
#     sl_trail=True,
# )

pf = vbt.Portfolio.from_signals(
    close,
    entries=long_entries,
    exits=long_exits,
    short_entries=short_entries,
    short_exits=short_exits,
    upon_dir_conflict=vbt.portfolio.enums.DirectionConflictMode.Short,
)

# fig = pf[pf.total_return().idxmax()].plot()
fig = pf.plot(column=pf.total_return().idxmax())

fig.write_html(
    ARTIFACTS_ABSPATH / Path(Path(__file__).stem + ".html"),
    post_script="document.body.style.background = '#151515'",
)

with pd.option_context(
    "display.expand_frame_repr",
    None,
    "display.max_rows",
    None,
    "display.max_columns",
    None,
):
    print(pf.stats(silence_warnings=True))
    print(pf[pf.total_return().idxmax()].stats(silence_warnings=True))

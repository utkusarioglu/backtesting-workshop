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

dfs = Store[pd.DataFrame]()

end_time = datetime.now()
start_time = end_time - timedelta(days=1)

dfs.latest = "BTC-USD-Close", pd.DataFrame(
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

ma_inds = vbt.IndicatorFactory.from_talib("MA").run(
    dfs.latest, timeperiod=[50, 100, 200]
)


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
    rsi_window=[14, 20],
    rsi_high=[80, 70],
    rsi_low=[20, 30],
    # param_product=True,
)

entries = signals.value == 1
exits = signals.value == -1

# PLOT_PARAMS = {
#     # "template": "plotly_dark",
#     "width": 1600,
#     "height": 800,
#     "trace_kwargs": {
#         "name": "Price",
#         "line": {
#             "color": "white",
#         },
#     },
# }

pf = vbt.Portfolio.from_signals(dfs.latest, entries, exits)

fig = pf[pf.total_return().idxmin()].plot(
    subplots=[
        (
            "MA",
            {
                "title": "Moving averages",
                "yaxis_kwargs": {
                    "title": "Price",
                },
            },
        ),
        "drawdowns",
        "gross_exposure",
        "trades",
    ]
)

for ma in ma_inds.real.columns:
    vbt.plotting.Scatter(
        data=ma_inds.real[ma],
        x_labels=ma_inds.real.index,
        trace_names=[f"MA: {ma}"],
        fig=fig,
        add_trace_kwargs={
            "row": 1,
            "col": 1,
        },
    )

# fig.show()

fig.write_html(
    ARTIFACTS_ABSPATH / f"{Path(__file__).stem}.html",
    post_script="document.body.style.background = '#151515'",
)

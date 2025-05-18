#!/opt/conda/envs/econ/bin/python

# ANKI DONE
import vectorbt as vbt
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta
import os

PYTHONPATH = Path(os.environ.get("PYTHONPATH").split(":")[0])
ARTIFACTS_RELPATH = Path("artifacts/charts")
ARTIFACTS_ABSPATH = PYTHONPATH / ARTIFACTS_RELPATH
FILENAME = Path(__file__).stem

# vbt.settings["plotting"]["layout"].update(
#     {
#         "width": 1800,
#         "height": 900,
#         "template": "plotly_dark",
#     }
# )

end_time = datetime.now()
start_time = end_time - timedelta(days=1)

df = vbt.YFData.download(
    ["BTC-USD"],
    missing_index="drop",
    start=start_time,
    end=end_time,
    interval="1m",
).get("Close")


ma_short = vbt.IndicatorFactory.from_talib("MA").run(
    df, timeperiod=[50, 100, 200]
)

PLOT_PARAMS = {
    "template": "plotly_dark",
    "width": 1900,
    "height": 900,
    "trace_kwargs": {
        "name": "Price",
        "line": {
            "color": "red",
        },
    },
}

fig = df.vbt.plot(**PLOT_PARAMS)

for col in ma_short.real.columns:
    fig.add_scatter(
        x=ma_short.real.index,
        y=ma_short.real[col],
        mode="lines",
        name=f"MA ({col})",
        line={"dash": "dot"},
    )

fig.write_html(
    ARTIFACTS_ABSPATH / f"{FILENAME}_ma_50_100_200.html",
    post_script="document.body.style.background = '#151515'",
)

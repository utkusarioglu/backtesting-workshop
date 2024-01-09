import vectorbt as vbt
from src.config import ARTIFACTS_ABSPATH

PLOT_ARTIFACTS_PATH = f"{ARTIFACTS_ABSPATH}/plots"


def apply_vbt_settings():
    vbt.settings["plotting"]["layout"] = {
        **vbt.settings["plotting"]["layout"],
        "width": 630,
        "template": "plotly_dark",
        "plot_bgcolor": "#080808",
        "paper_bgcolor": "#151515",
        "margin": dict(l=0, r=0, t=5, b=5),
    }


def get_backtesting_plot_kwargs(stats):
    strategy = stats._strategy
    name = strategy.__class__.__name__
    c = set(dir(strategy.__class__))
    base = set(dir(strategy.__class__.__base__))
    variables = c.difference(base)
    values = "-".join([str(getattr(strategy, v)) for v in variables])
    return {
        "filename": f"{PLOT_ARTIFACTS_PATH}/{name}-{values}.html",
        "open_browser": False,
    }

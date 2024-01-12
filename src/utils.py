from os.path import join
from typing import Any
import vectorbt as vbt
from src.config import PLOT_ARTIFACTS_ABSPATH


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
        "filename": join(PLOT_ARTIFACTS_ABSPATH, f"{name}-{values}.html"),
        "open_browser": False,
    }


# TODO get rid of `Any`
def reload_module(module_relpath: str, attribute: str | None = None) -> Any:
    import sys
    import importlib

    if sys.modules.get(module_relpath) is not None:
        del sys.modules[module_relpath]
    module = importlib.import_module(module_relpath.replace("/", "."))
    if attribute:
        return getattr(module, attribute)
    return module

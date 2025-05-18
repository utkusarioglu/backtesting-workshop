from os.path import join
from typing import Any
import vectorbt as vbt
from src.config import config
import matplotlib as mpl
from matplotlib import style

# from matplotlib import style, rcParams


def apply_matplotlib_settings():
    style.use("dark_background")
    # style.use(
    #     {
    #         "axes.facecolor": "#1a1a1a",
    #         "axes.edgecolor": "gray",
    #         "axes.labelcolor": "white",
    #         "text.color": "white",
    #         "xtick.color": "#555555",
    #         "ytick.color": "#555555",
    #         "grid.color": "gray",
    #         # "figure.facecolor": "#1a1a1a",
    #         "figure.edgecolor": "#1a1a1a",
    #         # "savefig.facecolor": "#1a1a1a",
    #         # "savefig.edgecolor": "#1a1a1a",
    #     }
    # )
    # rcParams["axes.facecolor"] = "#050505"
    # rcParams["figure.facecolor"] = "#151515"
    mpl.rcParams = {
        **mpl.rcParams,
        "axes.facecolor": "#111",
        "figure.facecolor": "#151515",
        # "axes.facecolor": "#1a1a1a",
        "axes.edgecolor": "gray",
        "axes.labelcolor": "white",
        "text.color": "white",
        "xtick.color": "#666666",
        "ytick.color": "#666666",
        "grid.color": "gray",
        # "figure.facecolor": "#1a1a1a",
        "figure.edgecolor": "#1a1a1a",
        # "savefig.facecolor": "#1a1a1a",
        # "savefig.edgecolor": "#1a1a1a",
    }


def apply_vbt_settings():
    vbt.settings["plotting"]["layout"] = {
        **vbt.settings["plotting"]["layout"],
        "width": 630,
        "template": "plotly_dark",
        "plot_bgcolor": config["AXES_FACECOLOR"],
        "paper_bgcolor": config["FIGURE_FACECOLOR"],
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
        "filename": join(
            config["PLOT_ARTIFACTS_ABSPATH"], f"{name}-{values}.html"
        ),
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

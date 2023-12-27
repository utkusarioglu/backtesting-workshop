PLOT_ARTIFACTS_PATH = "../artifacts/plots"


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

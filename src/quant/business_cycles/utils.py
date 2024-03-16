import matplotlib.pyplot as plt


def plot_growth(data, countries, events, figure_params={}):
    fig, ax = plt.subplots(**figure_params)
    for country in countries:
        data.loc[country].plot(ax=ax)
    ylim = ax.get_ylim()[1]
    for event in events:
        ax.axvspan(event["start"], event["end"], color="gray", alpha=0.2)
        ax.text(
            (event["end"] + event["start"]) / 2,
            ylim + 0.3,
            event["title"],
            va="bottom",
            ha="center",
        )
    fig.legend(loc="lower center", ncol=5, bbox_to_anchor=[0.5, -0.1])
    fig.show()

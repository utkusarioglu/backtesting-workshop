import pandas as pd
import matplotlib.cm as cm
import numpy as np
from collections import namedtuple
import matplotlib.pyplot as plt


Event = namedtuple("Event", ["year_range", "y_text", "text", "color", "ymax"])


def get_data(**excel_args):
    data_url = "https://github.com/QuantEcon/lecture-python-intro/raw/main/lectures/datasets/mpd2020.xlsx"
    data = pd.read_excel(data_url, **excel_args)
    return data


def get_country_active_years(data):
    country_years = pd.DataFrame(
        columns=["country", "first_year", "latest_year"]
    )
    for country in data.country.unique():
        country_data = data[data["country"] == country]["year"]
        min_year = country_data.min()
        max_year = country_data.max()
        country_years.loc[len(country_years.index)] = [
            country,
            min_year,
            max_year,
        ]
    country_years = country_years.set_index("country")
    return country_years


def get_code_to_name(data):
    code_to_name = (
        data[["countrycode", "country"]]
        .drop_duplicates()
        .set_index("countrycode")
    )
    return code_to_name


def get_gdp_pc(data):
    gdp_pc = data.set_index(["countrycode", "year"])["gdppc"].unstack()
    return gdp_pc


def create_color_map(data):
    # Color map
    colors = cm.tab20(np.linspace(0, 0.95, len(data["countrycode"])))
    color_mapping = {
        country: color for country, color in zip(data["countrycode"], colors)
    }
    return color_mapping


def plot_countries(
    ax,
    color_mapping,
    country_list,
    country_codes,
    gdp_pc,
    start_year,
    end_year,
    log_scale=True,
):
    for country in country_list:
        ax.spines.top.set_visible(False)
        ax.spines.right.set_visible(False)
        ax.set_xlabel("Year")
        ax.set_ylabel("International Dollars")
        country_gdp_pc = gdp_pc.loc[country]
        interpolated = country_gdp_pc.loc[start_year:end_year].interpolate()[
            country_gdp_pc.isnull()
        ]
        if log_scale:
            ax.set_yscale("log")
        ax.plot(
            interpolated,
            linestyle="--",
            color=color_mapping[country],
        )
        ax.plot(
            country_gdp_pc.loc[start_year:end_year],
            color=color_mapping[country],
            label=country_codes.loc[country]["country"],
        )


def draw_events(ax, events):
    t_params = {"fontsize": 9, "va": "baseline", "ha": "center"}
    ylim = ax.get_ylim()[1]
    for event in events:
        event_mid = sum(event.year_range) / 2
        ax.text(
            event_mid,
            ylim * event.y_text,
            event.text,
            color=event.color,
            **t_params
        )
        ax.axvspan(*event.year_range, color=event.color, alpha=0.2)
        ax.axvline(
            event_mid,
            ymin=1,
            ymax=event.ymax,
            color=event.color,
            clip_on=False,
            alpha=0.15,
        )


def plot_with_events(
    countries,
    country_codes,
    gdp_pc,
    start_year,
    end_year,
    events,
    color_mapping,
    log_scale=True,
):
    fig, ax = plt.subplots()
    # countries = ["CHN", "GBR", "USA", "IND"]
    plot_countries(
        ax=ax,
        color_mapping=color_mapping,
        country_list=countries,
        country_codes=country_codes,
        gdp_pc=gdp_pc,
        start_year=start_year,
        end_year=end_year,
        log_scale=log_scale,
    )
    # ylim = ax.get_ylim()[1]
    # events = define_events(ylim)
    draw_events(ax, events)
    fig.set_figwidth(18)
    ax.legend()
    fig.show()

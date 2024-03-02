import pandas as pd
import matplotlib.cm as cm
import numpy as np
from collections import namedtuple

Event = namedtuple("Event", ["year_range", "y_text", "text", "color", "ymax"])


def get_data():
    data_url = "https://github.com/QuantEcon/lecture-python-intro/raw/main/lectures/datasets/mpd2020.xlsx"
    data = pd.read_excel(data_url, sheet_name="Full data")
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

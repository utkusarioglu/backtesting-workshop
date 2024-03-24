import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.dates as mdates


def plot_countries(data, countries, start_year, end_year, y_scale=None):
    fig, ax = plt.subplots(figsize=(20, 6))
    data_before_1915 = data[data.index < end_year]

    for country in countries:
        ax.plot(
            data_before_1915.index,
            data_before_1915[country],
            label=country,
        )
    if y_scale:
        ax.set_yscale(y_scale)
    ax.set_xlim(start_year, end_year)
    ax.set_xlabel("Year")
    ax.set_ylabel("Inflation\n Index: 1913 = 100")

    fig.legend(loc="lower center", ncols=6, bbox_to_anchor=(0.5, -0.05))
    fig.show()


def process_entry(entry):
    "Clean each entry of a dataframe."

    if type(entry) == str:
        # remove leading and trailing whitespace
        entry = entry.strip()
        # remove comma
        entry = entry.replace(",", "")

        # remove HTML markers
        item_to_remove = ["<s>a</s>", "<s>c</s>", "<s>d</s>", "<s>e</s>"]

        # <s>b</s> represents a billion
        if "<s>b</s>" in entry:
            entry = entry.replace("<s>b</s>", "")
            entry = float(entry) * 1e9
        else:
            for item in item_to_remove:
                if item in entry:
                    entry = entry.replace(item, "")
    return entry


def process_df(df):
    "Clean and reorganize the entire dataframe."

    # remove HTML markers from column names
    for item in ["<s>a</s>", "<s>c</s>", "<s>d</s>", "<s>e</s>"]:
        df.columns = df.columns.str.replace(item, "")

    # convert years to int
    df["Year"] = df["Year"].apply(lambda x: int(x))

    # set index to datetime with year and month
    df = df.set_index(
        pd.to_datetime(
            (df["Year"].astype(str) + df["Month"].astype(str)), format="%Y%B"
        )
    )
    df = df.drop(["Year", "Month"], axis=1)

    # handle duplicates by keeping the first
    df = df[~df.index.duplicated(keep="first")]

    # convert attribute values to numeric
    df = df.applymap(lambda x: float(x) if x != "—" else np.nan)

    # finally, we only focus on data between 1919 and 1925
    mask = (df.index >= "1919-01-01") & (df.index < "1925-01-01")
    df = df.loc[mask]

    return df


def exchange_rate_plot(p_seq, e_seq, index, labs, ax):
    "Generate plots for price and exchange rates."

    p_lab, e_lab = labs

    # plot price and exchange rates
    ax.plot(index, p_seq, label=p_lab, color="tab:blue", lw=2)

    # add a new axis
    ax1 = ax.twinx()
    ax1.plot([None], [None], label=p_lab, color="tab:blue", lw=2)
    ax1.plot(index, e_seq, label=e_lab, color="tab:orange", lw=2)

    # set log axes
    ax.set_yscale("log")
    ax1.set_yscale("log")

    # define the axis label format
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=5))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    for label in ax.get_xticklabels():
        label.set_rotation(45)

    # set labels
    ax.set_ylabel("Price level")
    ax1.set_ylabel("Exchange rate")

    ax1.legend(loc="upper left")

    return ax1


def inflation_rate_plot(p_seq, index, ax):
    "Generate plots for inflation rates."

    #  Calculate the difference of log p_seq
    log_diff_p = np.diff(np.log(p_seq))

    # graph for the difference of log p_seq
    ax.scatter(
        index[1:], log_diff_p, label="Monthly inflation rate", color="tab:grey"
    )

    # calculate and plot moving average
    diff_smooth = pd.DataFrame(log_diff_p).rolling(3, center=True).mean()
    ax.plot(
        index[1:],
        diff_smooth,
        label="Moving average (3 period)",
        alpha=0.5,
        lw=2,
    )
    ax.set_ylabel("Inflation rate")

    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=5))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

    for label in ax.get_xticklabels():
        label.set_rotation(45)

    ax.legend(loc="upper left")

    return ax


def get_er_inflation_data():
    # import data
    data_url = "/".join(
        [
            "https://github.com",
            "QuantEcon/lecture-python-intro",
            "raw/main",
            "lectures/datasets/chapter_3.xlsx",
        ]
    )
    xls = pd.ExcelFile(data_url)

    # select relevant sheets
    sheet_index = [(2, 3, 4), (9, 10), (14, 15, 16), (21, 18, 19)]

    # remove redundant rows
    remove_row = [(-2, -2, -2), (-7, -10), (-6, -4, -3), (-19, -3, -6)]

    # unpack and combine series for each country
    df_list = []

    for i in range(4):

        indices, rows = sheet_index[i], remove_row[i]

        # apply process_entry on the selected sheet
        sheet_list = [
            pd.read_excel(xls, "Table3." + str(ind), header=1)
            .iloc[:row]
            .applymap(process_entry)
            for ind, row in zip(indices, rows)
        ]

        sheet_list = [process_df(df) for df in sheet_list]
        df_list.append(pd.concat(sheet_list, axis=1))

    return df_list


def plot_er_prices_inflation(
    price_sequence, exchange_rate_sequence, index, labels
):
    # create plot
    fig, [ax1, ax2] = plt.subplots(2, figsize=(10, 10), sharex=True)
    exchange_rate_plot(
        price_sequence, exchange_rate_sequence, index, labels, ax1
    )
    inflation_rate_plot(price_sequence, index, ax2)
    plt.tight_layout()
    plt.show()

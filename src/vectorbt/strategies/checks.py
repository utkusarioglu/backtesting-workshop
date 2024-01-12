from typing import TypedDict
import vectorbt as vbt
import numpy as np
import pandas as pd
from datetime import datetime, timedelta


class SplitParams(TypedDict):
    n: int
    range_len: int


class Checks:
    def __init__(self, base: str, tickers: list[str]) -> None:
        self.base = base
        self.tickers = tickers
        self.pairs = [f"{t}-{base}" for t in tickers]
        self.data = {"pd": {}, "np": {}}
        self.indicators = {}
        self.results = {}

    def get_data_from_yf(self, days, interval, split: SplitParams):
        print("Pulling new data…")
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)

        self.data["pd"]["prices"] = vbt.YFData.download(
            self.pairs,
            missing_index="drop",
            start=start_time,
            end=end_time,
            interval=interval,
        ).get("Close")

        range_prices, range_indexes = self.__prepare_ranges(
            self.data["pd"]["prices"], split
        )

        self.data["pd"]["ranges"] = {
            "prices": range_prices,
            "indexes": range_indexes,
        }

    def __prepare_ranges(self, data, split: SplitParams):
        return data.vbt.range_split(n=split["n"], range_len=split["range_len"])

    def set_data(self, data: pd.DataFrame, split: SplitParams | None = None):
        self.data["pd"]["prices"] = data

        if split:
            range_prices, range_indexes = self.__prepare_ranges(
                self.data["pd"]["prices"], split
            )

            self.data["pd"]["ranges"] = {
                "prices": range_prices,
                "indexes": range_indexes,
            }

    def __create_hypothesis_indicator(self) -> None:
        def rsi_signal(close, rsi_window, rsi_entry, rsi_exit):
            rsi = (
                vbt.IndicatorFactory.from_talib("RSI")
                .run(close, timeperiod=rsi_window)
                .real
            )

            return rsi < rsi_entry, rsi > rsi_exit

        self.indicators["hypothesis"] = vbt.IndicatorFactory(
            class_name="Hypothesis",
            short_name="hp",
            input_names=["close"],
            param_names=["rsi_window", "rsi_entry", "rsi_exit"],
            output_names=["entry_signals", "exit_signals"],
        ).from_apply_func(rsi_signal, rsi_window=14, rsi_entry=30, rsi_exit=70)

    def __create_control_indicator(self) -> None:
        def random_signal(close):
            values = np.random.randint(0, 2, size=close.shape)
            return values == 1, values == 0

        self.indicators["control"] = vbt.IndicatorFactory(
            class_name="Control",
            short_name="c",
            input_names=["close"],
            output_names=["entry_signals", "exit_signals"],
        ).from_apply_func(random_signal)

    def run_hypothesis_on_range(
        self, close_positions: bool = False, **variant_kwargs
    ):
        self.__create_hypothesis_indicator()
        result = self.indicators["hypothesis"].run(
            param_product=True,
            **variant_kwargs,
        )
        self.results["hypothesis"] = result
        if close_positions:
            self.results["hypothesis"].exit_signals.iloc[-1, :] = True
        return self.results["hypothesis"]

    def run_hypothesis_on_single(self, close_positions: bool = False):
        self.__create_hypothesis_indicator()
        result = self.indicators["hypothesis"].run(self.data["pd"]["prices"])
        self.results["hypothesis"] = result
        if close_positions:
            self.results["hypothesis"].exit_signals.iloc[-1, :] = True
        return self.results["hypothesis"]

    def run_control(self, close_positions: bool = False):
        self.__create_control_indicator()
        result = self.indicators["control"].run(
            self.data["pd"]["ranges"]["prices"], param_product=True
        )
        self.results["control"] = result
        if close_positions:
            self.results["control"].exit_signals.iloc[-1, :] = True
        return self.results["control"]

    def create_portfolio(self, **portfolio_kwargs):
        self.portfolio = vbt.Portfolio.from_signals(
            # self.data["pd"]["ranges"]["prices"],
            **portfolio_kwargs
        )
        return self.portfolio

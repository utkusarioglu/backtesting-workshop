import vectorbt as vbt
import pandas as pd
from os.path import isfile
import numpy as np
from datetime import datetime, timedelta
from numba import njit
from src.config import ARTIFACTS_ABSPATH
from src.utils import apply_vbt_settings

apply_vbt_settings()


class OrderTypes:
    def __init__(
        self, base: str, tickers: list[str], data_filename: str
    ) -> None:
        self.base = base
        self.tickers = tickers
        self.pairs = [f"{t}-{base}" for t in tickers]
        self.data_filename = data_filename
        self.data_file_relpath = "/".join(
            [ARTIFACTS_ABSPATH, self.data_filename]
        )
        self.data = dict(pd=dict(), np=dict())

    def get_data(self, days, interval, use_cache=True):
        if isfile(self.data_file_relpath) and use_cache:
            print(f"Using data from {self.data_filename}")
            self.prices = pd.read_json(self.data_file_relpath)
            # self.prices.set_index("Datetime", inplace=True)
            return self.prices
        print(f"Pulling new data to {self.data_filename}…")
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)

        self.prices = vbt.YFData.download(
            self.pairs,
            missing_index="drop",
            start=start_time,
            end=end_time,
            interval=interval,
        ).get("Close")

        self.prices.to_json(self.data_file_relpath)
        return self.prices

    def create_indicator(self):
        RSI = vbt.IndicatorFactory.from_talib("RSI")

        @njit
        def produce_signal(
            rsi,
            #    ma,
            close,
            entry_threshold,
            exit_threshold,
        ):
            trend = np.where(rsi > exit_threshold, -1, 0)
            trend = np.where((rsi < entry_threshold), 1, trend)
            return trend

        def custom_indicator(
            close,
            rsi_window,
            # rsi_period,
            # ma_window,
            entry_threshold,
            exit_threshold,
        ):
            rsi_pd = RSI.run(close, rsi_window)
            # close_resampled = close.resample(rsi_period).last()
            # rsi_unaligned = RSI.run(close_resampled, rsi_window).real
            # rsi_pd, _ = rsi_unaligned.align(
            #     close, broadcast_axis=0, method="ffill", join="right", axis=0
            # )
            # ma_pd = vbt.MA.run(close, ma_window)

            # self.data["ma"] = {"pd": ma_pd, "np": ma_pd.ma.to_numpy()}
            self.data["rsi"] = {"pd": rsi_pd, "np": rsi_pd.real.to_numpy()}

            close = close.to_numpy()

            return produce_signal(
                self.data["rsi"]["np"],
                # self.data["ma"]["np"],
                close,
                entry_threshold,
                exit_threshold,
            )

        self.indicator = vbt.IndicatorFactory(
            class_name="Combination",
            short_name="comb",
            input_names=["close"],
            param_names=[
                "rsi_window",
                # "rsi_period",
                # "ma_window",
                "entry_threshold",
                "exit_threshold",
            ],
            output_names=["trend"],
        ).from_apply_func(
            custom_indicator,
            rsi_window=14,
            # ma_window=50,
            entry_threshold=30,
            exit_threshold=70,
            keep_pd=True,
        )

    def run(self, **variant_kwargs):
        self.result = self.indicator.run(
            self.prices, param_product=True, **variant_kwargs
        )
        trend = self.result.trend
        self.entries = trend == 1.0
        self.exits = trend == -1.0

    def create_portfolio(self, **portfolio_kwargs):
        self.portfolio = vbt.Portfolio.from_signals(
            self.prices,
            # entries=self.entries,
            # exits=self.exits,
            # short_entries=self.exits,
            # short_exits=self.entries,
            **portfolio_kwargs,
        )
        return self.portfolio

from os.path import join
from sys import exit
import pandas as pd
from typing import Literal
from binance.client import Client
from src.vectorbt.strategies.checks import Checks
from time import sleep

# from src.config import (
#     BINANCE_SPOT_TESTNET_API_KEY,
#     BINANCE_SPOT_TESTNET_SECRET_KEY,
#     ARTIFACTS_ABSPATH,
# )
from src.config import config
from src.vectorbt.bot.constants import (
    SOURCE_COLUMNS,
    DATETIME_COLUMNS,
    NUMERIC_COLUMNS,
)
from src.vectorbt.bot.account import Account
from src.vectorbt.bot.logger import Logger


Currency = Literal["BTC", "ETH", "USDT"]


class BinanceTestnet:
    def __init__(
        self,
        api_key: str,
        secret_key: str,
        logs_folder_abspath: str,
        data_file_abspath: str,
    ) -> None:
        self.client = Client(
            api_key,
            secret_key,
            testnet=True,
        )
        self.logs_folder_abspath = logs_folder_abspath
        self.data_file_abspath = data_file_abspath

    def get_balance(self, asset: Currency):
        return self.client.get_asset_balance(asset=asset)

    def get_klines(self, asset: Currency, base: Currency):
        klines = self.client.get_historical_klines(
            f"{asset}{base}", Client.KLINE_INTERVAL_1MINUTE, "1 hours ago UTC"
        )
        df = pd.DataFrame(
            klines,
            columns=SOURCE_COLUMNS,
        )
        df[DATETIME_COLUMNS] = df[DATETIME_COLUMNS].apply(
            pd.to_datetime, unit="ms"
        )
        df[NUMERIC_COLUMNS] = df[NUMERIC_COLUMNS].apply(pd.to_numeric)
        df = df.set_index("Open time")
        return df

    def run(
        self,
        evaluate,
        asset: Currency,
        base: Currency,
        sleep_seconds: int,
        quantity: float,
    ):
        logger = Logger(self.logs_folder_abspath)
        account = Account(self.data_file_abspath)
        logger.info("Run started")
        while True:
            try:
                is_buying = account.is_buying()
                klines = self.get_klines(asset, base)
                entry_signals, exit_signals = evaluate(klines, asset, base)
                entry_signal = entry_signals["Close"].iloc[-1]
                exit_signal = exit_signals["Close"].iloc[-1]

                if entry_signal or exit_signal:
                    logger.info(
                        " ".join(
                            [
                                "Received signals, entry:",
                                f"{entry_signal},",
                                f"exit: {exit_signal}",
                            ]
                        )
                    )

                order = None
                if is_buying and entry_signal:
                    logger.info(f"Buying {asset}")
                    order = self.client.order_market_buy(
                        symbol=asset, quantity=quantity
                    )
                    account.set_is_buying(False)

                if not is_buying and exit_signal:
                    logger.info(f"Selling {asset}")
                    order = self.client.order_market_sell(
                        symbol=asset, quantity=quantity
                    )
                    account.set_is_buying(True)

                if order and order["orderId"]:
                    while order["status"] != "FILLED":
                        logger.info(
                            f"Awaiting confirmation for {order['orderId']}"
                        )
                        order = self.client.get_order(
                            symbol=asset, orderId=order["orderId"]
                        )
                        sleep(3)

                    order_cost = [
                        float(fill["price"]) * float(fill["qty"])
                        for fill in order["fills"]
                    ]

                    print(order)
                    print("order cost:", order_cost)

                logger.info(f"Sleeping for {sleep_seconds}s")
                sleep(sleep_seconds)

            except Exception as e:
                logger.info("Run interrupted")
                e_str = str(e)
                print(e_str)
                logger.error(e_str)
                exit(1)


def evaluation_method(klines, asset, base):
    prices = klines[["Close"]]
    c = Checks(base, [asset])
    c.set_data(prices)
    hp = c.run_hypothesis_on_single(close_positions=False)
    return hp.entry_signals, hp.exit_signals


def main():
    b = BinanceTestnet(
        config["BINANCE_SPOT_TESTNET_API_KEY"],
        config["BINANCE_SPOT_TESTNET_SECRET_KEY"],
        join(config["ARTIFACTS_ABSPATH"], "bot/logs"),
        join(config["ARTIFACTS_ABSPATH"], "bot/account_data.json"),
    )
    b.run(evaluation_method, "BTC", "USDT", 30, 0.01)


main()

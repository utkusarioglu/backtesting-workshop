from os import environ
from os.path import join
from dotenv import load_dotenv

load_dotenv()

REQUIRED_ENV_VARS = [
    "ARTIFACTS_ABSPATH",
    "ASSETS_ABSPATH",
    "BINANCE_SPOT_TESTNET_API_KEY",
    "BINANCE_SPOT_TESTNET_SECRET_KEY",
]

env = {
    key: value for [key, value] in environ.items() if key in REQUIRED_ENV_VARS
}

locals().update(env)

for required_env_var in REQUIRED_ENV_VARS:
    if required_env_var not in locals():
        raise ValueError(f"env.{required_env_var} is required")

PLOT_ARTIFACTS_ABSPATH = join(env["ARTIFACTS_ABSPATH"], "plots")

from os.path import dirname
from os import path, makedirs
from json import dumps, load


class Account:
    DEFAULT_ACCOUNT_CONTENT = {"is_buying": True, "assets": {}}

    def __init__(self, data_file_abspath: str) -> None:
        self.data_file_abspath = data_file_abspath
        data_file_dirname = dirname(data_file_abspath)
        makedirs(data_file_dirname, exist_ok=True)
        if not path.exists(self.data_file_abspath):
            self.__create_account()

    def __create_account(self):
        self.__update_account(self.DEFAULT_ACCOUNT_CONTENT)

    def __load_account(self):
        with open(self.data_file_abspath, "r") as f:
            return load(f)

    def is_buying(self) -> bool:
        return self.__load_account()["is_buying"]

    def set_is_buying(self, state: bool):
        account = self.__load_account()
        account["is_buying"] = state
        self.__update_account(account)

    def __update_account(self, account):
        with open(self.data_file_abspath, "w") as f:
            f.write(dumps(account))

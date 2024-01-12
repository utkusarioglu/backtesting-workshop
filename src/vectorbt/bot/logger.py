from os import makedirs
from datetime import datetime
from os.path import join


class Logger:
    def __init__(self, logs_folder_abspath: str) -> None:
        self.logs_folder_abspath = logs_folder_abspath
        makedirs(self.logs_folder_abspath, exist_ok=True)

    def __get_time(self):
        now = datetime.now()
        date = now.strftime("%Y-%m-%d")
        time = now.strftime("%H-%M-%s")
        return date, time

    def __write_log(self, severity: str, date: str, time: str, content: str):
        with open(join(self.logs_folder_abspath, f"{date}.log"), "a+") as f:
            f.write(f"[{severity}] {date} {time}: {content}\n")

    def info(self, content: str):
        date, time = self.__get_time()
        self.__write_log("INFO", date, time, content)
        print("info:", content)

    def error(self, content: str):
        date, time = self.__get_time()
        self.__write_log("ERROR", date, time, content)

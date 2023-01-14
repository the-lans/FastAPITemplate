import logging
from os.path import join, isfile
from typing import Optional

from backend.config import DATA_DIR, ArgParse
from backend.library.func import new_file


class MainLogger:
    _main_logger: Optional[logging.Logger] = None

    def __init__(self, name: str, filename: str = None):
        self._logger: Optional[logging.Logger] = None
        self._name = name
        self._log_filename = filename if filename else f'log_{name}.log'

    @property
    def logger(self):
        return self._logger

    @property
    def log_path(self):
        return join(DATA_DIR, self._log_filename)

    def init_logger(self):
        path = self.log_path
        if not isfile(path):
            new_file(path)
        self._logger = self.get_logger()
        return self._logger

    def get_logger(self, level: int = logging.INFO) -> logging.Logger:
        __logger = logging.getLogger(self._name)
        __logger.setLevel(level)
        if not len(__logger.handlers):
            __handler = logging.FileHandler(self.log_path)
            # __handler.setFormatter(logging.Formatter('%(asctime)s: %(message)s'))
            __logger.addHandler(__handler)
        return __logger

    @classmethod
    def update_main_logger(cls):
        cls._main_logger = MainLogger(ArgParse.getter('srv_name')).init_logger()
        return cls._main_logger

    @classmethod
    def main_logger(cls):
        return cls._main_logger

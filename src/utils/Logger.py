from enum import Enum
from typing import Any

from src.utils.Singleton import Singleton


class LogLevels(Enum):
    DEBUG = 1
    INFO = 2
    ERROR = 3
    PRODUCTION = 4


class Logger(metaclass=Singleton):

    def __init__(self, level=LogLevels.DEBUG):
        self.level = level

    def debug_item(self, item: Any, level: LogLevels = LogLevels.DEBUG):
        if self.__is_printable(level):
            print('{}: {}'.format(level.name, item))

    def debug_list(self, items: list, level: LogLevels = LogLevels.DEBUG, separator=', '):
        if self.__is_printable(level):
            print(*items, sep=separator)

    def __is_printable(self, level: LogLevels):
        return level.value >= self.level.value

    @staticmethod
    def get_instance():
        return Logger()

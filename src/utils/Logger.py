from enum import Enum
from typing import Any

from src.utils.Singleton import Singleton


class LogLevels(Enum):
    DEBUG = 1
    INFO = 2
    ERROR = 3
    WARNING = 4
    PRODUCTION = 5


class Color:
    PRODUCTION = lambda x: '\033[30m' + str(x)
    ERROR = lambda x: '\033[31m' + str(x)
    INFO = lambda x: '\033[32m' + str(x)
    WARNING = lambda x: '\033[33m' + str(x)
    DEBUG = lambda x: '\033[34m' + str(x)
    MAGENTA = lambda x: '\033[35m' + str(x)
    CYAN = lambda x: '\033[36m' + str(x)
    WHITE = lambda x: '\033[37m' + str(x)
    UNDERLINE = lambda x: '\033[4m' + str(x)
    RESET = lambda x: '\033[0m' + str(x)

    @staticmethod
    def colorize(x):
        return getattr(Color, x)(x)

    @staticmethod
    def reset(x):
        return getattr(Color, 'RESET')(x)


class Logger(metaclass=Singleton):

    def __init__(self, level=LogLevels.DEBUG):
        self.level = level

    def debug_item(self, item: Any, level: LogLevels = LogLevels.DEBUG):
        if self.__is_printable(level):
            print('{}: {}'.format(Color.colorize(level.name), Color.reset(item)))

    def debug_list(self, items: list, level: LogLevels = LogLevels.DEBUG, separator=', '):
        if self.__is_printable(level) and len(items) > 0:
            print(*items, sep=separator)
        else:
            print('List is empty!')

    def __is_printable(self, level: LogLevels):
        return level.value >= self.level.value

    @staticmethod
    def get_instance():
        return Logger()

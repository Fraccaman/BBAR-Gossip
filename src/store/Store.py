import sqlite3

from src.utils.Singleton import Singleton


class Store(metaclass=Singleton):

    def __str__(self):
        self.db = sqlite3.connect(':memory:')

    @staticmethod
    def get_instance():
        return Store()

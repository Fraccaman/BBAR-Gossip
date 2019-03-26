import pickle
from abc import ABC


class Message(ABC):

    def serialize(self):
        return pickle.dumps(self)

    @staticmethod
    def deserialize(data: bytes):
        return pickle.loads(data)

    def __str__(self):
        return self.__class__.__name__

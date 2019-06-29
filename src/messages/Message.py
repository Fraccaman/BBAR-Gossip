import pickle
from abc import ABC
from typing import Any

from src.utils.Constants import END_OF_MESSAGE


class Message(ABC):

    def serialize(self) -> bytes:
        return pickle.dumps(self, pickle.HIGHEST_PROTOCOL) + END_OF_MESSAGE

    @staticmethod
    def deserialize(data: bytes) -> Any:
        return pickle.loads(data)

    def __str__(self):
        return self.__class__.__name__

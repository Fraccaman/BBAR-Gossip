import pickle
import random
from abc import ABC
from typing import Any

from src.utils.Constants import END_OF_MESSAGE, BYZANTINE_RANDOM_SEED


class Message(ABC):

    def __init__(self):
        self.random = random.Random(BYZANTINE_RANDOM_SEED)

    @staticmethod
    def will_be_byzantine(level):
        return random.uniform(0, 1) < level

    def serialize(self) -> bytes:
        return pickle.dumps(self, pickle.HIGHEST_PROTOCOL) + END_OF_MESSAGE

    @staticmethod
    def deserialize(data: bytes) -> Any:
        return pickle.loads(data)

    def __str__(self):
        return self.__class__.__name__

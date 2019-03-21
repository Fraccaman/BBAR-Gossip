import pickle
from abc import ABC

from src.messages import MessageType


class Message(ABC):

    def __init__(self, message_type: MessageType):
        self.message_type: MessageType = message_type

    def serialize(self):
        return pickle.dumps(self)

    @staticmethod
    def deserialize(data: bytes):
        return pickle.loads(data)

    def __str__(self):
        return self.message_type.name

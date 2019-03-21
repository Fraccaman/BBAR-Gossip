from src.messages.Message import Message
from src.messages.MessageType import MessageType


class HelloMessage(Message):

    def __init__(self, public_key: str, ip: str, port: int):
        super().__init__(MessageType.HELLO)
        self.public_key = public_key
        self.ip = ip
        self.port = port

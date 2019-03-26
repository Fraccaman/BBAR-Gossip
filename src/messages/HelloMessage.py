from src.messages.Message import Message


class HelloMessage(Message):

    def __init__(self, public_key: str, ip: str, port: int):
        self.public_key = public_key
        self.ip = ip
        self.port = port

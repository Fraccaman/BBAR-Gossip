from abc import abstractmethod, ABC
from asyncio import StreamWriter

from src.cryptography.Crypto import Crypto
from src.messages import Message


class Controller(ABC):

    def __init__(self):
        self.crypto = Crypto()

    @staticmethod
    @abstractmethod
    def is_valid_controller_for(message: Message) -> bool:
        raise Exception("Not Implemented!")

    async def handle(self, connection: StreamWriter, message: Message) -> None:
        self.on_receiving(message)
        await self._handle(connection, message)
        self.on_sending(message)

    @abstractmethod
    async def _handle(self, connection: StreamWriter, message: Message):
        pass

    @staticmethod
    async def send(connection: StreamWriter, message: Message) -> None:
        connection.write(message.serialize())
        await connection.drain()

    @staticmethod
    def on_receiving(message: Message):
        pass

    @staticmethod
    def on_sending(message: Message):
        pass

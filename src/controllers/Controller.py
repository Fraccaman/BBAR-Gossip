from abc import abstractmethod, ABC
from asyncio import StreamWriter

from src.cryptography.Crypto import Crypto
from src.messages import Message
from src.store.tables.Epoch import Epoch
from src.utils.PubSub import PubSub


class Controller(ABC):

    def __init__(self):
        self.crypto = Crypto()
        self.pub_sub = PubSub()

    @staticmethod
    @abstractmethod
    def is_valid_controller_for(message: Message) -> bool:
        raise Exception("Not Implemented!")

    async def handle(self, connection: StreamWriter, message: Message) -> None:
        self.on_receiving(message)
        await self._handle(connection, message)
        self.on_sending(message)

    @staticmethod
    def get_current_epoch():
        current_epoch = Epoch.get_current_epoch()
        return current_epoch

    @staticmethod
    def get_next_epoch():
        next_epoch = Epoch.get_next_epoch()
        return next_epoch

    @staticmethod
    def format_address(address):
        return '{}:{}'.format(address[0] if address[0] != '127.0.0.1' else '0.0.0.0', address[1])

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

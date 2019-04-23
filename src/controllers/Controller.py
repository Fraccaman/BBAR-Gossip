from abc import abstractmethod, ABC
from asyncio import StreamWriter
from typing import NoReturn

from config import Config
from src.cryptography.Crypto import Crypto
from src.mempool.Mempool import Mempool
from src.messages import Message
from src.store.tables.Epoch import Epoch
from src.utils.Constants import REGISTRATION_DIFFICULTY
from src.utils.PubSub import PubSub


class Controller(ABC):

    def __init__(self, config: Config):
        self.config = config
        self.crypto = Crypto()
        self.pub_sub = PubSub()
        self.mempool = Mempool()

    @staticmethod
    @abstractmethod
    def is_valid_controller_for(message: Message) -> bool:
        raise Exception("Not Implemented!")

    async def handle(self, connection: StreamWriter, message: Message) -> NoReturn:
        self.on_receiving(message)
        await self._handle(connection, message)
        self.on_sending(message)

    @staticmethod
    def get_puzzle_difficulty() -> float:
        return REGISTRATION_DIFFICULTY

    @staticmethod
    def get_current_epoch() -> Epoch:
        current_epoch = Epoch.get_current_epoch()
        return current_epoch

    @staticmethod
    def get_next_epoch() -> Epoch:
        next_epoch = Epoch.get_next_epoch()
        return next_epoch

    @staticmethod
    def format_address(address: str) -> str:
        return '{}:{}'.format(address[0] if address[0] != '127.0.0.1' else '0.0.0.0', address[1])

    @abstractmethod
    async def _handle(self, connection: StreamWriter, message: Message) -> NoReturn:
        pass

    @staticmethod
    async def send(connection: StreamWriter, message: Message) -> NoReturn:
        connection.write(message.serialize())
        await connection.drain()

    @staticmethod
    def on_receiving(message: Message) -> NoReturn:
        pass

    @staticmethod
    def on_sending(message: Message) -> NoReturn:
        pass

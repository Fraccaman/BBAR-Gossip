import asyncio
from abc import abstractmethod, ABC
from asyncio import StreamWriter
from typing import NoReturn, Tuple

from config import Config
from src.cryptography.Crypto import Crypto
from src.messages import Message
from src.store.tables.Epoch import Epoch
from src.utils.Constants import REGISTRATION_DIFFICULTY
from src.utils.PubSub import PubSub


class Controller(ABC):

    def __init__(self, config: Config):
        self.config = config
        self.crypto = Crypto()
        self.pub_sub = PubSub()
        self.connection_lock = asyncio.Lock()

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
    def format_public_key(x: str) -> Tuple[int, int, str]:
        tmp = x.split('.')
        return int(tmp[0]), int(tmp[1]), tmp[2]

    def verify_token(self, message, public_key):
        x, y, curve = self.format_public_key(public_key)
        bn_public_key = self.crypto.get_ec().load_public_key(x, y, curve)
        return self.crypto.get_ec().verify(message.token.bn_signature,
                                           (message.token.base + message.token.proof +
                                            message.token.epoch).encode('utf-8'), bn_public_key)

    async def close_connection(self, connection: StreamWriter):
        async with self.connection_lock:
            try:
                connection.close()
                await asyncio.sleep(0.5)
            finally:
                print('closed')
                await connection.wait_closed()

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

    async def send(self, connection: StreamWriter, message: Message) -> NoReturn:
        async with self.connection_lock:
            try:
                connection.write(message.serialize())
                await connection.drain()
            except ConnectionResetError or ConnectionAbortedError as _:
                print('connection closed')
                pass
            except Exception as e:
                print('random error', e)
                print(message)
                pass

    @staticmethod
    def on_receiving(message: Message) -> NoReturn:
        pass

    @staticmethod
    def on_sending(message: Message) -> NoReturn:
        pass

import asyncio
from typing import NoReturn

from config.Config import Config
from src.controllers.Dispatcher import Dispatcher
from src.cryptography.Crypto import Crypto
from src.network.Server import Server
from src.store.Store import Store
from src.store.tables.View import View
from src.utils.Constants import EPOCH_DURATION
from src.utils.Logger import LogLevels, Logger


class BootstrapNode(Server):

    @staticmethod
    def setup(private_key: int, log_level: LogLevels, file: int) -> NoReturn:
        Logger(LogLevels(log_level))
        Crypto(private_key)
        Store.setup_bn_store(file)

    async def handle(self, message: bytes, connection):
        await self.dispatcher.handle(message, connection)

    async def on_start(self):
        while True:
            await asyncio.sleep(EPOCH_DURATION, loop=asyncio.get_event_loop())
            await self.change_epoch()

    @staticmethod
    def format_address(address: str) -> str:
        return '{}:{}'.format(address[0] if address[0] != '127.0.0.1' else '0.0.0.0', address[1])

    @staticmethod
    async def change_epoch() -> NoReturn:
        View.set_new_epoch_and_peer_list()

    def __init__(self, config: Config):
        super().__init__(config.get('port'), config.get('host'), config.get('private_key'), config.get('id'),
                         config.get('log_level'))
        self.dispatcher = Dispatcher.get_bn_dispatcher(config)

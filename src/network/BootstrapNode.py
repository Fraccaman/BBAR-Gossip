import asyncio

from config.Config import Config
from src.controllers.Dispatcher import Dispatcher
from src.cryptography.Crypto import Crypto
from src.network.Server import Server
from src.store.Store import Store
from src.store.tables.View import View
from src.utils.Constants import EPOCH_TIMEOUT
from src.utils.Logger import LogLevels, Logger


class BootstrapNode(Server):

    @staticmethod
    def setup(private_key: int, log_level: LogLevels, file: int):
        Logger(LogLevels(log_level))
        Crypto(private_key)
        Store.setup_bn_store(file)

    async def handle(self, message: bytes, connection):
        await self.dispatcher.handle(message, connection)

    async def on_start(self):
        while True:
            await asyncio.sleep(EPOCH_TIMEOUT, loop=asyncio.get_event_loop())
            await self.change_epoch()

    async def change_epoch(self):
        peer_list = View.set_new_epoch_and_peer_list()
        Logger.get_instance().debug_list(peer_list)

    def __init__(self, config: Config):
        super().__init__(config.get('port'), config.get('host'), config.get('private_key'), config.get('id'),
                         config.get('log_level'))
        self.dispatcher = Dispatcher.get_bn_dispatcher()


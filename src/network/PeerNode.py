import asyncio
from asyncio import StreamWriter

from config.Config import Config
from src.controllers.Dispatcher import Dispatcher
from src.cryptography.Crypto import Crypto
from src.messages.HelloMessage import HelloMessage
from src.network.Server import Server
from src.store.Store import Store
from src.store.tables.BootstrapIdentity import BootstrapIdentity
from src.utils.Constants import START_DELAY, PEER_EPOCH_DURATION
from src.utils.Logger import Logger, LogLevels


class PeerNode(Server):

    @staticmethod
    def setup(private_key: int, log_level: LogLevels, file: int):
        Logger(LogLevels(log_level))
        Crypto(private_key)
        Store.setup_fn_store(file)

    async def handle(self, message: bytes, connection: StreamWriter):
        await self.dispatcher.handle(message, connection)

    async def on_start(self):
        await asyncio.sleep(START_DELAY, loop=asyncio.get_event_loop())
        asyncio.get_event_loop().call_soon(asyncio.ensure_future, self.start_new_epoch())
        await self.register_to_bn()

    async def start_new_epoch(self):
        while True:
            await asyncio.sleep(PEER_EPOCH_DURATION or 5, loop=asyncio.get_event_loop())
            Logger.get_instance().debug_item('Cose')

    def __init__(self, config: Config):
        super().__init__(config.get('port'), config.get('host'), config.get('private_key'), config.get('id'),
                         config.get('log_level'))
        self.dispatcher = Dispatcher.get_peer_dispatcher()
        self.bootstrap_nodes_addresses = config.get('bn_nodes')

    @staticmethod
    def set_bn(info):
        address, public_key = info.split(', ')[0], info.split(', ')[1]
        return BootstrapIdentity(address=address, public_key=public_key)

    async def register_to_bn(self):
        msg = HelloMessage(self.public_key, self.host, self.port)
        for bn in self.bootstrap_nodes_addresses:
            bn = self.set_bn(bn)
            bn_ip, bn_port = self.get_ip_port(bn.address)
            BootstrapIdentity.get_or_add(bn)
            Logger.get_instance().debug_item('Sending Hello message to: {}:{}'.format(bn_ip, bn_port))
            await self.send_to(bn_ip, bn_port, msg)

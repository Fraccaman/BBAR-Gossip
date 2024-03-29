import asyncio
from asyncio import StreamWriter
from datetime import datetime, timezone
from typing import NoReturn

from config.Config import Config
from src.controllers.Dispatcher import Dispatcher
from src.cryptography.Crypto import Crypto
from src.mempool.Mempool import Mempool
from src.messages.HelloMessage import HelloMessage
from src.messages.RenewTokenMessage import RenewTokenMessage
from src.network.Server import Server
from src.store.Store import Store
from src.store.tables.BootstrapIdentity import BootstrapIdentity
from src.utils.Constants import START_DELAY
from src.utils.Logger import Logger, LogLevels
from src.utils.PubSub import PubSub


class PeerNode(Server):

    def __init__(self, config: Config):
        super().__init__(config.get('port'), config.get('host'), config.get('private_key'), config.get('id'),
                         config.get('log_level'))
        self.dispatcher = Dispatcher.get_peer_dispatcher(config)
        self.bootstrap_nodes_addresses = config.get('bn_nodes')
        self.bar_connection = {}

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
        asyncio.get_event_loop().call_soon(asyncio.ensure_future, self.start_new_connection())
        asyncio.get_event_loop().call_soon(asyncio.ensure_future, self.send_pom())
        await self.register_to_bn()

    async def start_new_epoch(self):
        while True:
            key, view_message = await PubSub.get_subscriber_epoch_instance().consume()
            next_epoch_time = int(view_message.next_epoch) - int(datetime.now(tz=timezone.utc).timestamp())
            await asyncio.sleep(next_epoch_time)
            renew_message = RenewTokenMessage(view_message.token.base, view_message.token.proof,
                                              view_message.token.bn_signature, view_message.token.epoch)
            Logger.get_instance().debug_item('Number of open connections: {}'.format(len(self.connections.keys())))
            bn = BootstrapIdentity.get_one_by_token(renew_message.bn_signature)
            await Mempool().get_instance().freeze(view_message.epoch)
            writer = self.connections[bn.address]
            writer.write(renew_message.serialize())
            Logger.get_instance().debug_item('Renew token message sent!')
            await writer.drain()

    async def send_pom(self):
        while True:
            key, pom_message = await PubSub.get_subscriber_pom_instance().consume()
            bns = BootstrapIdentity.get_all()
            for bn in bns:
                bn_public_key = Crypto.get_instance().get_ec().load_public_key_from_string(bn.public_key)
                if Crypto.get_instance().get_ec().verify(pom_message.token.bn_signature,
                                                         (pom_message.token.base + pom_message.token.proof +
                                                          pom_message.token.epoch).encode('utf-8'), bn_public_key):
                    writer = self.connections[bn.address]
                    writer.write(pom_message.serialize())
                    await writer.drain()
                    break

    async def start_new_connection(self):
        while True:
            key, connection_req_message = await PubSub.get_subscriber_conn_instance().consume()
            ip, port = connection_req_message.to_peer.address.split(':')[0], \
                       connection_req_message.to_peer.address.split(':')[1]
            if connection_req_message.to_peer in self.connections:
                writer = self.connections[connection_req_message.to_peer]
                msg_serialized = connection_req_message.serialize()
                writer.write(msg_serialized)
            else:
                await self.send_to(ip, port, connection_req_message)

    @staticmethod
    def set_bn(info: str) -> BootstrapIdentity:
        address, public_key = info.split(', ')[0], info.split(', ')[1]
        return BootstrapIdentity(address=address, public_key=public_key)

    async def register_to_bn(self) -> NoReturn:
        msg = HelloMessage(self.public_key, self.host, self.port)
        for bn in self.bootstrap_nodes_addresses:
            bn = self.set_bn(bn)
            bn_ip, bn_port = self.get_ip_port(bn.address)
            BootstrapIdentity.get_or_add(bn)
            Logger.get_instance().debug_item('Sending Hello message to: {}:{}'.format(bn_ip, bn_port))
            try:
                await self.send_to(bn_ip, bn_port, msg)
            except Exception as e:
                continue

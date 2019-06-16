import asyncio
from abc import abstractmethod
from asyncio import StreamWriter
from typing import NoReturn

from config.Config import Config
from src.controllers.Controller import Controller
from src.mempool.Mempool import Mempool
from src.messages.BARMessage import BARMessage
from src.messages.PoMBARMessage import Misbehaviour, PoMBARMessage
from src.store.tables.Token import Token
from src.store.tables.BootstrapIdentity import BootstrapIdentity
from src.store.tables.PeerView import PeerView
from src.utils.Constants import MAX_CONTACTING_PEERS
from src.utils.Logger import Logger, LogLevels


class BARController(Controller):
    RETRY = 15

    def __init__(self, config: Config):
        super().__init__(config)
        self.mempool = Mempool()

    @staticmethod
    @abstractmethod
    def is_valid_controller_for(message: BARMessage) -> bool:
        raise Exception("Not Implemented!")

    @abstractmethod
    async def _handle(self, connection: StreamWriter, message: BARMessage) -> NoReturn:
        raise Exception("Not Implemented!")

    @staticmethod
    async def close_connection(connection: StreamWriter):
        if not connection.is_closing():
            connection.close()
            await connection.wait_closed()

    def is_valid_token(self, message: BARMessage):
        bns = BootstrapIdentity.get_all()
        for bn in bns:
            if self.verify_token(message, bn.public_key):
                return bn
        return None

    async def send_pom(self, misbehaviour: Misbehaviour, message: BARMessage, connection: StreamWriter):
        pom_message = PoMBARMessage(message.token, message.from_peer, message.to_peer, None, misbehaviour)
        self.pub_sub.broadcast_pom(pom_message)
        await self.close_connection(connection)

    # TODO: can optimize this by querying all peers for epoch X and then iterating (maybe its better only if n_of_peers is small)
    async def verify_seed(self, message: BARMessage, bn: BootstrapIdentity):
        n_of_peers = PeerView.get_total_peers_per_epoch(message.token.epoch, bn.id)
        while n_of_peers == 0:
            Logger.get_instance().debug_item('Waiting for view message ...')
            await asyncio.sleep(0.5)
            n_of_peers = PeerView.get_total_peers_per_epoch(message.token.epoch, bn.id)
        # print('received', message.token.bn_signature)
        # print('received from', self.crypto.get_ec().dump_public_key(message.from_peer.public_key))
        partners_index = list(reversed(self.crypto.get_random().prng(message.token.bn_signature, n_of_peers - 1,
                                                       MAX_CONTACTING_PEERS * self.RETRY)))
        # print('received', partners_index)
        my_pk = self.crypto.get_ec().dump_public_key(self.crypto.get_ec().public_key)
        if not my_pk == self.crypto.get_ec().dump_public_key(message.to_peer.public_key):
            return False

        # if i am the one requesting the exchange
        current_epoch_token = Token.find_one_by_epoch(message.token.epoch).signature
        if current_epoch_token == message.token.bn_signature:
            return True

        while len(partners_index) > 0:
            p_index = partners_index.pop()
            # print('received p_index', p_index)
            partner = PeerView.get_partner(p_index)
            # print('received to_peer', self.crypto.get_ec().dump_public_key(message.to_peer.public_key))
            # print('received p_public_key', partner.public_key)
            # print('received p_index', partner.index)
            # print('my_pk', self.crypto.get_ec().dump_public_key(self.crypto.get_ec().public_key))
            if partner.public_key == self.crypto.get_ec().dump_public_key(message.from_peer.public_key):
                continue
            elif partner.public_key == self.crypto.get_ec().dump_public_key(message.to_peer.public_key) and partner.is_me:
                return True
            elif partner.public_key != self.crypto.get_ec().dump_public_key(message.to_peer.public_key) and not partner.is_me:
                return False

    async def is_valid_message(self, message: BARMessage) -> bool:
        bn = self.is_valid_token(message)
        if bn is None:
            Logger.get_instance().debug_item('Invalid token! Sending PoM...', LogLevels.WARNING)
            return False
        Logger.get_instance().debug_item('Valid token for bn: {}, {}'.format(bn.id, bn.address))

        is_valid_partner = await self.verify_seed(message, bn)
        if not is_valid_partner:
            Logger.get_instance().debug_item('Invalid partner! Sending PoM...', LogLevels.WARNING)
            return False
        Logger.get_instance().debug_item('Valid partner {}!'.format(message.from_peer.address))

        is_valid_message_signature = message.verify_signature()
        if not is_valid_message_signature:
            Logger.get_instance().debug_item('Invalid message signature! Sending PoM...', LogLevels.WARNING)
            return False
        Logger.get_instance().debug_item('Valid signature message!')
        return True

from asyncio import StreamWriter
from typing import Tuple

from src.controllers.Controller import Controller
from src.messages.Message import Message
from src.messages.ViewMessage import ViewMessage
from src.store.tables.BootstrapIdentity import BootstrapIdentity
from src.store.tables.PeerView import PeerView
from src.store.tables.Token import Token
from src.utils.Constants import MAX_CONTACTING_PEERS
from src.utils.Logger import Logger


class JoinController(Controller):
    RETRY = 3

    @staticmethod
    def is_valid_controller_for(message: Message) -> bool:
        return isinstance(message, ViewMessage)

    @staticmethod
    def format_public_key(x: str) -> Tuple[int, int, str]:
        tmp = x.split('-')
        return int(tmp[0]), int(tmp[1]), tmp[2]

    def is_myself(self, peer_info):
        return

    @staticmethod
    def is_valid_token_for_current_epoch(message):
        return int(message.epoch) == int(message.token.epoch)

    @staticmethod
    def are_peers_enough(message):
        return len(message.peer_list) > 1

    @staticmethod
    def setup_view(peer_list, epoch, my_address):
        peers_view = [PeerView(index=idx, public_key=peer.public_key, address=peer.public_address, epoch=epoch,
                               is_me=peer.public_address == my_address) for idx, peer in enumerate(peer_list)]
        PeerView.add_multiple(peers_view)

    async def _handle(self, connection: StreamWriter, message: ViewMessage):
        bn_address = self.format_address(connection.get_extra_info('peername'))
        bn = BootstrapIdentity.get_one_by_address(bn_address)
        x, y, curve = self.format_public_key(bn.public_key)
        bn_public_key = self.crypto.get_ec().load_public_key(x, y, curve)
        is_valid_shuffle = message.verify_shuffle(message.epoch)
        is_valid_token = self.crypto.get_ec().verify(message.token.bn_signature,
                                                     (message.token.base + message.token.proof +
                                                      message.token.epoch).encode('utf-8'), bn_public_key)
        if not is_valid_token and is_valid_shuffle:
            # TODO: handle invalid token
            raise Exception('Bad token or bad shuffle')
        token = Token(base=message.token.base, proof=message.token.proof, signature=message.token.bn_signature,
                      epoch=message.token.epoch, bn_id=bn.id, key=message.token.key)
        Token.add_or_update(token)
        Logger.get_instance().debug_item('Next epoch will start at: {}'.format(message.next_epoch))
        self.pub_sub.broadcast_epoch_time(message)
        if self.is_valid_token_for_current_epoch(message) and self.are_peers_enough(message):
            Logger.get_instance().debug_item(
                'Valid token for epoch {} with {} peers'.format(message.epoch, len(message.peer_list)))
            self.setup_view(message.peer_list, message.epoch, self.config.get_address())
            partners_index = self.crypto.get_random().prng(message.token.bn_signature, len(message.peer_list) - 1,
                                                           MAX_CONTACTING_PEERS * self.RETRY)
            for _ in range(MAX_CONTACTING_PEERS):
                partner = PeerView.get_partner(partners_index.pop())
                while partner is None:
                    partner = PeerView.get_partner(partners_index.pop())
                Logger.get_instance().debug_item('Contacting peer: {}'.format(partner.address))
                
from asyncio import StreamWriter

from src.controllers.Controller import Controller
from src.messages.BARMessage import Identity, PeerInfo
from src.messages.ConnectionRequestBARMessage import ConnectionRequestBARMessage
from src.messages.Message import Message
from src.messages.ViewMessage import ViewMessage
from src.store.tables.BootstrapIdentity import BootstrapIdentity
from src.store.tables.PeerView import PeerView
from src.store.tables.Token import Token
from src.utils.Constants import MAX_CONTACTING_PEERS
from src.utils.Logger import Logger, LogLevels


class JoinController(Controller):
    RETRY = 15

    @staticmethod
    def is_valid_controller_for(message: Message) -> bool:
        return isinstance(message, ViewMessage)

    @staticmethod
    def is_valid_token_for_current_epoch(message):
        return int(message.epoch) == int(message.token.epoch)

    @staticmethod
    def are_peers_enough(message):
        return len(message.peer_list) > 1

    @staticmethod
    def setup_view(peer_list, epoch, my_address, bn):
        peers_view = [PeerView(index=idx, public_key=peer.public_key, address=peer.public_address, epoch=epoch,
                               is_me=peer.public_address == my_address, bn_id=bn.id) for idx, peer in
                      enumerate(peer_list)]
        PeerView.add_multiple(peers_view)

    def init_bar_gossip(self, message, config, partner):
        seed = Identity(message.token.base, message.token.proof, message.token.bn_signature, message.token.epoch)
        _from = PeerInfo(config.get_address(), self.crypto.get_ec().get_public)
        _to = PeerInfo(partner.address, self.crypto.get_ec().load_public_key_from_string(partner.public_key))
        return seed, _from, _to

    async def _handle(self, connection: StreamWriter, message: ViewMessage):
        bn_address = self.format_address(connection.get_extra_info('peername'))
        bn = BootstrapIdentity.get_one_by_address(bn_address)
        is_valid_shuffle = message.verify_shuffle(message.epoch)
        is_valid_token = self.verify_token(message, bn.public_key)
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
            self.setup_view(message.peer_list, message.epoch, self.config.get_address(), bn)
            partners_index = list(reversed(self.crypto.get_random().prng(message.token.bn_signature, len(message.peer_list) - 1,
                                                           MAX_CONTACTING_PEERS * self.RETRY)))

            # WARNING: works if MAX_CONTACTING_PEERS == 1. Should not work if > 1. Maybe
            for _ in range(MAX_CONTACTING_PEERS):
                while len(partners_index) > 0:
                    p_index = partners_index.pop()
                    partner = PeerView.get_partner(p_index)
                    if partner.is_me:
                        continue
                    # TODO: check if len(partners_index) == 0. Should never happen
                    Logger.get_instance().debug_item('Contacting peer {} with address {}'.format(partner.id, partner.address), LogLevels.FEATURE)
                    seed, _from, _to = self.init_bar_gossip(message, self.config, partner)
                    conn_req_message = ConnectionRequestBARMessage(seed, _from, _to, None)
                    conn_req_message.compute_signature()
                    self.pub_sub.broadcast_new_connection(conn_req_message)
                    break

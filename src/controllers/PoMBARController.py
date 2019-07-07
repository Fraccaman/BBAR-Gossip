from asyncio import StreamWriter

from src.controllers.Controller import Controller
from src.messages.BARMessage import BARMessage
from src.messages.PoMBARMessage import PoMBARMessage
from src.store.tables.Peer import Peer
from src.store.tables.ProofOfMisbehaviour import ProofOfMisbehaviour
from src.utils.Logger import Logger


class PoMBARController(Controller):

    @staticmethod
    def is_valid_controller_for(message: BARMessage) -> bool:
        return isinstance(message, PoMBARMessage)

    async def _handle(self, connection: StreamWriter, message: PoMBARMessage):
        peer_from_pk = self.crypto.get_ec().public_key_to_string(message.from_peer.public_key)
        peer_to_pk = self.crypto.get_ec().public_key_to_string(message.to_peer.public_key)
        peer_from = Peer.find_one_by_public_key(peer_from_pk)
        peer_to = Peer.find_one_by_public_key(peer_to_pk)
        pom = ProofOfMisbehaviour(against_peer=peer_from.id, type=message.misbehaviour.value, from_peer=peer_to.id,
                                  epoch=message.token.epoch)
        Logger.get_instance().debug_item('Received a PoM against peer: {} from peer: {}'.format(peer_from.public_address, peer_to.public_address))
        ProofOfMisbehaviour.add(pom)

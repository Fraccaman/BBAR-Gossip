from asyncio import StreamWriter

from src.controllers.Controller import Controller
from src.cryptography.Hashcash import Hashcash
from src.messages import Message
from src.messages.LoginMessage import LoginMessage
from src.messages.TokenMessage import TokenMessage
from src.store.tables.Epoch import Epoch
from src.store.tables.Peer import Peer
from src.store.tables.Registration import Registration
from src.store.tables.View import View
from src.utils.Constants import EPOCH_DIFF
from src.utils.Logger import Logger


class TokenController(Controller):

    @staticmethod
    def is_valid_controller_for(message: Message) -> bool:
        return isinstance(message, LoginMessage)

    @staticmethod
    def get_puzzle_difficulty():
        return 1e-5

    @staticmethod
    def get_current_epoch():
        current_epoch = Epoch.get_current_epoch()
        return current_epoch.epoch

    def is_valid_proof(self, message: LoginMessage):
        is_registered = Registration.get_one_by_base(message.base)
        is_registration_recent = is_registered.epoch + EPOCH_DIFF >= self.get_current_epoch()
        base_to_bytes = message.base.encode('utf-8')
        salt_to_bytes = bytes.fromhex(message.proof)
        return is_registered and is_registration_recent and Hashcash.is_valid_proof(base_to_bytes, salt_to_bytes,
                                                                                    self.get_puzzle_difficulty())

    @staticmethod
    def create_token(base, salt):
        token_message = TokenMessage(base, salt)
        token_message.bn_sign()
        return token_message

    def format_address(self, address):
        return '{}:{}'.format(address[0] if address[0] != '127.0.0.1' else '0.0.0.0', address[1])

    async def _handle(self, connection: StreamWriter, message: LoginMessage):
        if self.is_valid_proof(message):
            Logger.get_instance().debug_item('Valid PoW received! Crafting token...')
            token_message = self.create_token(message.base, message.proof)
            await TokenController.send(connection, token_message)
            peer_address = self.format_address(connection.get_extra_info('peername'))
            peer_public_key = message.get_public_key()
            new_peer = Peer(address=peer_address, pk=peer_public_key)
            next_epoch = Epoch.get_next_epoch()
            Peer.add(new_peer)
            View.add(View(peer=new_peer.id, epoch=next_epoch.id))
            Logger.get_instance().debug_item('Token sent!')

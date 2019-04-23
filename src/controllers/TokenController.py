from asyncio import StreamWriter
from typing import Tuple, Union

from src.controllers.Controller import Controller
from src.cryptography.Hashcash import Hashcash
from src.messages import Message
from src.messages.LoginMessage import LoginMessage
from src.messages.TokenMessage import TokenMessage
from src.messages.ViewMessage import ViewMessage
from src.store.tables.Peer import Peer
from src.store.tables.Registration import Registration
from src.store.tables.View import View
from src.utils.Constants import EPOCH_DIFF
from src.utils.Logger import Logger


class TokenController(Controller):

    @staticmethod
    def is_valid_controller_for(message: Message) -> bool:
        return isinstance(message, LoginMessage)

    def is_valid_proof(self, message: LoginMessage) -> Union[Tuple[bool, int], Tuple[bool, None]]:
        is_registered = Registration.get_one_by_base(message.base)
        is_registration_recent = is_registered.epoch + EPOCH_DIFF >= self.get_current_epoch().epoch
        base_to_bytes = message.base.encode('utf-8')
        salt_to_bytes = bytes.fromhex(message.proof)
        valid = is_registered and is_registration_recent and Hashcash.is_valid_proof(base_to_bytes, salt_to_bytes,
                                                                                     self.get_puzzle_difficulty())
        return (valid, is_registered.id) if valid else (valid, None)

    @staticmethod
    def create_token(base: str, salt: str) -> TokenMessage:
        token_message = TokenMessage(base, salt)
        token_message.set_next_epoch()
        token_message.bn_sign()
        return token_message

    async def _handle(self, connection: StreamWriter, message: LoginMessage):
        is_valid_registration, id = self.is_valid_proof(message)
        if is_valid_registration:
            Logger.get_instance().debug_item('Valid PoW received! Crafting token...')
            Registration.update_registration(message.base, message.proof)
            current_view_peers = ViewMessage.get_current_view()
            view_message = ViewMessage(peer_list=current_view_peers, epoch=self.get_current_epoch().epoch)
            Logger.get_instance().debug_list(view_message.peer_list, separator='\n')
            token_message = self.create_token(message.base, message.proof)
            view_message.set_token(token_message)
            await TokenController.send(connection, view_message)
            peer_address = self.format_address(connection.get_extra_info('peername'))
            peer_public_key = message.get_public_key()
            new_peer = Peer(address=peer_address, public_key=peer_public_key, registration=id,
                            public_address=message.address)
            Peer.find_or_add(new_peer)
            next_epoch = self.get_next_epoch()
            View.add(View(peer=new_peer.id, epoch_id=next_epoch.id))
            Logger.get_instance().debug_item('View message sent!')

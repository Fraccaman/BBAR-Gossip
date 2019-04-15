from asyncio import StreamWriter

from src.controllers.Controller import Controller
from src.messages import Message
from src.messages.RenewTokenMessage import RenewTokenMessage
from src.messages.TokenMessage import TokenMessage
from src.messages.ViewMessage import ViewMessage
from src.store.tables.Peer import Peer
from src.store.tables.View import View
from src.utils.Logger import Logger


class RenewController(Controller):

    @staticmethod
    def is_valid_controller_for(message: Message) -> bool:
        return isinstance(message, RenewTokenMessage)

    @staticmethod
    def create_token(base: str, salt: str) -> TokenMessage:
        token_message = TokenMessage(base, salt)
        token_message.bn_sign()
        return token_message

    async def _handle(self, connection: StreamWriter, message: RenewTokenMessage):
        is_valid_token = message.is_valid_signature()
        if is_valid_token:
            current_view_peers = ViewMessage.get_current_view()
            view_message = ViewMessage(peer_list=current_view_peers, epoch=self.get_current_epoch().epoch)
            Logger.get_instance().debug_list(view_message.peer_list, separator='\n')
            token_message = self.create_token(message.base, message.proof)
            view_message.set_token(token_message)
            await RenewController.send(connection, view_message)
            peer_address = self.format_address(connection.get_extra_info('peername'))
            peer = Peer.find_one_by_address(peer_address)
            current_epoch = self.get_current_epoch()
            View.add(View(peer=peer.id, epoch_id=current_epoch.id))
            Logger.get_instance().debug_item('Renewed View Message for epoch {} sent!'.format(current_epoch.epoch))

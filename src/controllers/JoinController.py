from asyncio import StreamWriter
from typing import Tuple

from src.controllers.Controller import Controller
from src.messages.Message import Message
from src.messages.ViewMessage import ViewMessage
from src.store.tables.BootstrapIdentity import BootstrapIdentity
from src.store.tables.Token import Token
from src.utils.Logger import Logger


class JoinController(Controller):

    @staticmethod
    def is_valid_controller_for(message: Message) -> bool:
        return isinstance(message, ViewMessage)

    @staticmethod
    def format_public_key(x: str) -> Tuple[int, int, str]:
        tmp = x.split('-')
        return int(tmp[0]), int(tmp[1]), tmp[2]

    async def _handle(self, connection: StreamWriter, message: ViewMessage):
        bn_address = self.format_address(connection.get_extra_info('peername'))
        bn = BootstrapIdentity.get_one_by_address(bn_address)
        x, y, curve = self.format_public_key(bn.public_key)
        bn_public_key = self.crypto.get_ec().load_public_key(x, y, curve)
        is_valid = self.crypto.get_ec().verify(message.token.bn_signature, (message.token.base + message.token.proof +
                                                                            message.token.epoch).encode('utf-8'),
                                               bn_public_key)
        is_new = Token.find_one_by_epoch(message.epoch)
        if not is_valid:
            # TODO: handle invalid token
            raise Exception('Bad token')
        Logger.get_instance().debug_item('A valid token has been received for epoch {}'.format(message.token.epoch))
        if not is_new:
            Token.add(
                Token(base=message.token.base, proof=message.token.proof, signature=message.token.bn_signature,
                      epoch=message.token.epoch, bn_id=bn.id))
        Logger.get_instance().debug_item('Next epoch will start at: {}'.format(message.next_epoch))
        self.pub_sub.broadcast_epoch_time(message)

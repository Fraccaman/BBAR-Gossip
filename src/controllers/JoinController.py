from asyncio import StreamWriter

from src.controllers.Controller import Controller
from src.messages import Message
from src.messages.TokenMessage import TokenMessage
from src.messages.ViewMessage import ViewMessage
from src.store.tables.BootstrapIdentity import BootstrapIdentity
from src.store.tables.Token import Token
from src.utils.Logger import Logger


class JoinController(Controller):

    @staticmethod
    def is_valid_controller_for(message: Message) -> bool:
        return isinstance(message, ViewMessage)

    @staticmethod
    def format_address(address):
        return '{}:{}'.format(address[0] if address[0] != '127.0.0.1' else '0.0.0.0', address[1])

    @staticmethod
    def format_public_key(x):
        tmp = x.split('-')
        return int(tmp[0]), int(tmp[1]), tmp[2]

    async def _handle(self, connection: StreamWriter, message: ViewMessage):
        bn_address = self.format_address(connection.get_extra_info('peername'))
        bn = BootstrapIdentity.get_one_by_address(bn_address)
        x, y, curve = self.format_public_key(bn.public_key)
        bn_public_key = self.crypto.get_ec().load_public_key(x, y, curve)
        is_valid = self.crypto.get_ec().verify(message.token.bn_signature, (message.token.base + message.token.proof +
                                                                            message.token.epoch).encode('utf-8'), bn_public_key)
        if not is_valid:
            raise Exception('Bad token')
        Logger.get_instance().debug_item('A valid token has been received')
        Token.add(
            Token(base=message.token.base, proof=message.token.proof, signature=message.token.bn_signature, epoch=message.token.epoch, bn_id=bn.id))
        Logger.get_instance().debug_item('Next epoch will start at: {}'.format(message.next_epoch))

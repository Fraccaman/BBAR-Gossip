from asyncio import StreamWriter

from src.controllers.Controller import Controller
from src.messages import Message
from src.messages.TokenMessage import TokenMessage
from src.store.tables.BootstrapIdentity import BootstrapIdentity
from src.store.tables.Token import Token
from src.utils.Logger import Logger


class JoinController(Controller):

    @staticmethod
    def is_valid_controller_for(message: Message) -> bool:
        return isinstance(message, TokenMessage)

    @staticmethod
    def format_address(address):
        return '{}:{}'.format(address[0] if address[0] != '127.0.0.1' else '0.0.0.0', address[1])

    @staticmethod
    def format_public_key(x):
        tmp = x.split('-')
        return int(tmp[0]), int(tmp[1]), tmp[2]

    @staticmethod
    def get_message_epoch(x):
        return x.split('-')[1]

    async def _handle(self, connection: StreamWriter, message: TokenMessage):
        bn_address = self.format_address(connection.get_extra_info('peername'))
        bn = BootstrapIdentity.get_one_by_address(bn_address)
        x, y, curve = self.format_public_key(bn.public_key)
        bn_public_key = self.crypto.get_ec().load_public_key(x, y, curve)
        is_valid = self.crypto.get_ec().verify(message.bn_signature, (message.base + message.proof).encode('utf-8'),
                                               bn_public_key)
        if not is_valid:
            raise Exception('Bad token')
        Logger.get_instance().debug_item('A valid token has been received')
        epoch = message.get_epoch()
        Token.add(
            Token(base=message.base, proof=message.proof, signature=message.bn_signature, epoch=epoch, bn_id=bn.id))

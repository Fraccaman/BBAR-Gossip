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

    def format_address(self, address):
        return '{}:{}'.format(address[0] if address[0] != '127.0.0.1' else '0.0.0.0', address[1])

    def format_public_key(self, x):
        tmp = x.split('-')
        return int(tmp[0]), int(tmp[1]), tmp[2]

    def get_message_epoch(self, x):
        return x.split('-')[1]

    async def _handle(self, connection: StreamWriter, message: TokenMessage):
        bn_address = self.format_address(connection.get_extra_info('peername'))
        bn = BootstrapIdentity.get_one_by_address(bn_address)
        x, y, curve = self.format_public_key(bn.public_key)
        bn_public_key = self.crypto.get_ec().load_public_key(x, y, curve)
        is_valid = self.crypto.get_ec().verify(message.bn_signature, (message.base + message.proof).encode('utf-8'), bn_public_key)
        epoch = self.get_message_epoch(message.base)
        if not is_valid:
            raise Exception('Bad token')
        Logger.get_instance().debug_item('A valid token has been received')
        Token.add(Token(base=message.base, proof=message.proof, signature=message.bn_signature, epoch=epoch, bn_id=bn.id))




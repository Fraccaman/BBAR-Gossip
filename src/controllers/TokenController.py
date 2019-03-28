from asyncio import StreamWriter

from src.controllers.Controller import Controller
from src.cryptography.Hashcash import Hashcash
from src.messages import Message
from src.messages.LoginMessage import LoginMessage
from src.messages.TokenMessage import TokenMessage
from src.store.tables.Registration import Registration
from src.utils.Logger import Logger


class TokenController(Controller):

    @staticmethod
    def is_valid_controller_for(message: Message) -> bool:
        return isinstance(message, LoginMessage)

    def get_puzzle_difficulty(self):
        return 1e-5

    def get_current_epoch(self):
        return 1

    def is_valid_proof(self, message: LoginMessage):
        is_registered = Registration.get_one_by_base(message.base)
        # TODO: get current epoch
        is_registration_recent = is_registered.epoch + 2 >= self.get_current_epoch()
        base_to_bytes = message.base.encode('utf-8')
        salt_to_bytes = bytes.fromhex(message.proof)
        return is_registered and is_registration_recent and Hashcash.is_valid_proof(base_to_bytes, salt_to_bytes,
                                                                                    self.get_puzzle_difficulty())

    def create_token(self, base, salt):
        token_message = TokenMessage(base, salt)
        token_message.bn_sign()
        return token_message

    async def _handle(self, connection: StreamWriter, message: LoginMessage):
        if self.is_valid_proof(message):
            Logger.get_instance().debug_item('Valid PoW received! Crafting token...')
            token_message = self.create_token(message.base, message.proof)
            await TokenController.send(connection, token_message)
            Logger.get_instance().debug_item('Token sent!')

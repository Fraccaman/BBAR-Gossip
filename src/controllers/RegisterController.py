from asyncio import StreamWriter

from src.controllers.Controller import Controller
from src.cryptography.Hashcash import Hashcash
from src.messages import Message
from src.messages.LoginMessage import LoginMessage
from src.messages.RegisterMessage import RegisterMessage
from src.store.tables.Token import Token
from src.utils.Logger import Logger, LogLevels


class RegisterController(Controller):

    @staticmethod
    def is_valid_controller_for(message: Message) -> bool:
        return isinstance(message, RegisterMessage)

    @staticmethod
    def format_address(address):
        return '{}:{}'.format(address[0] if address[0] != '127.0.0.1' else '0.0.0.0', address[1])

    async def _handle(self, connection: StreamWriter, message: RegisterMessage):
        bn_address = self.format_address(connection.get_extra_info('peername'))
        already_registered = Token.get_one_by_epoch_and_address(message.get_epoch(), bn_address)
        if already_registered:
            Logger.get_instance().debug_item('Found an valid token!', LogLevels.INFO)
            connection.close()
        else:
            Logger.get_instance().debug_item('Computing a valid PoW ...', LogLevels.INFO)
            pow_solution = Hashcash.new(message.difficulty, message.puzzle.encode('utf-8'))
            Logger.get_instance().debug_item('PoW found! Salt: {}, percentile: {}'.format(pow_solution.salt.hex(), pow_solution.percentile()), LogLevels.INFO)
            login_message = LoginMessage(message.puzzle, pow_solution.salt.hex())
            await RegisterController.send(connection, login_message)



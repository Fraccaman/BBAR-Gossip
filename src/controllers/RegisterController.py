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

    async def _handle(self, connection: StreamWriter, message: RegisterMessage):
        bn_address = self.format_address(connection.get_extra_info('peername'))
        already_registered: Token = Token.find_one_by_address(bn_address, message.current_epoch)
        if already_registered:
            Logger.get_instance().debug_item('Found a valid token!', LogLevels.INFO)
            login_message = LoginMessage(already_registered.base, already_registered.proof, self.config.get_address())
            await RegisterController.send(connection, login_message)
        else:
            Logger.get_instance().debug_item('Computing a valid PoW ...', LogLevels.INFO)
            pow_solution = Hashcash.new(message.difficulty, message.puzzle.encode('utf-8'))
            Logger.get_instance().debug_item(
                'PoW found! Salt: {}, percentile: {}'.format(pow_solution.salt.hex(), pow_solution.percentile()),
                LogLevels.INFO)
            login_message = LoginMessage(message.puzzle, pow_solution.salt.hex(), self.config.get_address())
            await RegisterController.send(connection, login_message)

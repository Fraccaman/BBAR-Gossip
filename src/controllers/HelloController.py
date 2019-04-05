from asyncio import StreamWriter

from src.controllers.Controller import Controller
from src.messages import Message
from src.messages.HelloMessage import HelloMessage
from src.messages.RegisterMessage import RegisterMessage
from src.store.tables.Epoch import Epoch
from src.store.tables.Registration import Registration
from src.utils.Constants import REGISTRATION_DIFFICULTY
from src.utils.Logger import Logger


class HelloController(Controller):

    @staticmethod
    def is_valid_controller_for(message: Message) -> bool:
        return isinstance(message, HelloMessage)

    @staticmethod
    def get_puzzle_difficulty():
        return REGISTRATION_DIFFICULTY

    @staticmethod
    def get_current_epoch():
        current_epoch = Epoch.get_current_epoch()
        return current_epoch.epoch

    async def _handle(self, connection: StreamWriter, message: HelloMessage):
        difficulty = self.get_puzzle_difficulty()
        register_message = RegisterMessage(difficulty, message.public_key)
        already_exist = Registration.is_registration_present(register_message.puzzle)
        if already_exist:
            register_message.puzzle = already_exist.base
            Logger.get_instance().debug_item('A valid registration already exist')
            await HelloController.send(connection, register_message)
        else:
            Registration.add(Registration(base=register_message.puzzle, epoch=self.get_current_epoch()))
            await HelloController.send(connection, register_message)

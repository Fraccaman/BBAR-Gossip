from asyncio import StreamWriter

from src.controllers.Controller import Controller
from src.messages import Message
from src.messages.HelloMessage import HelloMessage
from src.messages.RegisterMessage import RegisterMessage
from src.store.tables.Registration import Registration
from src.utils.Logger import Logger


class HelloController(Controller):

    @staticmethod
    def is_valid_controller_for(message: Message) -> bool:
        return isinstance(message, HelloMessage)

    async def _handle(self, connection: StreamWriter, message: HelloMessage):
        difficulty = self.get_puzzle_difficulty()
        current_epoch = self.get_current_epoch().epoch
        register_message = RegisterMessage(difficulty, message.public_key, current_epoch)
        already_exist = Registration.is_registration_present(register_message.puzzle)
        if already_exist:
            register_message.puzzle = already_exist.base
            Logger.get_instance().debug_item('A valid registration already exist')
            await HelloController.send(connection, register_message)
        else:
            epoch = self.get_current_epoch().epoch
            Registration.add(Registration(base=register_message.puzzle, epoch=epoch))
            await HelloController.send(connection, register_message)

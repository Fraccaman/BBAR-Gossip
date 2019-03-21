from asyncio import StreamWriter
from typing import NoReturn

from src.controllers.Controller import Controller
from src.messages import Message
from src.messages.RegisterMessage import RegisterMessage


class RegisterController(Controller):

    @staticmethod
    def is_valid_controller_for(message: Message) -> bool:
        return isinstance(message, RegisterMessage)

    @staticmethod
    async def _handle(connection: StreamWriter, message: RegisterMessage) -> NoReturn:
        pass

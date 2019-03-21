from asyncio import StreamWriter

from src.controllers.Controller import Controller
from src.messages import Message
from src.messages.HelloMessage import HelloMessage
from src.messages.RegisterMessage import RegisterMessage


class HelloController(Controller):

    @staticmethod
    def is_valid_controller_for(message: Message) -> bool:
        return isinstance(message, HelloMessage)

    @staticmethod
    async def _handle(connection: StreamWriter, message: HelloMessage):
        connection.write(RegisterMessage(5, 1, message.public_key).serialize())
        await connection.drain()

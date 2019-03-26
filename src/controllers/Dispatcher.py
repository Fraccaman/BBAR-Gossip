from asyncio import StreamWriter
from typing import NoReturn

from src.controllers.HelloController import HelloController
from src.controllers.JoinController import JoinController
from src.controllers.RegisterController import RegisterController
from src.controllers.TokenController import TokenController
from src.messages.Message import Message
from src.utils.Logger import Logger


class Dispatcher:
    def __init__(self, controllers):
        self.controllers = controllers

    @staticmethod
    def get_peer_dispatcher():
        return Dispatcher([RegisterController(), JoinController()])

    @staticmethod
    def get_bn_dispatcher():
        return Dispatcher([HelloController(), TokenController()])

    @staticmethod
    def deserialize_data(msg_bytes) -> Message:
        return None if msg_bytes == b'' or msg_bytes is None else Message.deserialize(msg_bytes)

    async def handle(self, msg_bytes: bytes, connection: StreamWriter) -> NoReturn:
        message = self.deserialize_data(msg_bytes)
        for controller in self.controllers:
            if controller.is_valid_controller_for(message):
                Logger.get_instance().debug_item('A {} message is arrived and being handled'.format(message))
                await controller.handle(connection, message)
                break

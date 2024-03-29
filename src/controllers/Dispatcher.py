from asyncio import StreamWriter
from typing import NoReturn

from config.Config import Config
from src.controllers.BriefcaseBARController import BriefcaseBARController
from src.controllers.ConnectionRequestBARController import ConnectionRequestBARController
from src.controllers.FinishBarController import FinishBARController
from src.controllers.HelloController import HelloController
from src.controllers.JoinController import JoinController
from src.controllers.KeyBARController import KeyBARController
from src.controllers.KeyRequestBARController import KeyRequestBARController
from src.controllers.PoMBARController import PoMBARController
from src.controllers.PromiseAcceptBARController import PromiseAcceptBARController
from src.controllers.PromiseRequestBARController import PromiseRequestBARController
from src.controllers.RegisterController import RegisterController
from src.controllers.RenewController import RenewController
from src.controllers.TokenController import TokenController
from src.messages.Message import Message
from src.utils.Logger import Logger, LogLevels


class Dispatcher:
    def __init__(self, controllers):
        self.controllers = controllers
        self.invalid_messages = list([])

    @staticmethod
    def get_peer_dispatcher(config: Config):
        return Dispatcher([RegisterController(config), JoinController(config), ConnectionRequestBARController(config),
                           PromiseRequestBARController(config), PromiseAcceptBARController(config),
                           BriefcaseBARController(config),
                           KeyRequestBARController(config), KeyBARController(config), FinishBARController(config)])

    @staticmethod
    def get_bn_dispatcher(config: Config):
        return Dispatcher(
            [HelloController(config), TokenController(config), RenewController(config), PoMBARController(config)])

    def deserialize_data(self, msg_bytes) -> Message:
        try:
            return None if msg_bytes == b'' or msg_bytes is None else Message.deserialize(msg_bytes)
        except Exception as _:
            Logger.get_instance().debug_item('deserialize exception: {}'.format(msg_bytes), LogLevels.ERROR)
            self.invalid_messages.append(msg_bytes)
            if len(self.invalid_messages) > 1:
                try:
                    print('start')
                    t = b''.join(self.invalid_messages)
                    print('t done', t)
                    msg = Message.deserialize(t)
                    print('recovery with {} messages', len(self.invalid_messages))
                    self.invalid_messages = []
                    Logger.get_instance().debug_item('message recovered successfully', LogLevels.INFO)
                    return msg
                except Exception as e:
                    self.invalid_messages.append(msg_bytes)
                    Logger.get_instance().debug_item('failed message recovery: {}'.format(e), LogLevels.ERROR)

    async def handle(self, msg_bytes: bytes, connection: StreamWriter) -> NoReturn:
        message = self.deserialize_data(msg_bytes)
        for controller in self.controllers:
            if controller.is_valid_controller_for(message):
                Logger.get_instance().debug_item('A {} message is arrived and being handled'.format(message))
                try:
                    await controller.handle(connection, message)
                except Exception as _:
                    break
                finally:
                    break

from asyncio import StreamWriter
from typing import NoReturn

from src.controllers.BARController import BARController
from src.messages.BARMessage import BARMessage
from src.messages.ConnectionRequestBARMessage import ConnectionRequestBARMessage
from src.messages.HistoryDivulgeBARMessage import HistoryDivulgeBARMessage
from src.messages.PoMBARMessage import Misbehaviour
from src.utils.Logger import Logger


class ConnectionRequestBARController(BARController):

    @staticmethod
    def is_valid_controller_for(message: BARMessage) -> bool:
        return isinstance(message, ConnectionRequestBARMessage)

    async def _handle(self, connection: StreamWriter, message: ConnectionRequestBARMessage) -> NoReturn:
        if not await self.is_valid_message(message):
            Logger.get_instance().debug_item('Invalid seed ... sending PoM')
            await self.send_pom(Misbehaviour.BAD_SEED, message, connection)
            return

        history_divulge_message = HistoryDivulgeBARMessage(self.mempool.serialize(), message.token,
                                                           message.to_peer, message.from_peer, message)
        history_divulge_message.compute_signature()

        await self.send(connection, history_divulge_message)

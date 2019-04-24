from asyncio import StreamWriter
from typing import NoReturn

from src.controllers.BARController import BARController
from src.messages.BARMessage import BARMessage
from src.messages.ConnectionRequestBARMessage import ConnectionRequestBARMessage
from src.utils.Logger import Logger, LogLevels


class ConnectionRequestBARController(BARController):

    @staticmethod
    def is_valid_controller_for(message: BARMessage) -> bool:
        return isinstance(message, ConnectionRequestBARMessage)

    async def _handle(self, connection: StreamWriter, message: ConnectionRequestBARMessage) -> NoReturn:
        bn = self.is_valid_token(message)
        if bn is None:
            Logger.get_instance().debug_item('Invalid token! Sending PoM...', LogLevels.WARNING)
            # TODO: send PoM
        Logger.get_instance().debug_item('Valid token for bn: {}, {}'.format(bn.id, bn.address))
        is_valid_partner = await self.verify_seed(message, bn)
        if not is_valid_partner:
            Logger.get_instance().debug_item('Invalid partner! Sending PoM...', LogLevels.WARNING)
            # TODO: send PoM
        Logger.get_instance().debug_item('Valid partner {}!'.format(message.from_peer.address))
        if not connection.is_closing():
            connection.close()
            await connection.wait_closed()

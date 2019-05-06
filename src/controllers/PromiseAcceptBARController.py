from asyncio import StreamWriter
from typing import NoReturn

from src.controllers.BARController import BARController
from src.messages.BARMessage import BARMessage
from src.messages.ExchangeBARMessage import ExchangeBARMessage
from src.messages.PromiseBARMessage import PromiseBARMessage
from src.store.tables.ExchangeTable import Exchange
from src.utils.Logger import Logger


class PromiseAcceptBARController(BARController):
    BAL = 'Balanced Exchange'
    OPT = 'Optimistic Exchange'

    @staticmethod
    def is_valid_controller_for(message: BARMessage) -> bool:
        return isinstance(message, ExchangeBARMessage)

    def is_promise_request_valid(self, message: ExchangeBARMessage):
        for tx in message.needed:
            if not self.mempool.has(tx):
                return False
        for tx in message.promised:
            if self.mempool.has(tx):
                return False
        return True

    # TODO: add OPT exchange logic
    async def _handle(self, connection: StreamWriter, message: ExchangeBARMessage) -> NoReturn:
        if not await self.is_valid_message(message):
            # TODO: send PoM
            Logger.get_instance().debug_item('Invalid request... sending PoM')

        if self.is_promise_request_valid(message):
            # TODO: send PoM
            Logger.get_instance().debug_item('Invalid history message... sending PoM')

        exchange = Exchange(seed=message.token.bn_signature, sender=False, needed=message.needed,
                            promised=message.promised,
                            type=str(message.type), signature=message.signature)
        Exchange.add(exchange)

        promise_message = PromiseBARMessage(message.token, message.to_peer, message.from_peer, message,
                                            message.promised,
                                            message.needed, str(message.type))
        promise_message.compute_signature()

        await self.send(connection, promise_message)

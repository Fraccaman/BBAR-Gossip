import asyncio
import json
from asyncio import StreamWriter
from typing import NoReturn

from src.controllers.BARController import BARController
from src.messages.BARMessage import BARMessage
from src.messages.BriefcaseBARMessage import BriefcaseBARMessage
from src.messages.ExchangeBARMessage import ExchangeBARMessage
from src.messages.PromiseBARMessage import PromiseBARMessage
from src.store.tables.ExchangeTable import Exchange
from src.store.tables.Token import Token
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

    def encrypt_txs(self, exchange_type, promised, epoch):
        aes_key = Token.find_one_by_epoch(epoch).key
        if exchange_type == self.BAL:
            txs = self.mempool.get_txs(promised)
            return [self.crypto.get_aes().encrypt(tx.data.hex(), aes_key).decode('ascii') for tx in txs]

    # TODO: add OPT exchange logic
    async def _handle(self, connection: StreamWriter, message: ExchangeBARMessage) -> NoReturn:
        if not await self.is_valid_message(message):
            # TODO: send PoM
            Logger.get_instance().debug_item('Invalid request... sending PoM')

        if self.is_promise_request_valid(message):
            # TODO: send PoM
            Logger.get_instance().debug_item('Invalid history message... sending PoM')

        ser_needed, ser_promised = json.dumps(message.needed), json.dumps(message.promised)

        exchange = Exchange(seed=message.token.bn_signature, sender=False, needed=ser_promised,
                            promised=ser_needed,
                            type=str(message.type), signature=message.signature)
        Exchange.add(exchange)

        promise_message = PromiseBARMessage(message.token, message.to_peer, message.from_peer, message,
                                            message.promised,
                                            message.needed, str(message.type))
        promise_message.compute_signature()

        encrypted_promised_txs = self.encrypt_txs(message.type, message.needed, message.token.epoch)
        briefcase_message = BriefcaseBARMessage(message.token, message.to_peer, message.from_peer, message,
                                                encrypted_promised_txs)

        briefcase_message.compute_signature()

        await self.send(connection, promise_message)
        await asyncio.sleep(0.1) # there is a bug in asyncio, need to sleep or message is not sent for some reason god only knows
        await self.send(connection, briefcase_message)


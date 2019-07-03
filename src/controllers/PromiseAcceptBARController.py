import json
import math
from asyncio import StreamWriter
from typing import NoReturn, List

from src.controllers.BARController import BARController
from src.messages.BARMessage import BARMessage
from src.messages.BriefcaseBARMessage import BriefcaseBARMessage
from src.messages.ExchangeBARMessage import ExchangeBARMessage
from src.messages.PoMBARMessage import Misbehaviour
from src.messages.PromiseBARMessage import PromiseBARMessage
from src.store.tables.Exchange import Exchange
from src.store.tables.Token import Token
from src.utils.Constants import MAX_UPDATE_PER_BAL, MAX_UPDATE_PER_OPT, RATIO_PROMISED_FAKE
from src.utils.Logger import Logger, LogLevels


class PromiseAcceptBARController(BARController):
    BAL = 'Balanced Exchange'
    OPT = 'Optimistic Exchange'

    @staticmethod
    def is_valid_controller_for(message: BARMessage) -> bool:
        return isinstance(message, ExchangeBARMessage)

    def is_promise_request_valid(self, message: ExchangeBARMessage):
        for tx in message.needed:
            if not self.mempool.has(tx):
                Logger.get_instance().debug_item('Wrong needed', LogLevels.ERROR)
                return False
        for tx in message.promised:
            if self.mempool.has(tx):
                Logger.get_instance().debug_item('Wrong promised', LogLevels.ERROR)
                return False
        if not self.is_bar_or_opt(message) and not self.is_valid_bar(message) and not self.is_valid_opt(message):
            return False
        return True

    def is_bar_or_opt(self, message: ExchangeBARMessage):
        return message.type == self.BAL or message.type == self.OPT

    def is_valid_bar(self, message: ExchangeBARMessage):
        if message.type == self.BAL and len(message.needed) != len(message.promised) and len(
                message.needed) > MAX_UPDATE_PER_BAL:
            return False
        return True

    def is_valid_opt(self, message: ExchangeBARMessage):
        if message.type == self.OPT and len(message.needed) > MAX_UPDATE_PER_OPT and len(
                message.promised) > MAX_UPDATE_PER_OPT:
            return False
        return True

    def encrypt_txs(self, exchange_type, promised: List[str], needed: List[str], epoch: int):
        aes_key = Token.find_one_by_epoch(epoch).key
        if exchange_type == self.BAL:
            txs = self.mempool.get_txs(promised)
            return [self.crypto.get_aes().encrypt(tx.data.hex(), aes_key).decode('ascii') for tx in txs]
        elif exchange_type == self.OPT:
            if len(promised) < len(needed):
                txs = self.mempool.get_txs(promised)
                return [self.crypto.get_aes().encrypt(tx.data.hex(), aes_key).decode('ascii') for tx in txs]
            else:
                txs = self.mempool.get_txs(promised)
                bf = [self.crypto.get_aes().encrypt(tx.data.hex(), aes_key).decode('ascii') for tx in txs]
                n_fake_txs = math.ceil((len(promised) - len(needed)) * RATIO_PROMISED_FAKE)
                fake_txs = self.mempool.get_fake_txs(n_fake_txs)
                return bf + [self.crypto.get_aes().encrypt(tx.hex(), aes_key).decode('ascii') for tx in fake_txs]

    async def _handle(self, connection: StreamWriter, message: ExchangeBARMessage) -> NoReturn:
        if not await self.is_valid_message(message):
            Logger.get_instance().debug_item('Invalid request... sending PoM')
            await self.send_pom(Misbehaviour.BAD_SEED, message, connection)

        if not self.is_promise_request_valid(message):
            Logger.get_instance().debug_item('Invalid history message... sending PoM')
            await self.send_pom(Misbehaviour.BAD_PROMISE, message, connection)
            return

        ser_needed, ser_promised = json.dumps(message.needed), json.dumps(message.promised)

        exchange = Exchange(seed=message.token.bn_signature, sender=False, needed=ser_promised,
                            promised=ser_needed,
                            type=str(message.type), signature=message.signature, valid=False)
        Exchange.add(exchange)

        promise_message = PromiseBARMessage(message.token, message.to_peer, message.from_peer, message,
                                            message.promised,
                                            message.needed, str(message.type))
        promise_message.compute_signature()

        encrypted_promised_txs = self.encrypt_txs(message.type, message.needed, message.promised, message.token.epoch)
        briefcase_message = BriefcaseBARMessage(message.token, message.to_peer, message.from_peer, message,
                                                encrypted_promised_txs)
        briefcase_message.compute_signature()

        await self.send(connection, promise_message)
        await self.send(connection, briefcase_message)

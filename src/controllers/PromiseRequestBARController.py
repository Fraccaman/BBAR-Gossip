import json
import random
from asyncio import StreamWriter
from typing import NoReturn, List, Tuple, Set

from src.controllers.BARController import BARController
from src.mempool.Mempool import Mempool
from src.messages.BARMessage import BARMessage
from src.messages.ExchangeBARMessage import ExchangeBARMessage
from src.messages.HistoryDivulgeBARMessage import HistoryDivulgeBARMessage
from src.messages.PoMBARMessage import Misbehaviour
from src.store.tables.Exchange import Exchange
from src.utils.Constants import MAX_UPDATE_PER_BAL, MAX_UPDATE_PER_OPT
from src.utils.Logger import Logger, LogLevels


class PromiseRequestBARController(BARController):
    BAL = 'Balanced Exchange'
    OPT = 'Optimistic Exchange'
    ABORT = 'Abort'

    @staticmethod
    def is_valid_controller_for(message: BARMessage) -> bool:
        return isinstance(message, HistoryDivulgeBARMessage)

    @staticmethod
    def get_random_from_list(entries, n):
        return random.sample(entries, n) if n < len(entries) else entries

    # TODO: add OPT exchange rules
    def select_exchanges(self, type, needed, promised, n) -> Tuple[List[str], List[str]]:
        if type == self.BAL:
            needed, promised = self.get_random_from_list(needed, n), self.get_random_from_list(promised, n)
            return [tx for tx in needed], [tx for tx in promised]
        else:
            needed, promised = self.get_random_from_list(needed, n), self.get_random_from_list(promised, n)
            return [tx for tx in needed], [tx for tx in promised]

    def bal_or_opt_exchange(self, needed: Set[str], promised: Set[str]) -> Tuple[str, int]:
        if len(needed) >= MAX_UPDATE_PER_BAL and len(promised) >= MAX_UPDATE_PER_BAL:
            Logger.get_instance().debug_item('BAL (1) exchange selected', LogLevels.INFO)
            return self.BAL, MAX_UPDATE_PER_BAL
        elif len(needed) <= len(promised):
            Logger.get_instance().debug_item('BAL (2) exchange selected', LogLevels.INFO)
            return self.BAL, len(needed)
        elif len(needed) == 0 and len(promised) == 0:
            Logger.get_instance().debug_item('ABORT (2) exchange selected', LogLevels.INFO)
            return self.ABORT, -1
        elif len(needed) == 0:
            Logger.get_instance().debug_item('ABORT (2) exchange selected', LogLevels.INFO)
            return self.ABORT, -1
        elif len(promised) == 0:
            Logger.get_instance().debug_item(
                'OPT (1) exchange selected, needed: {}, promised: {}'.format(len(needed), len(promised)),
                LogLevels.INFO)
            return self.OPT, MAX_UPDATE_PER_OPT
        else:
            Logger.get_instance().debug_item(
                'OPT (2) exchange selected, needed: {}, promised: {}'.format(len(needed), len(promised)),
                LogLevels.INFO)
            return self.OPT, MAX_UPDATE_PER_OPT

    async def _handle(self, connection: StreamWriter, message: HistoryDivulgeBARMessage) -> NoReturn:
        if not await self.is_valid_message(message):
            await self.send_pom(Misbehaviour.BAD_SEED, message, connection)
            Logger.get_instance().debug_item('Invalid request ... sending PoM')
            return

        partner_mempool = Mempool.deserialize(message.elements)
        intersection_set_a_b = Mempool.get_diff(self.mempool.frozen_mp, partner_mempool)
        intersection_set_b_a = Mempool.get_diff(partner_mempool, self.mempool.frozen_mp)

        exchange_type, exchange_number = self.bal_or_opt_exchange(intersection_set_b_a, intersection_set_a_b)
        if exchange_type == self.ABORT:
            exchange = Exchange(seed=message.token.bn_signature, sender=True, needed=json.dumps([]),
                                promised=json.dumps([]),
                                type=exchange_type, signature='', valid=True)
            Exchange.add(exchange)
            return
        needed, promised = self.select_exchanges(exchange_type, intersection_set_b_a, intersection_set_a_b,
                                                 exchange_number)

        ser_needed, ser_promised = json.dumps(needed), json.dumps(promised)
        exchange = Exchange(seed=message.token.bn_signature, sender=True, needed=ser_needed, promised=ser_promised,
                            type=exchange_type, signature='', valid=False)

        Exchange.add(exchange)

        exchange_message = ExchangeBARMessage(message.token, message.to_peer, message.from_peer, message, needed,
                                              promised, exchange_type)
        exchange_message.compute_signature()

        await self.send(connection, exchange_message)

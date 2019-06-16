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
from src.store.iblt.iblt import IBLT
from src.store.tables.Exchange import Exchange
from src.utils.Constants import MAX_UPDATE_PER_BAL, MAX_UPDATE_PER_OPT
from src.utils.Logger import Logger


class PromiseRequestBARController(BARController):
    BAL = 'Balanced Exchange'
    OPT = 'Optimistic Exchange'

    @staticmethod
    def is_valid_controller_for(message: BARMessage) -> bool:
        return isinstance(message, HistoryDivulgeBARMessage)

    @staticmethod
    def get_random_from_list(entries, n):
        return random.sample(entries, n)

    # TODO: add OPT exchange rules
    def select_exchanges(self, type, needed, promised, n) -> Tuple[List[str], List[str]]:
        if type == self.BAL:
            needed, promised = self.get_random_from_list(needed, n), self.get_random_from_list(promised, n)
            return [tx for tx in needed], [tx for tx in promised]
        else:
            return ([], [])

    def bal_or_opt_exchange(self, needed: Set[str], promised: Set[str]) -> Tuple[str, int]:
        if len(needed) >= MAX_UPDATE_PER_BAL and len(promised) >= MAX_UPDATE_PER_BAL:
            return self.BAL, MAX_UPDATE_PER_BAL
        elif len(needed) <= len(promised):
            return self.BAL, len(needed)
        else:
            return self.OPT, MAX_UPDATE_PER_OPT

    async def _handle(self, connection: StreamWriter, message: HistoryDivulgeBARMessage) -> NoReturn:
        if not await self.is_valid_message(message):
            await self.send_pom(Misbehaviour.BAD_SEED, message, connection)
            Logger.get_instance().debug_item('Invalid request ... sending PoM')
            return

        partner_mempool = Mempool.deserialize(message.elements)
        intersection_set_a_b = Mempool.get_diff(self.mempool.mp, partner_mempool)

        intersection_set_b_a = Mempool.get_diff(partner_mempool, self.mempool.mp)

        exchange_type, exchange_number = self.bal_or_opt_exchange(intersection_set_b_a, intersection_set_a_b)
        needed, promised = self.select_exchanges(exchange_type, intersection_set_b_a, intersection_set_a_b, exchange_number)

        ser_needed, ser_promised = json.dumps(needed), json.dumps(promised)
        exchange = Exchange(seed=message.token.bn_signature, sender=True, needed=ser_needed, promised=ser_promised,
                            type=exchange_type, signature='')

        Exchange.add(exchange)

        exchange_message = ExchangeBARMessage(message.token, message.to_peer, message.from_peer, message, needed,
                                              promised, exchange_type)
        exchange_message.compute_signature()

        await self.send(connection, exchange_message)

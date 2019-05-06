import json
import random
from asyncio import StreamWriter
from typing import NoReturn, List, Tuple

from src.controllers.BARController import BARController
from src.mempool.Mempool import Mempool
from src.messages.BARMessage import BARMessage
from src.messages.ExchangeBARMessage import ExchangeBARMessage
from src.messages.HistoryDivulgeBARMessage import HistoryDivulgeBARMessage
from src.store.iblt.iblt import IBLT
from src.store.tables.ExchangeTable import Exchange
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
            return self.get_random_from_list(needed, n), self.get_random_from_list(promised, n)

    def bal_or_opt_exchange(self, needed: List[Tuple[str, str]], promised: List[Tuple[str, str]]) -> Tuple[str, int]:
        if len(needed) >= MAX_UPDATE_PER_BAL and len(promised) >= MAX_UPDATE_PER_BAL:
            return self.BAL, MAX_UPDATE_PER_BAL
        elif len(needed) <= len(promised):
            return self.BAL, len(needed)
        else:
            return self.OPT, MAX_UPDATE_PER_OPT

    async def _handle(self, connection: StreamWriter, message: HistoryDivulgeBARMessage) -> NoReturn:
        if not await self.is_valid_message(message):
            # TODO: send PoM
            Logger.get_instance().debug_item('Invalid request ... sending PoM')
        partner_iblt: IBLT = Mempool.deserialize(bytes.fromhex(message.elements))
        intersection_iblt_a_b: IBLT = self.mempool.iblt.subtract(partner_iblt)
        res_a_b, entries_a_b, deleted_a_b = intersection_iblt_a_b.list_entries()

        intersection_iblt_b_a: IBLT = partner_iblt.subtract(self.mempool.iblt)
        res_b_a, entries_b_a, deleted_b_a = intersection_iblt_b_a.list_entries()

        exchange_type, exchange_number = self.bal_or_opt_exchange(entries_a_b, entries_b_a)
        needed, promised = self.select_exchanges(exchange_type, entries_a_b, entries_b_a, exchange_number)

        ser_needed, ser_promised = json.dumps(needed), json.dumps(promised)
        exchange = Exchange(seed=message.token.bn_signature, sender=True, needed=ser_needed, promised=ser_promised,
                            type=exchange_type, signature='')
        Exchange.add(exchange)

        exchange_message = ExchangeBARMessage(message.token, message.to_peer, message.from_peer, message, ser_needed,
                                              ser_promised, exchange_type)
        exchange_message.compute_signature()

        await self.send(connection, exchange_message)

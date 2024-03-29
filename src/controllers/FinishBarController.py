import json
from asyncio import StreamWriter

from src.controllers.BARController import BARController
from src.mempool.Mempool import Data
from src.messages.BARMessage import BARMessage
from src.messages.KeyBARMessage import KeyBARMessage
from src.messages.PoMBARMessage import Misbehaviour
from src.store.tables.Exchange import Exchange
from src.store.tables.MempoolDisk import MempoolDisk
from src.utils.Logger import Logger


class FinishBARController(BARController):

    @staticmethod
    def is_valid_controller_for(message: BARMessage) -> bool:
        return isinstance(message, KeyBARMessage)

    def decrypt_briefcase(self, briefcase, key):
        try:
            briefcase = json.loads(briefcase)
            if briefcase is None:
                return None
            for index, encrypted_tx in enumerate(briefcase):
                briefcase[index] = self.crypto.get_aes().decrypt(encrypted_tx.encode(), key).decode()
            return [Data(bytes.fromhex(tx)) for tx in briefcase]
        except Exception as e:
            Logger.get_instance().debug_item('Invalid briefcase decrypt, {}'.format(e))
            return None

    @staticmethod
    def is_valid_data(promised, data):
        promised_set = set(json.loads(promised))
        data_set = [tx.short_hash for tx in data]
        return set(data_set).issubset(promised_set) or set(promised_set).issubset(data_set)

    async def _handle(self, connection: StreamWriter, message: KeyBARMessage):
        if not await self.is_valid_message(message):
            Logger.get_instance().debug_item('Invalid request... sending PoM')
            await self.send_pom(Misbehaviour.BAD_SEED, message, connection)
        else:
            exchange = Exchange.get_exchange(message.token.bn_signature)
            data = self.decrypt_briefcase(exchange.briefcase, message.key)
            if not self.is_valid_data(exchange.needed, data):
                Logger.get_instance().debug_item('Invalid data... sending PoM')
                await self.send_pom(Misbehaviour.BAD_BRIEFCASE, message, connection)
                return

            Exchange.set_valid(message.token.bn_signature)

            txs = [MempoolDisk(data=tx.data, short_id=tx.short_hash, full_id=tx.hash) for tx in data]
            real_txs = list(filter(lambda tx: tx.short_id in set(json.loads(exchange.needed)), txs))
            added = MempoolDisk.add_if_new(real_txs)
            self.mempool.insert(txs, added)

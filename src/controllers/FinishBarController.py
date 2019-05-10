import json
from asyncio import StreamWriter

from src.controllers.BARController import BARController
from src.mempool.Mempool import Data
from src.messages.BARMessage import BARMessage
from src.messages.KeyBARMessage import KeyBARMessage
from src.store.tables.MempoolDisk import MempoolDisk
from src.store.tables.ExchangeTable import Exchange
from src.utils.Logger import Logger


class FinishBARController(BARController):

    @staticmethod
    def is_valid_controller_for(message: BARMessage) -> bool:
        return isinstance(message, KeyBARMessage)

    def decrypt_briefcase(self, briefcase, key):
        try:
            briefcase = json.loads(briefcase)
            for index, encrypted_tx in enumerate(briefcase):
                briefcase[index] = self.crypto.get_aes().decrypt(encrypted_tx.encode(), key).decode()
            return [Data(bytes.fromhex(tx)) for tx in briefcase]
        except Exception as _:
            return None

    @staticmethod
    def is_valid_data(promised, data):
        return data and set(json.loads(promised)) == set([tx.short_hash for tx in data])

    async def _handle(self, connection: StreamWriter, message: KeyBARMessage):
        if not await self.is_valid_message(message):
            # TODO: send PoM
            Logger.get_instance().debug_item('Invalid request... sending PoM')

        exchange = Exchange.get_exchange(message.token.bn_signature)
        data = self.decrypt_briefcase(exchange.briefcase, message.key)
        if not self.is_valid_data(exchange.promised, data):
            # TODO: send PoM
            Logger.get_instance().debug_item('Invalid promised data... sending PoM')

        txs = [MempoolDisk(data=tx.data, short_id=tx.short_hash, full_id=tx.hash) for tx in data]
        MempoolDisk.add_multiple(txs)

        await self.close_connection(connection)









import json
from asyncio import StreamWriter

from src.controllers.BARController import BARController
from src.messages.BARMessage import BARMessage
from src.messages.BriefcaseBARMessage import BriefcaseBARMessage
from src.messages.PoMBARMessage import Misbehaviour
from src.messages.PromiseBARMessage import PromiseBARMessage
from src.store.tables.ExchangeTable import Exchange
from src.store.tables.Token import Token
from src.utils.Logger import Logger


class BriefcaseBARController(BARController):

    @staticmethod
    def is_valid_controller_for(message: BARMessage) -> bool:
        return isinstance(message, PromiseBARMessage)

    @staticmethod
    def string_to_set(string):
        return set(json.loads(string))

    def is_valid_promise(self, ser_needed, ser_promised, seed):
        trade = Exchange.get_exchange(seed)
        if self.string_to_set(trade.needed) == self.string_to_set(ser_promised) \
                and self.string_to_set(trade.promised) == self.string_to_set(ser_needed):
            return True
        return False

    def encrypt_txs(self, promised, epoch):
        aes_key = Token.find_one_by_epoch(epoch).key
        txs = self.mempool.get_txs(promised)
        return [self.crypto.get_aes().encrypt(tx.data.hex(), aes_key).decode('ascii') for tx in txs]

    async def _handle(self, connection: StreamWriter, message: PromiseBARMessage):
        if not await self.is_valid_message(message):
            Logger.get_instance().debug_item('Invalid request... sending PoM 1')
            await self.send_pom(Misbehaviour.BAD_SEED, message, connection)
            return

        ser_needed, ser_promised = json.dumps(message.needed), json.dumps(message.promised)
        valid_promise = self.is_valid_promise(ser_needed, ser_promised, message.token.bn_signature)
        if not valid_promise:
            Logger.get_instance().debug_item('Invalid request... sending PoM 2')
            await self.send_pom(Misbehaviour.BAD_PROMISE_ACCEPT, message, connection)
            return

        Exchange.add_signature(message.token.bn_signature, message.signature)

        encrypted_promised_txs = self.encrypt_txs(message.needed, message.token.epoch)
        briefcase_message = BriefcaseBARMessage(message.token, message.to_peer, message.from_peer, message,
                                                encrypted_promised_txs)
        briefcase_message.compute_signature()

        await self.send(connection, briefcase_message)

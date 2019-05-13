import json
from asyncio import StreamWriter

from src.controllers.BARController import BARController
from src.messages.BARMessage import BARMessage
from src.messages.KeyBARMessage import KeyBARMessage
from src.messages.KeyRequestBARMessage import KeyRequestBARMessage
from src.store.tables.Token import Token
from src.utils.Logger import Logger


class KeyBARController(BARController):

    @staticmethod
    def is_valid_controller_for(message: BARMessage) -> bool:
        return isinstance(message, KeyRequestBARMessage)

    def decrypt_briefcase(self, briefcase, key):
        plaintext = self.crypto.get_aes().decrypt(briefcase, key)
        try:
            return json.loads(plaintext)
        except Exception:
            return None

    @staticmethod
    def is_valid_data(promised, data):
        return json.loads(promised) == data

    async def _handle(self, connection: StreamWriter, message: KeyRequestBARMessage):
        if not await self.is_valid_message(message):
            # TODO: send PoM
            Logger.get_instance().debug_item('Invalid request... sending PoM cose')

        key = Token.find_one_by_epoch(message.token.epoch).key

        key_message = KeyBARMessage(message.token, message.to_peer, message.from_peer, message, key)
        key_message.compute_signature()

        await self.send(connection, key_message)

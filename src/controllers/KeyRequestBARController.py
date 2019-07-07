import asyncio
import json
from asyncio import StreamWriter

from src.controllers.BARController import BARController
from src.messages.BARMessage import BARMessage
from src.messages.BriefcaseBARMessage import BriefcaseBARMessage
from src.messages.KeyRequestBARMessage import KeyRequestBARMessage
from src.messages.PoMBARMessage import Misbehaviour
from src.store.tables.Exchange import Exchange
from src.utils.Logger import Logger


class KeyRequestBARController(BARController):

    @staticmethod
    def is_valid_controller_for(message: BARMessage) -> bool:
        return isinstance(message, BriefcaseBARMessage)

    @staticmethod
    def is_valid_exchange_entry(seed):
        return Exchange.get_exchange(seed) is None

    async def _handle(self, connection: StreamWriter, message: BriefcaseBARMessage):
        if not await self.is_valid_message(message):
            await self.send_pom(Misbehaviour.BAD_SEED, message, connection)
            Logger.get_instance().debug_item('Invalid request... sending PoM')
        else:
            while self.is_valid_exchange_entry(message.token.bn_signature):
                await asyncio.sleep(0.5)
                Logger.get_instance().debug_item('Waiting for accept promise ...')

            ser_briefcase = json.dumps(message.data)
            Exchange.add_briefcase(message.token.bn_signature, ser_briefcase)

            key_req_message = KeyRequestBARMessage(message.token, message.to_peer, message.from_peer, message)

            key_req_message.set_byzantine(self.config.get('byzantine'))
            key_req_message.compute_signature()

            await self.send(connection, key_req_message)

from typing import NoReturn

from src.cryptography.Crypto import Crypto
from src.messages.Message import Message
from src.store.tables.Epoch import Epoch


class TokenMessage(Message):

    def __init__(self, base, proof):
        self.base = base
        self.proof = proof
        self.bn_signature = None
        self.epoch = self.get_current_epoch()

    def bn_sign(self) -> NoReturn:
        message = (self.base + self.proof + self.epoch).encode('utf-8')
        self.bn_signature = Crypto.get_instance().get_ec().sign(message)

    def get_epoch(self) -> str:
        return self.epoch

    def regenerate_token(self):
        next_epoch = self.get_next_epoch()
        message = (self.base + self.proof + next_epoch).encode('utf-8')
        self.bn_signature = Crypto.get_instance().get_ec().sign(message)
        self.epoch = next_epoch
        return self

    def set_next_epoch(self) -> NoReturn:
        self.epoch = self.get_next_epoch()

    @staticmethod
    def get_next_epoch() -> str:
        return Epoch.get_next_epoch().epoch.__str__()

    @staticmethod
    def get_current_epoch() -> str:
        return Epoch.get_current_epoch().epoch.__str__()

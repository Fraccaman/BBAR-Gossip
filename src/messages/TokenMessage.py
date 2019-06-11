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
        self.key = self.compute_key()

    def compute_key(self):
        return Crypto.get_instance().get_hasher().hash(
            Crypto.get_instance().get_ec().private_key.to_bytes(length=256, byteorder='big', signed=True) +
            self.epoch.encode() +
            self.get_peer_public_key().encode()
        )

    def get_peer_public_key(self) -> str:
        return self.base.split('-')[0]

    def bn_sign(self) -> NoReturn:
        message = (self.base + self.proof + self.epoch).encode('utf-8')
        self.bn_signature = Crypto.get_instance().get_ec().sign(message)

    def get_epoch(self) -> str:
        return self.epoch

    def set_next_epoch(self) -> NoReturn:
        self.epoch = self.get_next_epoch()

    @staticmethod
    def get_next_epoch() -> str:
        return Epoch.get_next_epoch().epoch.__str__()

    @staticmethod
    def get_current_epoch() -> str:
        return Epoch.get_current_epoch().epoch.__str__()

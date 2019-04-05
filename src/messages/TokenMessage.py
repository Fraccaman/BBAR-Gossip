from src.cryptography.Crypto import Crypto
from src.messages.Message import Message
from src.store.tables.Epoch import Epoch


class TokenMessage(Message):

    def __init__(self, base, proof):
        self.base = base
        self.proof = proof
        self.bn_signature = None
        self.epoch = self.get_next_epoch()

    def bn_sign(self):
        message = (self.base + self.proof + self.epoch).encode('utf-8')
        self.bn_signature = Crypto.get_instance().get_ec().sign(message)

    def get_epoch(self):
        return self.epoch

    def regenerate_token(self):
        next_epoch = self.get_next_epoch()
        message = (self.base + self.proof + next_epoch).encode('utf-8')
        self.bn_signature = Crypto.get_instance().get_ec().sign(message)
        self.epoch = next_epoch
        return self

    @staticmethod
    def get_next_epoch():
        return Epoch.get_next_epoch().epoch.__str__()


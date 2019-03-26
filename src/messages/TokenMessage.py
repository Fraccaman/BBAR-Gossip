from src.cryptography.Crypto import Crypto
from src.messages.Message import Message


class TokenMessage(Message):

    def __init__(self, base, proof):
        self.base = base
        self.proof = proof
        self.bn_signature = None

    def bn_sign(self):
        message = (self.base + self.proof).encode('utf-8')
        self.bn_signature = Crypto.get_instance().get_ec().sign(message)

from src.cryptography.Crypto import Crypto
from src.messages.Message import Message


class RenewTokenMessage(Message):

    def __init__(self, base, proof, token, epoch):
        self.base = base
        self.proof = proof
        self.bn_signature = token
        self.epoch = epoch

    def is_valid_signature(self):
        return Crypto.get_instance().get_ec().verify(self.bn_signature,
                                                     (self.base + self.proof + str(self.epoch)).encode('utf-8'),
                                                     Crypto.get_instance().get_ec().public_key)

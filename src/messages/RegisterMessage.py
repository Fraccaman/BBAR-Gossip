from fastecdsa.point import Point

from src.cryptography.Crypto import Crypto
from src.messages.Message import Message


class RegisterMessage(Message):

    def __init__(self, difficulty: float, epoch: int, public_key: Point):
        self.difficulty = difficulty
        self.puzzle = self.generate_puzzle(epoch, public_key)

    @staticmethod
    def generate_puzzle(epoch: int, public_key: Point):
        nonce = Crypto().get_instance().get_random().generate_random_bytes()
        formatted_public_key = Crypto.get_instance().get_ec().dump_public_key(public_key)
        return '{}-{}-{}'.format(formatted_public_key, epoch, nonce)

    def get_epoch(self):
        return self.puzzle.split('-')[1]

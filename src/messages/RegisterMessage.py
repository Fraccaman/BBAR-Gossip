from src.cryptography.RandomGenerator import RandomGenerator
from src.messages.Message import Message
from src.messages.MessageType import MessageType


class RegisterMessage(Message):

    def __init__(self, difficulty: int, epoch: int, public_key: str):
        super().__init__(MessageType.REGISTER)
        self.difficulty = difficulty
        self.puzzle = self.generate_puzzle(epoch, public_key)

    @staticmethod
    def generate_puzzle(epoch: int, public_key: str):
        nonce = RandomGenerator.generate_random_bytes()
        return '{}-{}-{}'.format(public_key, epoch, nonce)

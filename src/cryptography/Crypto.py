from src.cryptography.EllipticCurve import EllipticCurve
from src.cryptography.RandomGenerator import RandomGenerator
from src.utils.Singleton import Singleton


class Crypto(metaclass=Singleton):

    def __init__(self, private_key=None):
        self.ec = EllipticCurve(private_key)
        self.random = RandomGenerator()

    @staticmethod
    def get_instance():
        return Crypto()

    @staticmethod
    def get_ec():
        return Crypto().ec

    @staticmethod
    def get_random():
        return Crypto().random

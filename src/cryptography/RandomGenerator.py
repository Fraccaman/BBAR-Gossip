import random
import secrets


class RandomGenerator:

    @staticmethod
    def generate_random_bytes(length: int = 16):
        return secrets.token_hex(length)

    @staticmethod
    def prng(seed, upperbound, length=1):
        r = random.seed(seed)
        return [r.randint(0, upperbound) for _ in range(length)]

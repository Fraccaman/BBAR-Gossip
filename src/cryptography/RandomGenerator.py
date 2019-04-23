import random
import secrets


class RandomGenerator:

    @staticmethod
    def generate_random_bytes(length: int = 16):
        return secrets.token_hex(length)

    @staticmethod
    def prng(seed, upperbound, length=1):
        random.seed(seed)
        return [random.randint(0, upperbound) for _ in range(length)]

    @staticmethod
    def pnrg_next(seed, upperbound):
        l = RandomGenerator.prng(seed, upperbound)
        return l[0]

    @staticmethod
    def prng_unique(seed, upperbound, length=1):
        random.seed(seed)
        return random.sample([i for i in range(0, upperbound)], length)

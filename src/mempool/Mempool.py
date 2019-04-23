import hashlib
import pickle
from lru import LRU

from src.cryptography.Crypto import Crypto
from src.store.iblt.pyblt import PYBLT


class Data:
    HASH_FUNCTION = 'sha256'

    def __init__(self, data):
        self.data = data
        self.hash = self._compute_hash()

    def _compute_hash(self):
        return Crypto().get_hasher().hash(self.data)

    def serialize(self):
        return pickle.dumps(self)

    @staticmethod
    def deserialize(data: bytes):
        return pickle.loads(data)


class Mempool:
    HASH_FUNCTION = 'ripemd160'

    def __init__(self, n: int = 1000, key_size: int = 40):
        self.iblt = PYBLT(n, key_size)
        self.cache = LRU(n)
        self.size = n
        self.actual_size = 0

    def _hash(self, element):
        return hashlib.new(self.HASH_FUNCTION, str(element).encode()).hexdigest()

    @staticmethod
    def _split_key_value(element_hash):
        return int(element_hash, 16), element_hash

    def insert(self, element):
        element_hash = self._hash(element)
        key, value = self._split_key_value(element_hash)
        self.iblt.insert(key, value)
        self.actual_size = self.actual_size + 1

    def serialize(self):
        return pickle.dumps(self)

    @staticmethod
    def deserialize(data: bytes):
        return pickle.loads(data)

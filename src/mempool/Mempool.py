import hashlib
import pickle
from typing import Union, List

from src.cryptography.Crypto import Crypto
from src.store.iblt.iblt import IBLT
from src.store.tables.MempoolDisk import MempoolDisk
from src.utils.Logger import Logger, LogLevels
from src.utils.Singleton import Singleton


class Data:
    HASH_FUNCTION = 'sha256'
    SHORT_HASH_FUNCTION = 'ripemd160'

    def __init__(self, data):
        self.data = data
        self.hash = self._compute_hash()

    def _compute_hash(self):
        return Crypto().get_hasher().hash(self.data)

    @property
    def short_hash(self):
        return hashlib.new(self.SHORT_HASH_FUNCTION, self.data).hexdigest()

    def serialize(self):
        return pickle.dumps(self)

    @staticmethod
    def deserialize(data: bytes):
        return pickle.loads(data)


class Mempool(metaclass=Singleton):
    HASH_FUNCTION = 'ripemd160'

    def __init__(self, n: int = 1000, key_size: int = 40):
        self.iblt = IBLT(1500, 4, 40, 64)
        self.size = n
        self.key_size = key_size
        self.actual_size = 0
        self.init()

    def _hash_short(self, element: Union[Data, str]):
        if isinstance(element, Data):
            return hashlib.new(self.HASH_FUNCTION, str(element.serialize()).encode()).hexdigest()
        if isinstance(element, bytes):
            return hashlib.new(self.HASH_FUNCTION, element).hexdigest()
        return hashlib.new(self.HASH_FUNCTION, element.encode()).hexdigest()

    def insert(self, txs: List[Data]):
        for tx in txs:
            self.iblt.insert(tx.short_hash, tx.hash)
            self.actual_size = self.actual_size + 1
        if self.actual_size > self.size:
            Logger.get_instance().debug_item('IBLT FULL', LogLevels.WARNING)

    @staticmethod
    def _split_key_value(element_hash):
        return str(int(element_hash, 16)), element_hash

    def serialize(self):
        return self.iblt.serialize()

    def get_diff(self, other: IBLT):
        return self.iblt.subtract(other)

    @staticmethod
    def deserialize(data: bytes):
        return IBLT.unserialize(data)

    def has(self, tx_short_hash):
        key, value = self._split_key_value(tx_short_hash)
        res, item = self.iblt.get(key)
        return True if IBLT.RESULT_GET_MATCH == res else False

    def init(self):
        txs = MempoolDisk.get_all()
        for tx in txs:
            self.iblt.insert(tx.short_id, tx.full_id)
        res, items, _ = self.iblt.list_entries()
        assert (res == 'complete')

    def get_txs(self, ids: List[str]):
        return MempoolDisk.get_txs_by_full_hash(ids)

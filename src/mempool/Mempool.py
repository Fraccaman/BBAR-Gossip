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

    def __init__(self, data: bytes):
        self.data = data
        self.hash = self._compute_hash()

    def _compute_hash(self):
        return Crypto().get_hasher().hash(self.data)

    @property
    def short_hash(self):
        return Crypto().get_hasher().short_hash(self.data)

    def serialize(self):
        return pickle.dumps(self)

    @staticmethod
    def deserialize(data: bytes):
        return pickle.loads(data)


class Mempool(metaclass=Singleton):
    HASH_FUNCTION = 'ripemd160'

    def __init__(self, n: int = 200, key_size: int = 40):
        self.iblt = IBLT(n, 5, 40, 64)
        self.size = n
        self.key_size = key_size
        self.actual_size = 0
        self.init()

    def _hash_short(self, element: Union[Data, str]):
        if isinstance(element, Data):
            return Crypto().get_hasher().short_hash(element.serialize())
        if isinstance(element, bytes):
            return Crypto().get_hasher().short_hash(element)
        return Crypto().get_hasher().short_hash(element.encode())

    def insert(self, txs: List[MempoolDisk], added: List[str]):
        for tx in txs:
            if tx.short_id in added:
                self.iblt.insert(tx.short_id, tx.full_id)
                self.actual_size = self.actual_size + 1
        res, items, _ = self.iblt.list_entries()
        if res != 'complete':
            Logger.get_instance().debug_item('IBLT FULL: {}, actual_size: {}, size: {}'.format(res, self.actual_size, self.size), LogLevels.WARNING)

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

    def has(self, tx_hash):
        res, item = self.iblt.get(tx_hash)
        print(res, item)
        return IBLT.RESULT_GET_MATCH == res

    def init(self):
        txs = MempoolDisk.get_all()
        for tx in txs:
            self.iblt.insert(tx.short_id, tx.full_id)
        res, items, _ = self.iblt.list_entries()
        self.actual_size = len(txs)
        assert (res == 'complete')

    def get_txs(self, ids: List[str]):
        return MempoolDisk.get_txs_by_full_hash(ids)

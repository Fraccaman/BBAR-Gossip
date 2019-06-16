import hashlib
import pickle
from typing import Union, List, Dict, Set

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

    def __init__(self):
        self.mp = set([])
        self._mapping = {}
        self.size = 0
        self.init()

    @staticmethod
    def _hash_short(element: Union[Data, str]):
        if isinstance(element, Data):
            return Crypto().get_hasher().short_hash(element.serialize())
        if isinstance(element, bytes):
            return Crypto().get_hasher().short_hash(element)
        return Crypto().get_hasher().short_hash(element.encode())

    def insert(self, txs: List[MempoolDisk], added: List[str]):
        for tx in txs:
            if tx.short_id in added:
                self.mp.add(tx.short_id)
                self._mapping[tx.short_id] = tx.full_id
                self.size = self.size + 1
        Logger.get_instance().debug_item('I have {} txs in my mempool'.format(self.size), LogLevels.INFO)

    @staticmethod
    def _split_key_value(element_hash):
        return str(int(element_hash, 16)), element_hash

    def serialize(self):
        return pickle.dumps(self.mp)

    @staticmethod
    def get_diff(one: Set[str], two: Set[str]):
        return one.difference(two)

    @staticmethod
    def deserialize(data: bytes):
        return pickle.loads(data)

    def has(self, tx_hash):
        return tx_hash in self.mp

    def init(self):
        txs = MempoolDisk.get_all()
        for tx in txs:
            self.mp.add(tx.short_id)
            self._mapping[tx.short_id] = tx.full_id
        self.size = len(txs)
        Logger.get_instance().debug_item('I have {} txs in my mempool'.format(len(txs)), LogLevels.INFO)
        return len(txs) == len(self.mp)

    def get_txs(self, ids: List[str]):
        return MempoolDisk.get_txs_by_full_hash(ids)

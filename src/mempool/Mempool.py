import asyncio
import pickle
import random
from typing import List, Set

from src.cryptography.Crypto import Crypto
from src.store.tables.MempoolDisk import MempoolDisk
from src.utils.Constants import TRANSACTION_SIZE_MU, TRANSACTION_SIZE_SIGMA, MAX_FAKE_DATA
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
        self.frozen_mp = frozenset(self.mp)
        self._frozen_mp_epoch = -1
        self._mapping = {}
        self.size = 0
        self.fake_data = set([])
        self.init()
        self.lock = asyncio.Lock()

    def insert(self, txs: List[MempoolDisk], added: List[str]):
        old_size = self.size
        for tx in txs:
            if tx.short_id in added:
                self.mp.add(tx.short_id)
                self._mapping[tx.short_id] = tx.full_id
                self.size = self.size + 1
        Logger.get_instance().debug_item('I had {} txs and now I have {} txs in my mempool'.format(old_size, self.size),
                                         LogLevels.INFO)

    def serialize(self):
        return pickle.dumps(self.frozen_mp)

    @staticmethod
    def get_diff(one: Set[str], two: Set[str]):
        return one.difference(two)

    @staticmethod
    def deserialize(data: bytes):
        return pickle.loads(data)

    def has(self, tx_hash):
        return tx_hash in self.frozen_mp

    def init(self):
        txs = MempoolDisk.get_all()
        for tx in txs:
            self.mp.add(tx.short_id)
            self._mapping[tx.short_id] = tx.full_id
        for i in range(MAX_FAKE_DATA):
            transaction = bytearray(random.getrandbits(8) for _ in range(int(random.normalvariate(TRANSACTION_SIZE_MU,
                                                                                                  TRANSACTION_SIZE_SIGMA))))
            self.fake_data.add(transaction.hex())
        self.size = len(txs)
        self.frozen_mp = frozenset(self.mp)
        Logger.get_instance().debug_item('I have {} txs in my mempool'.format(len(txs)), LogLevels.INFO)
        return len(txs) == len(self.mp)

    @staticmethod
    def get_txs(ids: List[str]):
        return MempoolDisk.get_txs_by_full_hash(ids)

    def get_fake_txs(self, n):
        return list(map(lambda x: bytes.fromhex(x), random.choices(list(self.fake_data), k=n)))

    async def freeze(self, epoch):
        async with self.lock:
            if self._frozen_mp_epoch != epoch:
                self._frozen_mp_epoch = epoch
                self.frozen_mp = frozenset(self.mp)
                Logger.get_instance().debug_item('Mempool frozen!', LogLevels.INFO)
            else:
                Logger.get_instance().debug_item('Mempool already frozen!', LogLevels.INFO)

    @staticmethod
    def get_instance():
        return Mempool()

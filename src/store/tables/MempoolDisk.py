import math
import pickle
import random
from copy import deepcopy
from typing import List

from sqlalchemy import Column, String, BLOB, event, or_

from src.cryptography.Crypto import Crypto
from src.store.Base import Base
from src.store.BaseMixin import BaseMixin


class MempoolDisk(BaseMixin, Base):
    data = Column(BLOB)
    short_id = Column(String(40), unique=True)
    full_id = Column(String(64), unique=True)

    @classmethod
    def get_last_n_entries(cls, n):
        return reversed(cls.get_session().query(cls).order_by(cls.id.desc()).limit(n).all())

    @classmethod
    def get_txs_by_full_hash(cls, hashes: List[str]):
        return cls.get_session().query(cls).filter(cls.short_id.in_(hashes)).all()

    @classmethod
    def add_if_new(cls, txs):
        added = []
        for tx in txs:
            exists = cls.get_session().query(cls).filter(or_(cls.full_id==tx.full_id,cls.short_id==tx.short_id)).first()
            if not exists:
                added.append(tx.short_id)
                cls.add(tx)
            else:
                print('duplicate {}'.format(tx.short_id))
        return added


def insert_data(target, connection, **kw):
    with open('/Users/fraccaman/Projects/BlockchainBar/network/data.data', 'rb') as data:
        transactions = pickle.loads(data.read())
        known_transactions = random.sample(transactions, k=len(transactions) - math.floor(len(transactions) * 0.9))
        for known_tx in known_transactions:
            d = bytearray.fromhex(known_tx[0])
            d_short_hash = Crypto.get_instance().get_hasher().short_hash(d)
            d_full_hash = Crypto.get_instance().get_hasher().hash(d)
            connection.execute(target.insert(), {'data': d, 'short_id': d_short_hash,
                                                 'full_id': d_full_hash})


event.listen(MempoolDisk.__table__, 'after_create', insert_data)

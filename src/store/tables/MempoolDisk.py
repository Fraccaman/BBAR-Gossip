import math
import pickle
import random

from sqlalchemy import Column, String, BLOB, event

from src.store.Base import Base
from src.store.BaseMixin import BaseMixin


class MempoolDisk(BaseMixin, Base):
    data = Column(BLOB)
    short_id = Column(String(40), unique=True)
    full_id = Column(String(64), unique=True)

    @classmethod
    def get_last_n_entries(cls, n):
        return reversed(cls.get_session().query(cls).order_by(cls.id.desc()).limit(n).all())


def insert_data(target, connection, **kw):
    with open('/Users/fraccaman/Projects/BlockchainBar/network/data.data', 'rb') as data:
        transactions = pickle.loads(data.read())
        known_transactions = random.sample(transactions, k=len(transactions) - math.floor(len(transactions) * 0.8))
        for known_tx in known_transactions:
            connection.execute(target.insert(), {'data': bytearray.fromhex(known_tx[0]), 'short_id': known_tx[2],
                                                 'full_id': known_tx[1]})


event.listen(MempoolDisk.__table__, 'after_create', insert_data)

from sqlalchemy import Column, String, Integer, BLOB

from src.store.Base import Base
from src.store.BaseMixin import BaseMixin


class Mempool(BaseMixin, Base):
    data = Column(BLOB, unique=True)
    short_id = Column(String, unique=True)
    full_id = Column(String, unique=True)
    epoch = Column(Integer)

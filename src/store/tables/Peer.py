from sqlalchemy import Column, String

from src.store.Base import Base
from src.store.BaseMixin import BaseMixin


class Peer(BaseMixin, Base):
    address = Column(String, unique=True)
    pk = Column(String, unique=True)

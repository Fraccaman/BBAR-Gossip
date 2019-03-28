from sqlalchemy import Column, String

from src.store.Base import Base
from src.store.BaseMixin import BaseMixin


class Peer(BaseMixin, Base):
    address = Column(String, unique=True)
    pk = Column(String, unique=True)

    @classmethod
    def add(cls, peer):
        session = cls.get_session()
        session.add(peer)
        session.commit()

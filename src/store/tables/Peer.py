from sqlalchemy import Column, String

from src.store.Base import Base
from src.store.BaseMixin import BaseMixin


class Peer(BaseMixin, Base):
    address = Column(String, unique=True)
    public_key = Column(String, unique=True)

    @classmethod
    def get_all(cls, ids):
        return cls.get_session().query(cls).filter(cls.id.in_(ids)).all()

    def __str__(self):
        return 'address: {}, pk: {}'.format(self.address, self.public_key)

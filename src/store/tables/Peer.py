from sqlalchemy import Column, String, Integer, ForeignKey

from src.store.Base import Base
from src.store.BaseMixin import BaseMixin


class Peer(BaseMixin, Base):
    address = Column(String, unique=True)
    public_key = Column(String, unique=True)
    registration = Column(Integer, ForeignKey('registration.id'))

    @classmethod
    def get_all(cls, ids):
        return cls.get_session().query(cls).filter(cls.id.in_(ids)).all()

    def __str__(self):
        return 'address: {}, public key: {}'.format(self.address, self.public_key)

    @classmethod
    def find_one_by_address(cls, peer_address):
        return cls.get_session().query(cls).filter_by(address=peer_address).one()

    @classmethod
    def find_one_by_public_key(cls, pk):
        return cls.get_session().query(cls).filter_by(public_key=pk).one()

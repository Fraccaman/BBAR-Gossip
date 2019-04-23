from sqlalchemy import Column, String, Integer, ForeignKey, or_

from src.store.Base import Base
from src.store.BaseMixin import BaseMixin


class Peer(BaseMixin, Base):
    address = Column(String, unique=True)
    public_address = Column(String, unique=True)
    public_key = Column(String, unique=True)
    registration = Column(Integer, ForeignKey('registration.id'))

    @classmethod
    def get_all(cls, ids):
        return cls.get_session().query(cls).filter(cls.id.in_(ids)).all()

    def __str__(self):
        return 'address: {}, public key: {}'.format(self.public_address, self.public_key)

    @classmethod
    def find_one_by_address(cls, peer_address):
        return cls.get_session().query(cls).filter_by(address=peer_address).one()

    @classmethod
    def find_on_by_address_or_pk(cls, peer_address, public_key):
        return cls.get_session().query(cls).filter(or_(cls.address == peer_address, cls.public_key == public_key)).one()

    @classmethod
    def find_one_by_public_key(cls, pk):
        return cls.get_session().query(cls).filter_by(public_key=pk).one()

    @classmethod
    def find_or_add(cls, peer):
        instance = cls.get_session().query(cls).filter_by(public_key=peer.public_key).first()
        if instance: return instance
        return cls.add(peer)

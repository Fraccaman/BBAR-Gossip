from sqlalchemy import Column, String, Integer, ForeignKey

from src.store.Base import Base
from src.store.BaseMixin import BaseMixin


class ProofOfMisbehaviour(BaseMixin, Base):
    against_peer = Column(Integer, ForeignKey('peer.id'))
    proof = Column(String, unique=True)
    from_peer = Column(Integer, ForeignKey('peer.id'))

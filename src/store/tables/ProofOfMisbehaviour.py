from sqlalchemy import Column, Integer, ForeignKey

from src.store.Base import Base
from src.store.BaseMixin import BaseMixin


class ProofOfMisbehaviour(BaseMixin, Base):
    against_peer = Column(Integer, ForeignKey('peer.id'))
    type = Column(Integer)
    from_peer = Column(Integer, ForeignKey('peer.id'))
    epoch = Column(Integer)

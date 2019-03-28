from sqlalchemy import Column, Integer, ForeignKey

from src.store.Base import Base
from src.store.BaseMixin import BaseMixin


class View(BaseMixin, Base):
    peer = Column(Integer, ForeignKey('peer.id'))
    epoch = Column(Integer, ForeignKey('epoch.id'))

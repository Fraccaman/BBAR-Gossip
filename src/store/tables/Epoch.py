from sqlalchemy import Column, Integer, Boolean, event

from src.store.Base import Base
from src.store.BaseMixin import BaseMixin


class Epoch(BaseMixin, Base):
    epoch = Column(Integer, unique=True)
    current = Column(Boolean)
    next = Column(Boolean)

    @classmethod
    def get_current_epoch(cls):
        return cls.get_session().query(cls).filter_by(current=True).one()

    @classmethod
    def get_next_epoch(cls):
        return cls.get_session().query(cls).filter_by(next=True).one()


def insert_data(target, connection, **kw):
    connection.execute(target.insert(), {'epoch': 1, 'current': True, 'next': False},
                       {'epoch': 2, 'current': False, 'next': True})


event.listen(Epoch.__table__, 'after_create', insert_data)

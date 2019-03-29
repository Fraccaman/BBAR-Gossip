from sqlalchemy import Column, Integer, Boolean, event

from src.store.Base import Base
from src.store.BaseMixin import BaseMixin
from src.utils.Logger import Logger


# TODO: Add constrains

class Epoch(BaseMixin, Base):
    epoch = Column(Integer)
    current = Column(Boolean)
    next = Column(Boolean)

    @classmethod
    def get_current_epoch(cls):
        return cls.get_session().query(cls).filter_by(current=True).one()

    @classmethod
    def get_next_epoch(cls):
        return cls.get_session().query(cls).filter_by(next=True).one()

    @classmethod
    def update_to_current(cls, epoch):
        session = cls.get_session()
        session.query(cls).filter_by(id=epoch.id).update({'current': True, 'next': False})
        session.commit()

    @classmethod
    def update_to_old(cls, epoch):
        session = cls.get_session()
        session.query(cls).filter_by(id=epoch.id).update({'current': False, 'next': False})
        session.commit()

    @classmethod
    def set_new_epoch(cls):
        current_epoch: Epoch = cls.get_current_epoch()
        cls.update_to_old(current_epoch)
        next_epoch = cls.get_next_epoch()
        cls.update_to_current(next_epoch)
        cls.add(Epoch(epoch=next_epoch.epoch + 1, current=False, next=True))
        Logger.get_instance().debug_item(
            'Current epoch: {}, next epoch: {}.'.format(next_epoch.epoch, next_epoch.epoch + 1))
        return next_epoch.epoch


def insert_data(target, connection, **kw):
    connection.execute(target.insert(), {'epoch': 1, 'current': True, 'next': False},
                       {'epoch': 2, 'current': False, 'next': True})


event.listen(Epoch.__table__, 'after_create', insert_data)

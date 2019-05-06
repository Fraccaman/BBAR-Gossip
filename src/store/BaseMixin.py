from typing import List

from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.ext.declarative import declared_attr


class BaseMixin(object):
    created_at = Column(DateTime, default=func.now())

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower().strip()

    __table_args__ = {'mysql_engine': 'InnoDB'}
    __mapper_args__ = {'always_refresh': True}

    id = Column(Integer, primary_key=True)

    @staticmethod
    def get_session():
        from src.store.Store import Store
        return Store().get_session()

    @classmethod
    def add(cls, item):
        session = cls.get_session()
        session.add(item)
        session.commit()

    @classmethod
    def get_all_with_ids(cls, ids: List):
        cls.get_session().query(cls).filter(cls.id.in_(ids)).all()

    @classmethod
    def get_all(cls):
        return cls.get_session().query(cls).all()

    @classmethod
    def add_multiple(cls, items, preserve_order=False):
        # TODO: optimize table locking
        session = cls.get_session()
        session.bulk_save_objects(items, preserve_order=preserve_order)
        session.commit()

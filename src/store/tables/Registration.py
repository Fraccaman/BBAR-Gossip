from sqlalchemy import Column, Integer, String, ForeignKey

from src.store.BaseMixin import BaseMixin
from src.store.Base import Base


class Registration(BaseMixin, Base):

    base = Column(String, unique=True)
    epoch = Column(Integer)

    @classmethod
    def is_registration_present(cls, base):
        format_base = ''.join(base.split('-')[0]) + '%'
        return cls.get_session().query(cls).filter(cls.base.ilike(format_base)).first()

    @classmethod
    def get_one_by_base(cls, base):
        return cls.get_session().query(cls).filter_by(base=base).first()

    @staticmethod
    def get_session():
        from src.store.Store import Store
        return Store().get_session()

    @classmethod
    def add(cls, registration):
        session = cls.get_session()
        session.add(registration)
        session.commit()


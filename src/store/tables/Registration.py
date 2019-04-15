from sqlalchemy import Column, Integer, String

from src.store.Base import Base
from src.store.BaseMixin import BaseMixin
from src.utils.Constants import EPOCH_DIFF


class Registration(BaseMixin, Base):
    base = Column(String, unique=True)
    proof = Column(String)
    epoch = Column(Integer)

    @classmethod
    def is_registration_present(cls, base):
        format_base = ''.join(base.split('-')[0]) + '%'
        return cls.get_session().query(cls).filter(cls.base.ilike(format_base),
                                                   cls.epoch.between(cls.epoch, cls.epoch - EPOCH_DIFF)).first()

    @classmethod
    def get_one_by_id(cls, id):
        return cls.get_session().query(cls).filter_by(id=id).first()

    @classmethod
    def get_one_by_base(cls, base):
        return cls.get_session().query(cls).filter_by(base=base).first()

    @classmethod
    def update_registration(cls, base, proof):
        session = cls.get_session()
        session.query(cls).filter_by(base=base).update({'proof': proof})
        session.commit()

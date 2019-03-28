from sqlalchemy import Column, Integer, String

from src.store.Base import Base
from src.store.BaseMixin import BaseMixin
from src.utils.Constants import EPOCH_DIFF


class Registration(BaseMixin, Base):
    base = Column(String, unique=True)
    epoch = Column(Integer)

    @classmethod
    def is_registration_present(cls, base, epoch):
        format_base = ''.join(base.split('-')[0]) + '%'
        return cls.get_session().query(cls).filter(cls.base.ilike(format_base),
                                                   cls.epoch.between(epoch, epoch - EPOCH_DIFF)).first()

    @classmethod
    def get_one_by_base(cls, base):
        return cls.get_session().query(cls).filter_by(base=base).first()
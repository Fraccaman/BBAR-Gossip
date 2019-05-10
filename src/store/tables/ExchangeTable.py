from sqlalchemy import Column, String, Boolean

from src.store.Base import Base
from src.store.BaseMixin import BaseMixin


class Exchange(BaseMixin, Base):
    seed = Column(String, unique=True)
    sender = Column(Boolean)
    needed = Column(String)
    promised = Column(String)
    type = Column(String(3))  # BAL or OPT
    signature = Column(String)
    briefcase = Column(String)

    @classmethod
    def get_exchange(cls, seed):
        return cls.get_session().query(cls).filter_by(seed=seed).first()

    @classmethod
    def add_signature(cls, seed, signature):
        session = cls.get_session()
        session.query(cls).filter_by(seed=seed).update({"signature": signature})
        session.commit()

    @classmethod
    def add_briefcase(cls, seed, briefcase):
        session = cls.get_session()
        session.query(cls).filter_by(seed=seed).update({"briefcase": briefcase})
        session.commit()

    @classmethod
    def get_briefcase(cls, seed):
        return cls.get_session().query(cls).filter_by(seed=seed).first().briefcase


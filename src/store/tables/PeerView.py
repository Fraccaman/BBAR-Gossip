from sqlalchemy import Column, String, Integer, Boolean

from src.store.Base import Base
from src.store.BaseMixin import BaseMixin


class PeerView(BaseMixin, Base):
    index = Column(Integer)
    public_key = Column(String)
    address = Column(String)
    epoch = Column(Integer)
    is_me = Column(Boolean)

    @classmethod
    def get_partner(cls, index):
        return cls.get_session().query(cls).filter_by(index=index, is_me=False).first()

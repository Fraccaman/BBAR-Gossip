from sqlalchemy import Column, String

from src.store.Base import Base
from src.store.BaseMixin import BaseMixin


class BootstrapIdentity(BaseMixin, Base):
    address = Column(String, unique=True)
    public_key = Column(String)

    @staticmethod
    def get_session():
        from src.store.Store import Store
        return Store().get_session()

    @classmethod
    def get_one_by_address(cls, address):
        return cls.get_session().query(cls).filter_by(address=address).one()

    @classmethod
    def get_or_add(cls, bn):
        session = cls.get_session()
        item = cls.get_session().query(cls).filter_by(address=bn.address).first()
        if not item:
            session.add(bn)
            session.commit()

from sqlalchemy import Column, Integer, String, ForeignKey

from src.store.Base import Base
from src.store.BaseMixin import BaseMixin
from src.store.tables.BootstrapIdentity import BootstrapIdentity


class Token(BaseMixin, Base):
    base = Column(String)
    proof = Column(String, unique=True)
    signature = Column(String, unique=True)
    epoch = Column(Integer)
    bn_id = Column(Integer, ForeignKey('bootstrapidentity.id'))

    @classmethod
    def find_one_by_epoch_and_address(cls, epoch, address):
        return cls.get_session().query(cls).join(BootstrapIdentity).filter(BootstrapIdentity.address == address,
                                                                           cls.epoch == epoch).first()

    @classmethod
    def add(cls, token):
        session = cls.get_session()
        session.add(token)
        session.commit()

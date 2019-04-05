from sqlalchemy import Column, Integer, String, ForeignKey

from src.store.Base import Base
from src.store.BaseMixin import BaseMixin
from src.store.tables.BootstrapIdentity import BootstrapIdentity
from src.utils.Constants import EPOCH_DIFF


class Token(BaseMixin, Base):
    base = Column(String)
    proof = Column(String)
    signature = Column(String, unique=True)
    epoch = Column(Integer)
    bn_id = Column(Integer, ForeignKey('bootstrapidentity.id'))

    @classmethod
    def find_one_by_address(cls, address):
        return cls.get_session().query(cls).join(BootstrapIdentity).filter(BootstrapIdentity.address == address,
                                                                           cls.epoch.between(cls.epoch, cls.epoch + EPOCH_DIFF)).first()

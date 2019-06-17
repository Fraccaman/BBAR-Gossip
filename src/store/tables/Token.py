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
    key = Column(String)
    bn_id = Column(Integer, ForeignKey('bootstrapidentity.id'))

    @classmethod
    def find_one_by_address(cls, address, epoch):
        return cls.get_session().query(cls).join(BootstrapIdentity).filter(BootstrapIdentity.address == address,
                                                                           cls.epoch.between(epoch,
                                                                                             epoch + EPOCH_DIFF)).first()

    @classmethod
    def find_one_by_epoch(cls, epoch):
        return cls.get_session().query(cls).filter_by(epoch=epoch).first()

    @classmethod
    def find_all_tokens(cls, epoch):
        return [token.signature for token in cls.get_session().query(cls).filter_by(epoch=epoch).all()]

    @classmethod
    def add_or_update(cls, token):
        instance = cls.get_session().query(cls).filter_by(base=token.base).first()
        if instance:
            session = cls.get_session()
            session.query(cls).filter_by(base=token.base).update({'signature': token.signature, 'epoch': token.epoch})
            session.commit()
        else:
            cls.add(token)

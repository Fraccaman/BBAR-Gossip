from sqlalchemy import Column, String, Integer, Boolean, func, ForeignKey

from src.store.Base import Base
from src.store.BaseMixin import BaseMixin


class PeerView(BaseMixin, Base):
    index = Column(Integer)
    public_key = Column(String)
    address = Column(String)
    epoch = Column(Integer)
    is_me = Column(Boolean)
    bn_id = Column(Integer, ForeignKey('bootstrapidentity.id'))

    @classmethod
    def get_partner(cls, index):
        return cls.get_session().query(cls).filter_by(index=index).first()

    @classmethod
    def get_total_peers_per_epoch(cls, epoch, bn_id):
        return cls.get_session().query((func.count(cls.id))).filter(cls.epoch==epoch, cls.bn_id==bn_id).scalar()

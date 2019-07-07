from sqlalchemy import Column, Integer, ForeignKey, or_

from src.store.Base import Base
from src.store.BaseMixin import BaseMixin
from src.store.tables.Epoch import Epoch
from src.store.tables.ProofOfMisbehaviour import ProofOfMisbehaviour


class View(BaseMixin, Base):
    peer = Column(Integer, ForeignKey('peer.id'))
    epoch_id = Column(Integer, ForeignKey('epoch.id'))

    @classmethod
    def get_all_honest_peer_from_current_epoch(cls):
        subquery = ~cls.get_session().query(ProofOfMisbehaviour).filter(
            ProofOfMisbehaviour.against_peer == View.peer).exists()
        prev_epoch = Epoch.get_current_epoch().epoch - 1
        return cls.get_session().query(cls).filter(subquery).join(Epoch).filter(
            or_(Epoch.current == True, Epoch.epoch == prev_epoch)).all()

    @classmethod
    def get_current_view(cls):
        prev_epoch = Epoch.get_current_epoch().epoch - 1
        subquery = ~cls.get_session().query(ProofOfMisbehaviour).filter(
            ProofOfMisbehaviour.against_peer == View.peer, ProofOfMisbehaviour.epoch == prev_epoch).exists()
        return cls.get_session().query(cls).filter(subquery).join(Epoch).filter(
            or_(Epoch.current == True, Epoch.epoch == prev_epoch)).all()

    @classmethod
    def set_new_epoch_and_peer_list(cls):
        return Epoch.set_new_epoch()

    def __str__(self):
        return 'peer: {}, epoch: {}'.format(self.peer, self.epoch_id)

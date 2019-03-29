from sqlalchemy import Column, Integer, ForeignKey, or_

from src.store.Base import Base
from src.store.BaseMixin import BaseMixin
from src.store.tables.Epoch import Epoch
from src.store.tables.Peer import Peer
from src.store.tables.ProofOfMisbehaviour import ProofOfMisbehaviour


class View(BaseMixin, Base):
    peer = Column(Integer, ForeignKey('peer.id'))
    epoch = Column(Integer, ForeignKey('epoch.id'))

    @classmethod
    def get_all_honest_peer_from_current_epoch(cls):
        subquery = ~cls.get_session().query(ProofOfMisbehaviour).filter(
            ProofOfMisbehaviour.against_peer == View.peer).exists()
        return cls.get_session().query(cls).filter(subquery).join(Epoch).filter(or_(Epoch.current == True)).all()

    @classmethod
    def set_new_epoch_and_peer_list(cls):
        view_list = cls.get_all_honest_peer_from_current_epoch()
        epoch = Epoch.set_new_epoch()
        for view in view_list:
            View.add(View(peer=view.peer, epoch=epoch))
        peer_list = Peer.get_all([view.peer for view in view_list])
        return peer_list, epoch

    def __str__(self):
        return 'peer: {}, epoch: {}'.format(self.peer, self.epoch)

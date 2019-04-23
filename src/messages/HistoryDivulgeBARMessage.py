from src.messages import Message
from src.messages.BARMessage import BARMessage, Identity
from src.messages.ViewMessage import PeerInfo
from src.store.iblt.pyblt import PYBLT


class HistoryDivulgeBARMessage(BARMessage):

    def __init__(self, elements: PYBLT, identity: Identity, _from: PeerInfo, _to: PeerInfo, prev: Message):
        super().__init__(identity, _from, _to, prev)
        self.elements = elements

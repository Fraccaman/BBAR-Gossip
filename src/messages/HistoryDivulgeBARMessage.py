from src.messages import Message
from src.messages.BARMessage import BARMessage, Identity, PeerInfo


class HistoryDivulgeBARMessage(BARMessage):

    def __init__(self, elements: str, identity: Identity, _from: PeerInfo, _to: PeerInfo, prev: Message):
        super().__init__(identity, _from, _to, prev)
        self.elements = elements

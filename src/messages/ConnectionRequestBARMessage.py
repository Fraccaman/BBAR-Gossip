from src.messages import Message
from src.messages.BARMessage import BARMessage, Identity
from src.messages.ViewMessage import PeerInfo


class ConnectionRequestBARMessage(BARMessage):

    def __init__(self, identity: Identity, _from: PeerInfo, _to: PeerInfo, prev: Message):
        super().__init__(identity, _from, _to, prev)

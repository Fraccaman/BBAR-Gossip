from enum import Enum

from src.messages import Message
from src.messages.BARMessage import BARMessage, Identity, PeerInfo


class Misbehaviour(Enum):
    BAD_BRIEFCASE = 1
    BAD_SEED = 2
    BAD_PROMISE = 3
    BAD_PROMISE_ACCEPT = 4


class PoMBARMessage(BARMessage):

    def __init__(self, identity: Identity, _from: PeerInfo, _to: PeerInfo, prev: Message, misbehaviour: Misbehaviour):
        super().__init__(identity, _from, _to, prev)
        self.misbehaviour = misbehaviour

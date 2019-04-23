from src.cryptography.Crypto import Crypto
from src.messages.Message import Message
from src.messages.ViewMessage import PeerInfo


class Identity:

    def __init__(self, base: str, proof: str, token: str):
        self.base = base
        self.proof = proof
        self.token = token


class BARMessage(Message):

    def __init__(self, identity: Identity, _from: PeerInfo, _to: PeerInfo, prev: Message):
        self.identity = identity
        self._from = _from
        self._to = _to
        self.prev_msg_hash = self._compute_prev_hash(prev)

    @staticmethod
    def _compute_prev_hash(prev_msg: Message):
        return Crypto.get_instance().get_hasher().hash(prev_msg.serialize())

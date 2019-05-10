import copy
from typing import Union

from fastecdsa.point import Point

from src.cryptography.Crypto import Crypto
from src.messages.Message import Message


class Identity:

    def __init__(self, base: str, proof: str, token: str, epoch: str):
        self.base = base
        self.proof = proof
        self.bn_signature = token
        self.epoch = epoch

    def verify(self):
        return (self.base + self.proof + self.epoch).encode()


class PeerInfo:

    def __init__(self, address: str, public_key: Point):
        self.address = address
        self.public_key = public_key


class BARMessage(Message):

    def __init__(self, identity: Identity, _from: PeerInfo, _to: PeerInfo, prev: Union[Message, None]):
        self.token = identity
        self.from_peer = _from
        self.to_peer = _to
        self.prev_msg_hash = self._compute_prev_hash(prev)
        self.signature = None

    @staticmethod
    def _compute_prev_hash(prev_msg: Message):
        return Crypto.get_instance().get_hasher().hash(prev_msg.serialize()) if prev_msg is not None else '0' * 64

    def compute_signature(self):
        self.signature = Crypto.get_ec().sign(self.serialize())

    def verify_signature(self):
        sig = copy.deepcopy(self.signature)
        self.signature = None
        res = Crypto.get_ec().verify(sig, self.serialize(), self.from_peer.public_key)
        self.signature = sig
        return res

import copy
from typing import Union

from fastecdsa.point import Point

from src.cryptography.Crypto import Crypto
from src.messages.Message import Message
from src.utils.Logger import Logger, LogLevels


class Identity:

    def __init__(self, base: str, proof: str, token: str, epoch: str):
        self.base = base
        self.proof = proof
        self.bn_signature = token
        self.epoch = epoch


class PeerInfo:

    def __init__(self, address: str, public_key: Point):
        self.address = address
        self.public_key = public_key


class BARMessage(Message):

    def __init__(self, identity: Identity, _from: PeerInfo, _to: PeerInfo, prev: Union[Message, None]):
        super().__init__()
        self.token = identity
        self.from_peer = _from
        self.to_peer = _to
        self.prev_msg_hash = self._compute_prev_hash(prev)
        self.signature = None
        self._is_byzantine = False

    @staticmethod
    def _compute_prev_hash(prev_msg: Message):
        return Crypto.get_instance().get_hasher().hash(prev_msg.serialize()) if prev_msg is not None else '0' * 64

    def is_byzantine(self):
        return self._is_byzantine

    def set_byzantine(self, byzantine_level):
        if self.will_be_byzantine(byzantine_level):
            Logger.get_instance().debug_item('I am EVIL! Will I get banhammered?...', LogLevels.WARNING)
            self._is_byzantine = True

    def compute_signature(self):
        self.signature = Crypto.get_ec().sign(self.serialize())

    def verify_signature(self):
        sig = copy.deepcopy(self.signature)
        self.signature = None
        res = Crypto.get_ec().verify(sig, self.serialize(), self.from_peer.public_key)
        self.signature = sig
        return res

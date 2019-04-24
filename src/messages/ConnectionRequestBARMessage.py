from typing import Union

from src.cryptography.Crypto import Crypto
from src.messages.BARMessage import BARMessage, Identity, PeerInfo


class  ConnectionRequestBARMessage(BARMessage):

    def __init__(self, identity: Identity, _from: PeerInfo, _to: PeerInfo, prev: Union[BARMessage, None]):
        super().__init__(identity, _from, _to, prev)

    def verify(self, bn_public_key):
        return Crypto.get_instance().get_ec().verify(self.token.token,
                                                     (self.token.base + self.token.proof +
                                                      self.token.epoch).encode('utf-8'), bn_public_key)

from typing import Union

from src.messages.BARMessage import BARMessage, Identity, PeerInfo


class KeyBARMessage(BARMessage):

    def __init__(self, identity: Identity, _from: PeerInfo, _to: PeerInfo, prev: Union[BARMessage, None], key: str):
        super().__init__(identity, _from, _to, prev)
        self.key = key

from typing import Union

from src.messages.BARMessage import BARMessage, Identity, PeerInfo


class KeyRequestBARMessage(BARMessage):

    def __init__(self, identity: Identity, _from: PeerInfo, _to: PeerInfo, prev: Union[BARMessage, None]):
        super().__init__(identity, _from, _to, prev)

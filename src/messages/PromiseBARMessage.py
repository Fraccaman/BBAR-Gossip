from typing import Union, List

from src.messages.BARMessage import BARMessage, Identity, PeerInfo


class PromiseBARMessage(BARMessage):

    def __init__(self, identity: Identity, _from: PeerInfo, _to: PeerInfo, prev: Union[BARMessage, None],
                 needed: List[str],
                 promised: List[str], type: str):
        super().__init__(identity, _from, _to, prev)
        self.needed = needed
        self.promised = promised
        self.type = type

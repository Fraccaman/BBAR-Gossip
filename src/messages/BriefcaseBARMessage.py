from typing import Union, List

from src.messages.BARMessage import BARMessage, Identity, PeerInfo


class BriefcaseBARMessage(BARMessage):

    def __init__(self, identity: Identity, _from: PeerInfo, _to: PeerInfo, prev: Union[BARMessage, None],
                 encrypted_txs: List[str]):
        super().__init__(identity, _from, _to, prev)
        self.data = encrypted_txs

import copy
from datetime import timezone, datetime
from typing import List, Union, NoReturn

from src.cryptography.Crypto import Crypto
from src.messages.Message import Message
from src.messages.TokenMessage import TokenMessage
from src.store.tables.Peer import Peer
from src.store.tables.View import View
from src.utils.Constants import EPOCH_DURATION


class ViewMessage(Message):

    def __init__(self, peer_list: List[Peer], epoch: int):
        self.peer_list = self.sort(peer_list, epoch)
        self.epoch = epoch
        self.token: TokenMessage = None
        self.next_epoch = int(datetime.now(tz=timezone.utc).timestamp() + EPOCH_DURATION)

    @classmethod
    def get_current_view(cls) -> List[Peer]:
        view_list = View.get_all_honest_peer_from_current_epoch()
        peers_ids = [view.peer for view in view_list]
        peer_list = Peer.get_all_with_ids(peers_ids)
        return peer_list

    @staticmethod
    def sort(peer_list, epoch) -> Union[List[Peer], List[None]]:
        peer_list.sort(key=lambda x: int(x.__dict__['public_key'].split('.')[0]), reverse=True)
        n_of_peers = len(peer_list)
        random_indexes = Crypto.get_instance().get_random().prng_unique(epoch, n_of_peers, n_of_peers)
        shuffled_peer_list = [None for _ in range(n_of_peers)]
        for index, random_index in enumerate(random_indexes):
            shuffled_peer_list[random_index] = peer_list[index]
        return shuffled_peer_list

    def verify_shuffle(self, epoch: int) -> bool:
        peer_list_copy = copy.deepcopy(self.peer_list)
        peer_list_copy = self.sort(peer_list_copy, epoch)
        return peer_list_copy == self.peer_list

    def set_token(self, token_message) -> NoReturn:
        self.token = token_message

    def get_epoch(self) -> int:
        return self.epoch

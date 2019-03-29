from typing import List

from src.cryptography.Crypto import Crypto
from src.messages.Message import Message


class Peer:

    def __init__(self, address: str, public_key: str):
        self.address = address
        self.public_key = public_key


class ViewMessage(Message):

    def __init__(self, peer_list: List[Peer], epoch: int):
        self.peer_list = self.sort(peer_list, epoch)
        self.epoch = epoch

    @staticmethod
    def sort(peer_list, epoch):
        peer_list.sort(key=lambda x: x.__dict__['public_key'].split('.')[0], reverse=True)
        n_of_peers = len(peer_list)
        random_indexes = Crypto.get_instance().get_random().prng_unique(epoch, n_of_peers, n_of_peers)
        shuffled_peer_list = [None for _ in range(n_of_peers)]
        for index, random_index in enumerate(random_indexes):
            shuffled_peer_list[random_index] = peer_list[index]
        return shuffled_peer_list

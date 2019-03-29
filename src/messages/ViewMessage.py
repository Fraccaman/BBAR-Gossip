from typing import List

from src.messages.Message import Message


class Peer:

    def __init__(self, address: str, public_key: str):
        self.address = address
        self.public_key = public_key


class ViewMessage(Message):

    def __init__(self, peer_list: List[Peer], epoch: int):
        self.peer_list = peer_list
        self.epoch = epoch

from src.messages.Message import Message


class LoginMessage(Message):

    def __init__(self, base: str, proof: str, address: str):
        self.address = address
        self.base = base
        self.proof = proof

    def get_public_key(self) -> str:
        return self.base.split('-')[0]

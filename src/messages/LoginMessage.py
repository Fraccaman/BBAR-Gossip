from src.messages.Message import Message


class LoginMessage(Message):

    def __init__(self, base: str, proof: str):
        self.base = base
        self.proof = proof

    def get_public_key(self):
        return self.base.split('-')[0]

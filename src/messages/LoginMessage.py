from src.messages.Message import Message


class LoginMessage(Message):

    def __init__(self, base: str, proof: str):
        self.base = base
        self.proof = proof

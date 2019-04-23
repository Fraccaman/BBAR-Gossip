import hashlib


class Hash:
    HASH_FUNCTION = 'sha256'

    @staticmethod
    def hash(element: str) -> str:
        return hashlib.new(Hash.HASH_FUNCTION, str(element).encode()).hexdigest()

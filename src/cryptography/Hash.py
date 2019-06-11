import hashlib


class Hash:
    HASH_FUNCTION = 'sha256'
    SHORT_HASH_FUNCTION = 'ripemd160'

    @staticmethod
    def hash(element: bytes) -> str:
        return hashlib.new(Hash.HASH_FUNCTION, element).hexdigest()

    @staticmethod
    def short_hash(element: bytes) -> str:
        return hashlib.new(Hash.SHORT_HASH_FUNCTION, element).hexdigest()

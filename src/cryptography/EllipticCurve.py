from fastecdsa import keys, curve, ecdsa
from fastecdsa.encoding.der import DEREncoder
from fastecdsa.keys import export_key, import_key


class EllipticCurve:

    def __init__(self, private_key):
        self.private_key = private_key or self.generate_private_key()
        self.public_key = self.generate_public_from_private(self.private_key)

    @staticmethod
    def generate_keys():
        return keys.gen_keypair(curve.secp256k1)

    @staticmethod
    def generate_private_key():
        return keys.gen_private_key(curve.secp256k1)

    @staticmethod
    def generate_public_key(private):
        return keys.get_public_key(private, curve.secp256k1)

    @staticmethod
    def generate_public_from_private(private_key):
        return keys.get_public_key(private_key, curve.secp256k1)

    @staticmethod
    def sign(private_key, message_bytes):
        r, s = ecdsa.sign(message_bytes, private_key)
        return DEREncoder.encode_signature(r, s)

    @staticmethod
    def verify(signature, message_bytes, public_key):
        r, s = DEREncoder.decode_signature(signature)
        return ecdsa.verify((r, s), message_bytes, public_key)

    @staticmethod
    def export_keys(private_key, public_key, path):
        export_key(private_key, curve.secp256k1, path)
        export_key(public_key, curve.secp256k1, path)

    @staticmethod
    def import_keys(path):
        return import_key(path)

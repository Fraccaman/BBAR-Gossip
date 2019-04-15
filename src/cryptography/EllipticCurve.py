from fastecdsa import keys, curve, ecdsa
from fastecdsa.encoding.der import DEREncoder
from fastecdsa.keys import export_key, import_key
from fastecdsa.point import Point


class EllipticCurve:

    def __init__(self, private_key):
        self.private_key = private_key or self.generate_private_key()
        self.public_key = self.generate_public_from_private(self.private_key)

    @staticmethod
    def generate_keys():
        return keys.gen_keypair(curve.secp256k1)

    @staticmethod
    def load_public_key(x, y, c):
        if c == 'secp256k1':
            return Point(x, y, curve.secp256k1)

    @staticmethod
    def dump_public_key(public_key: Point):
        return '{}.{}.{}'.format(public_key.x, public_key.y, public_key.curve)

    @staticmethod
    def generate_private_key():
        return keys.gen_private_key(curve.secp256k1)

    @staticmethod
    def generate_public_key(private):
        return keys.get_public_key(private, curve.secp256k1)

    @staticmethod
    def public_key_to_string(public_key: Point):
        return '{}-{}-{}'.format(public_key.x, public_key.y, public_key.curve)

    @staticmethod
    def generate_public_from_private(private_key):
        return keys.get_public_key(private_key, curve.secp256k1)

    @property
    def get_public(self):
        return self.public_key

    def sign(self, message_bytes):
        r, s = ecdsa.sign(message_bytes, self.private_key, curve=self.public_key.curve)
        return DEREncoder.encode_signature(r, s).hex()

    @staticmethod
    def verify(signature, message_bytes: str, public_key: Point):
        r, s = DEREncoder.decode_signature(bytes.fromhex(signature))
        return ecdsa.verify((r, s), message_bytes, public_key, curve=public_key.curve)

    def export_keys(self, path):
        export_key(self.private_key, curve.secp256k1, path)
        export_key(self.public_key, curve.secp256k1, path)

    @staticmethod
    def import_keys(path):
        return import_key(path)

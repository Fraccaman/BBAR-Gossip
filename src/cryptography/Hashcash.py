# taken from: https://github.com/doctaphred/hashcoin

import hashlib
from collections import namedtuple
from itertools import count, combinations_with_replacement, islice


def iter_bytes():
    for num_bytes in count():
        value_combos = combinations_with_replacement(range(256), num_bytes)
        for values in value_combos:
            yield bytes(values)


def intify(b, byteorder='big'):
    return int.from_bytes(b, byteorder=byteorder)


class Hashcash(namedtuple('Hashcash', ['data', 'salt'])):
    hash = hashlib.sha256

    @classmethod
    def salts(cls):
        yield from iter_bytes()

    @classmethod
    def max_digest(cls):
        return bytes([0xff] * cls.hash().digest_size)

    @classmethod
    def percentile_digest(cls, percentile):
        max_digest_value = int.from_bytes(cls.max_digest(), 'big')
        percentile_digest_value = int(percentile * (max_digest_value + 1))
        return percentile_digest_value.to_bytes(cls.hash().digest_size, 'big')

    @classmethod
    def new(cls, percentile, data):
        return next(cls.in_percentile(percentile, data))

    @classmethod
    def in_percentile(cls, percentile, data):
        data_hash = cls.hash(data)
        max_digest = cls.percentile_digest(percentile)
        for salt in cls.salts():
            full_hash = data_hash.copy()
            full_hash.update(salt)
            if full_hash.digest() <= max_digest:
                yield cls(data, salt)

    @classmethod
    def refine(cls, data):
        data_hash = cls.hash(data)
        min_digest = cls.max_digest()
        for salt in cls.salts():
            full_hash = data_hash.copy()
            full_hash.update(salt)
            digest = full_hash.digest()
            if digest < min_digest:
                min_digest = digest
                yield cls(data, salt)

    @classmethod
    def best(cls, n, data):
        data_hash = cls.hash(data)
        min_digest = cls.max_digest()
        min_salt = b''
        for salt in islice(cls.salts(), n):
            full_hash = data_hash.copy()
            full_hash.update(salt)
            digest = full_hash.digest()
            if digest < min_digest:
                min_digest = digest
                min_salt = salt
        return cls(data, min_salt)

    def digest(self):
        h = self.hash(self.data)
        h.update(self.salt)
        return h.digest()

    def percentile(self):
        return intify(self.digest()) / (intify(self.max_digest()) + 1)

    @classmethod
    def is_valid_proof(cls, base, proof, percentile):
        data_hash = cls.hash(base)
        data_hash.update(proof)
        max_digest = cls.percentile_digest(percentile)
        if data_hash.digest() <= max_digest:
            return True
        return False


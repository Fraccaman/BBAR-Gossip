from sqlalchemy import Column, String

from src.store.Base import Base
from src.store.BaseMixin import BaseMixin


class BootstrapIdentity(BaseMixin, Base):
    address = Column(String, unique=True)
    public_key = Column(String)

    @classmethod
    def get_one_by_address(cls, address):
        return cls.get_session().query(cls).filter_by(address=address).one()

    @classmethod
    def get_one_by_token(cls, token):
        from src.store.tables.Token import Token
        return cls.get_session().query(cls).join(Token).filter(Token.signature == token).one()

    @classmethod
    def get_or_add(cls, bn):
        session = cls.get_session()
        item = cls.get_session().query(cls).filter_by(address=bn.address).first()
        if not item:
            session.add(bn)
            session.commit()

    @classmethod
    def get_all(cls):
        return cls.get_session().query(cls).all()
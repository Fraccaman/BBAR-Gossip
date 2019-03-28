from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.store.Base import Base
from src.store.tables.BootstrapIdentity import BootstrapIdentity
from src.store.tables.Registration import Registration
from src.store.tables.Token import Token
from src.utils.Singleton import Singleton


class Store(metaclass=Singleton):

    def __init__(self, name=None, tables: list = None):
        self.engine = create_engine('sqlite:///../network/{}.db'.format(name), echo=False, pool_recycle=3600)
        self.session = sessionmaker(bind=self.engine)
        # scoped_session(self.session())
        Base.metadata.bind = self.engine
        Base.metadata.create_all(self.engine, tables=tables)

    @staticmethod
    def setup_bn_store(name):
        return Store(str(name), [Registration.__table__])

    @staticmethod
    def setup_fn_store(name):
        return Store(str(name), [BootstrapIdentity.__table__, Token.__table__])

    @staticmethod
    def get_session():
        return Store.get_instance().session()

    @staticmethod
    def get_instance():
        return Store()

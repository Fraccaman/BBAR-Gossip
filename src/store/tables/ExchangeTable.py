from sqlalchemy import Column, String, Boolean

from src.store.Base import Base
from src.store.BaseMixin import BaseMixin


class Exchange(BaseMixin, Base):
    seed = Column(String, unique=True)
    sender = Column(Boolean)
    needed = Column(String)
    promised = Column(String)
    type = Column(String(3))  # BAL or OPT
    signature = Column(String)
    briefcase = Column(String)

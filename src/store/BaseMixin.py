from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.ext.declarative import declared_attr


class BaseMixin(object):
    created_at = Column(DateTime, default=func.now())

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower().strip()

    __table_args__ = {'mysql_engine': 'InnoDB'}
    __mapper_args__= {'always_refresh': True}

    id =  Column(Integer, primary_key=True)

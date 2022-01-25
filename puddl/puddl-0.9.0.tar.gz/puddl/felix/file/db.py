from pathlib import Path

from sqlalchemy import DateTime, func, Column, Integer, String, types, ForeignKey, \
    UniqueConstraint
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship

from puddl.db.alchemy import Schema
from .lib import default_device_name

schema = Schema('file')
Base = schema.declarative_base()


# maybe class LastModifiedMixin
# onupdate=func.now()

class DateMixin:
    # server_default=func.sysdate()
    # https://docs.sqlalchemy.org/en/13/core/defaults.html#server-invoked-ddl-explicit-default-expressions
    date = Column(DateTime(timezone=True), default=func.now())


class Device(Base, DateMixin):
    __tablename__ = 'device'
    id = Column(Integer, primary_key=True)
    name = Column(String(40), unique=True, default=default_device_name)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'Device(id={self.id}, name={self.name})'


# https://docs.sqlalchemy.org/en/13/core/custom_types.html
# noinspection PyAbstractClass


class PathType(types.TypeDecorator):
    impl = types.Text

    def process_bind_param(self, value, dialect):
        return str(value)

    def process_result_value(self, value, dialect):
        return Path(value)


class File(Base, DateMixin):
    __tablename__ = 'file'
    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey(Device.id))

    path = Column(PathType, nullable=False)
    filetype = Column(JSON)
    stat = Column(JSON, nullable=False)

    device = relationship(Device)
    UniqueConstraint(device_id, path)


def get_default_device(session):
    """
    Gets the local device based on hostname.
    Creates it, if it does not exist yet.
    """
    name = default_device_name()
    device = session.query(Device).filter(Device.name == name).first()
    if not device:
        device = Device(name=name)
        session.add(device)
    return device

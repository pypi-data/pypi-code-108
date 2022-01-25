from sqlalchemy import Column, Integer, Text, String, ForeignKey, UniqueConstraint, \
    BigInteger
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship

from puddl.db.alchemy import Schema

schema = Schema('codimd')

Base = schema.declarative_base()


# https://docs.sqlalchemy.org/en/13/orm/tutorial.html
class Remote(Base):
    __tablename__ = 'remotes'

    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String(20), unique=True)
    url = Column(Text, unique=True)
    email = Column(Text)
    password = Column(Text)

    def __str__(self):
        return f'Remote({self.id} {self.name} {self.url} {self.email})'


class History(Base):
    """
    As given by CODIMD_URL/history
    """
    __tablename__ = 'history'

    id = Column(Text, primary_key=True)
    tags = Column(postgresql.ARRAY(Text))
    text = Column(Text)
    time = Column(BigInteger)

    # TODO remote_id


class Note(Base):
    __tablename__ = 'notes'

    id = Column(Integer, primary_key=True)
    remote_id = Column(Integer, ForeignKey(Remote.id))
    note_id = Column(Text)
    text = Column(Text)

    remote = relationship('Remote')

    UniqueConstraint(remote_id, note_id)

from sqlalchemy import DateTime, func, Column, Integer, JSON, Text

from puddl.db.alchemy import Schema

schema = Schema('mampf')
Base = schema.declarative_base()


class Thing(Base):
    __tablename__ = 'thing'
    id = Column(Integer, primary_key=True, unique=True)
    dt = Column(DateTime(timezone=True), default=func.now())
    scope = Column(Text, nullable=False)
    x = Column(JSON, nullable=False)

    def __str__(self):
        local_dt = self.dt.astimezone()
        return f'id={self.id} dt={local_dt} scope={self.scope} x={self.x}'

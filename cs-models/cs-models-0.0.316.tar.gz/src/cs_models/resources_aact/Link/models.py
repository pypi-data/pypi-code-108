from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
)

from ...aact_database import Base


class LinkModel(Base):
    __tablename__ = 'links'
    __table_args__ = (
        {'schema': 'ctgov'},
    )

    id = Column(Integer, primary_key=True)
    nct_id = Column(
        String,
        ForeignKey('ctgov.studies.nct_id'),
        nullable=False,
    )
    url = Column(String)
    description = Column(Text)

    def __repr__(self):
        return "<Link(id='{}', nct_id='{}', " \
               "url='{}', description='{}'>"\
            .format(self.id, self.nct_id, self.url, self.description)

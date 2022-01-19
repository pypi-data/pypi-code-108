from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
)

from ...aact_database import Base


class KeywordModel(Base):
    __tablename__ = 'keywords'
    __table_args__ = (
        {'schema': 'ctgov'},
    )
    id = Column(Integer, primary_key=True)
    nct_id = Column(
        String,
        ForeignKey('ctgov.studies.nct_id'),
        nullable=False,
    )
    name = Column(String)
    downcase_name = Column(String)

    def __repr__(self):
        return "<Keyword(id='{}', nct_id='{}', " \
               "name='{}', downcase_name='{}'>"\
            .format(self.id, self.nct_id, self.name, self.downcase_name)

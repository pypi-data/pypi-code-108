from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Text,
)

from ...aact_database import Base


class DesignGroupModel(Base):
    __tablename__ = 'design_groups'
    __table_args__ = (
        {'schema': 'ctgov'},
    )

    id = Column(Integer, primary_key=True)
    nct_id = Column(
        String,
        ForeignKey('ctgov.studies.nct_id'),
        nullable=False,
    )
    group_type = Column(String)
    title = Column(String)
    description = Column(Text)

    def __repr__(self):
        return "<DesignGroup(id='{}', nct_id='{}', " \
               "group_type='{}', title='{}', description='{}'>"\
            .format(self.id, self.nct_id, self.group_type, self.title, self.description)

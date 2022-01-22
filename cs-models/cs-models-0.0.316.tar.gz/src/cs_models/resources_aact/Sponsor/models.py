from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
)

from ...aact_database import Base


class SponsorModel(Base):
    __tablename__ = 'sponsors'
    __table_args__ = (
        {'schema': 'ctgov'},
    )

    id = Column(Integer, primary_key=True)
    nct_id = Column(
        String,
        ForeignKey('ctgov.studies.nct_id'),
        nullable=False,
    )
    agency_class = Column(String)
    lead_or_collaborator = Column(String)
    name = Column(String)

    def __repr__(self):
        return "<Sponsor(id='{}', nct_id='{}', name='{}', agency_class={}, " \
               "lead_or_collaborator={})>".format(self.id, self.nct_id,
                                                  self.name,
                                                  self.agency_class,
                                                  self.lead_or_collaborator)

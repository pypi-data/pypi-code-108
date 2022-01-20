from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
)

from ...aact_database import Base


class BrowseInterventionModel(Base):
    __tablename__ = 'browse_interventions'
    __table_args__ = (
        {'schema': 'ctgov'},
    )

    id = Column(Integer, primary_key=True)
    nct_id = Column(
        String,
        ForeignKey('ctgov.studies.nct_id'),
        nullable=False,
    )
    mesh_term = Column(String)
    downcase_mesh_term = Column(String)

    def __repr__(self):
        return "<BrowseIntervention(id='{}', nct_id='{}', " \
               "downcase_mesh_term='{}'>"\
            .format(self.id, self.nct_id, self.downcase_mesh_term)

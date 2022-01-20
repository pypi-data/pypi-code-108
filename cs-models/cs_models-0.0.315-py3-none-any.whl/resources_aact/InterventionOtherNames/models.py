from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
)

from ...aact_database import Base


class InterventionOtherModel(Base):
    __tablename__ = 'intervention_other_names'
    __table_args__ = (
        {'schema': 'ctgov'},
    )
    id = Column(Integer, primary_key=True)
    nct_id = Column(
        String,
        ForeignKey('ctgov.studies.nct_id'),
        nullable=False,
    )
    intervention_id = Column(
        Integer,
        ForeignKey('ctgov.interventions.id'),
        nullable=False,
    )
    name = Column(String)

    def __repr__(self):
        return "<Intervention(id='{}', nct_id='{}', " \
               "intervention_id='{}', name='{}'>"\
            .format(self.id, self.nct_id, self.intervention_id, self.name)

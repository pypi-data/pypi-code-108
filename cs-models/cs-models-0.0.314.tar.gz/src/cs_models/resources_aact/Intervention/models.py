from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
)

from ...aact_database import Base


class InterventionModel(Base):
    __tablename__ = 'interventions'
    __table_args__ = (
        {'schema': 'ctgov'},
    )

    id = Column(Integer, primary_key=True)
    nct_id = Column(
        String,
        ForeignKey('ctgov.studies.nct_id'),
        nullable=False,
    )
    intervention_type = Column(String)
    name = Column(String)
    description = Column(Text)

    def __repr__(self):
        return "<Intervention(id='{}', nct_id='{}', " \
               "intervention_type='{}', name='{}'>"\
            .format(self.id, self.nct_id, self.intervention_type, self.name)

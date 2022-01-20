from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
)

from ...aact_database import Base


class DesignGroupInterventionModel(Base):
    __tablename__ = 'design_group_interventions'
    __table_args__ = (
        {'schema': 'ctgov'},
    )

    id = Column(Integer, primary_key=True)
    nct_id = Column(
        String,
        ForeignKey('ctgov.studies.nct_id'),
        nullable=False,
    )
    design_group_id = Column(
        Integer,
        ForeignKey('ctgov.design_groups.id'),
        nullable=False,
    )
    intervention_id = Column(
        Integer,
        ForeignKey('ctgov.interventions.id'),
        nullable=False,
    )

    def __repr__(self):
        return "<DesignGroupIntervention(id='{}', nct_id='{}', " \
               "design_group_id='{}', intervention_id='{}'>"\
            .format(self.id, self.nct_id, self.design_group_id, self.intervention_id)

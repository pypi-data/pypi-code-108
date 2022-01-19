from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
)

from ...aact_database import Base


class StudyReferenceModel(Base):
    __tablename__ = 'study_references'
    __table_args__ = (
        {'schema': 'ctgov'},
    )

    id = Column(Integer, primary_key=True)
    nct_id = Column(
        String,
        ForeignKey('ctgov.studies.nct_id'),
        nullable=False,
    )
    pmid = Column(String)
    reference_type = Column(String)
    citation = Column(Text)

    def __repr__(self):
        return "<StudyReference(id='{}', pmid='{}', reference_type='{}', " \
               "citation='{}'>"\
            .format(self.id, self.pmid, self.reference_type, self.citation)

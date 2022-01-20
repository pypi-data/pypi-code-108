from sqlalchemy import (
    Column,
    Integer,
    String,
)

from ...aact_database import Base


class MeshHeadingModel(Base):
    __tablename__ = 'mesh_headings'
    __table_args__ = (
        {'schema': 'ctgov'},
    )

    id = Column(Integer, primary_key=True)
    qualifier = Column(String)
    heading = Column(String)
    subcategory = Column(String)

    def __repr__(self):
        return "<MeshHeading(id='{}', qualifier='{}', " \
               "heading='{}', subcategory='{}'>"\
            .format(self.id, self.qualifier, self.heading,
                    self.subcategory)

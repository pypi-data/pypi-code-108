from sqlalchemy import (
    Column,
    Integer,
    String,
)

from ...aact_database import Base


class MeshTermModel(Base):
    __tablename__ = 'mesh_terms'
    __table_args__ = (
        {'schema': 'ctgov'},
    )

    id = Column(Integer, primary_key=True)
    qualifier = Column(String)
    tree_number = Column(String)
    description = Column(String)
    mesh_term = Column(String)
    downcase_mesh_term = Column(String)

    def __repr__(self):
        return "<MeshTerm(id='{}', qualifier='{}', " \
               "tree_number='{}', description='{}', mesh_term='{}'>"\
            .format(
                self.id,
                self.qualifier,
                self.tree_number,
                self.description,
                self.mesh_term,
            )

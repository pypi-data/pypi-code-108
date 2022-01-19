from sqlalchemy.orm import reconstructor
from propzen.common.domain.entity import Entity

@reconstructor
def sqlalchemy_entity_constructor(self):
    self.events = []

Entity.orm_constructor = sqlalchemy_entity_constructor

import ckan.model as model
import ckan.logic as logic
from ckan.model import core
from ckan.model.types import make_uuid
from sqlalchemy import Column, Text, or_, and_

from .base import Base


class Relationship(Base):
    __tablename__ = 'relationship_relationship'
    id: str = Column(Text, primary_key=True, default=make_uuid)
    subject_id: str = Column(Text, nullable=False)
    object_id: str = Column(Text, nullable=False)
    relation_type: str = Column(Text, nullable=False)

    reverse_reletion_type = {'related_to': 'related_to',
                             'child_of': 'parent_of',
                             'parent_of': 'child_of'
                             }

    def __repr__(self):
        return (
            'Relationship('
            f'id={self.id!r},'
            f'subject_id={self.subject_id!r},'
            f'object_id={self.object_id!r},'
            f'relation_type={self.relation_type!r},'
            ')'
        )

    def as_dict(self):
        id = self.id
        subject_id = self.subject_id
        object_id = self.object_id
        relation_type = self.relation_type
        return ({'id': id,
                 'subject_id': subject_id,
                 'object_id': object_id,
                 'relation_type': relation_type
                 })

    @classmethod
    def by_object_id(cls, subject_id, object_id, relation_type):
        return model.Session.query(cls). \
            filter(cls.subject_id == subject_id). \
            filter(cls.object_id == object_id). \
            filter(cls.relation_type == relation_type).one_or_none()

    @classmethod
    def by_object_type(cls, subject_id, object_entity, object_type, relation_type):
        object_class = logic.model_name_to_class(model, object_entity)

        return model.Session.query(cls). \
            filter(cls.subject_id == subject_id). \
            filter(object_class.id == cls.object_id). \
            filter(object_class.type == object_type). \
            filter(cls.relation_type == relation_type).all()

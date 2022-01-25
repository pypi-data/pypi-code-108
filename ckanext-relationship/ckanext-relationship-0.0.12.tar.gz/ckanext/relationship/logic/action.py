import ckan.logic as logic
import ckan.plugins.toolkit as tk
import ckanext.relationship.logic.schema as schema
from ckan.logic import validate
from ckanext.relationship.model.relationship import Relationship

NotFound = logic.NotFound

_actions = {}


def action(func):
    func.__name__ = f'relationship_{func.__name__}'
    _actions[func.__name__] = func
    return func


def get_actions():
    return _actions.copy()


@action
@validate(schema.relation_create)
def relation_create(context, data_dict):
    tk.check_access('relationship_relation_create', context, data_dict)

    model = context['model']

    subject_id = data_dict['subject_id']
    object_id = data_dict['object_id']
    relation_type = data_dict.get('relation_type')

    relation = Relationship(subject_id=subject_id,
                            object_id=object_id,
                            relation_type=relation_type
                            )

    reverse_relation = Relationship(subject_id=object_id,
                                    object_id=subject_id,
                                    relation_type=Relationship.reverse_reletion_type[relation_type]
                                    )

    context['session'].add(relation)
    context['session'].add(reverse_relation)
    context['session'].commit()

    return [rel.as_dict() for rel in (relation, reverse_relation)]


@action
@validate(schema.relations_list)
def relations_list(context, data_dict):
    tk.check_access('relationship_relations_list', context, data_dict)

    subject_id = data_dict['subject_id']
    object_entity = data_dict['object_entity']
    object_entity = object_entity if object_entity != 'organization' else 'group'
    object_type = data_dict['object_type']
    relation_type = data_dict.get('relation_type')

    relations = Relationship.by_object_type(subject_id,
                                            object_entity,
                                            object_type,
                                            relation_type
                                            )
    if not relations:
        return []

    return [rel.as_dict() for rel in relations]


@action
@validate(schema.relation_delete)
def relation_delete(context, data_dict):
    tk.check_access('relationship_relation_delete', context, data_dict)

    subject_id = data_dict['subject_id']
    object_id = data_dict['object_id']
    relation_type = data_dict.get('relation_type')

    relation = (context['session'].query(Relationship)
                .filter(Relationship.subject_id == data_dict['subject_id'],
                        Relationship.object_id == data_dict['object_id'],
                        Relationship.relation_type == data_dict.get('relation_type'))
                .one_or_none()
                )

    if not relation:
        raise tk.ObjectNotFound('Relation not found')

    reverse_relation = (context['session'].query(Relationship)
                        .filter(Relationship.subject_id == data_dict['object_id'],
                                Relationship.object_id == data_dict['subject_id'],
                                Relationship.relation_type == Relationship.reverse_reletion_type[
                                    data_dict.get('relation_type')])
                        .one_or_none()
                        )

    context['session'].delete(relation)
    context['session'].delete(reverse_relation)
    context['session'].commit()

    return [rel.as_dict() for rel in (relation, reverse_relation)]


@action
@validate(schema.get_entity_list)
def get_entity_list(context, data_dict):
    tk.check_access('relationship_get_entity_list', context, data_dict)

    model = context['model']

    entity = data_dict['entity']
    entity = entity if entity != 'organization' else 'group'

    entity_type = data_dict['entity_type']

    entity_class = logic.model_name_to_class(model, entity)

    entity_list = (context['session'].query(entity_class.id, entity_class.name, entity_class.title)
                   .filter(entity_class.state != 'deleted')
                   .filter(entity_class.type == entity_type).all())

    return entity_list

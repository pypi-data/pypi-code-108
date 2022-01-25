from ckan.logic.schema import validator_args
import ckan.plugins.toolkit as tk


@validator_args
def relation_create(not_empty, one_of, ignore_missing):
    return {
        'subject_id': [
            not_empty,
        ],
        'object_id': [
            not_empty,
        ],
        'relation_type': [
            one_of(['related_to', 'child_of', 'parent_of']),
        ],
    }


@validator_args
def relations_list(not_empty, one_of, ignore_missing):
    return {
        'subject_id': [
            not_empty,
        ],
        'object_entity': [
            not_empty,
            one_of(['package', 'organization', 'group']),
        ],
        'object_type': [
            not_empty,
        ],
        'relation_type': [
            not_empty,
            one_of(['related_to', 'child_of', 'parent_of']),
        ],
    }


@validator_args
def relation_delete(not_empty, one_of, ignore_missing):
    return {
        'subject_id': [
            not_empty,
        ],
        'object_id': [
            not_empty,
        ],
        'relation_type': [
            one_of(['related_to', 'child_of', 'parent_of']),
        ],
    }


@validator_args
def get_entity_list(not_empty, one_of, ignore_missing):
    return {
        'entity': [
            not_empty,
            one_of(['package', 'organization', 'group']),
        ],
        'entity_type': [
            not_empty,
        ],
    }

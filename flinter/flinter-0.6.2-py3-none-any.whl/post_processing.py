
from flinter.nesting_utils import aggregate_rules


def compute_rate(size, struct_nb, regexp_nb):
    if size == 0:
        rate = 0
    else:
        rate = (float(struct_nb * 5 + regexp_nb) / size) * 10
        rate = 10.0 - rate
    return rate


def count_errors(db, rate_fnc=compute_rate):
    if type(db) is dict:
        return _count_errors_dict(db, rate_fnc)

    # in case it is an iterable
    new_dict = {'path': 'project', 'size': 1, 'type': 'folder',
                'struct_rules': {}, 'regexp_rules': {},
                'children': db}
    return _count_errors_dict(new_dict, rate_fnc)['children']


def order_by_key(unnested_count, key='rate'):
    """Orders list of dicts by key.

    Args:
        unnested_count (list): List of dicts that constain `rate`.
    """
    return sorted(unnested_count, key=lambda x: x[key])


def _count_errors_dict(nested_db, rate_fnc):

    new_dict = {'type': nested_db['type'],
                'path': nested_db['path'],
                'size': nested_db['size'],  # relevant for rate
                'struct_nberr': 0, 'regexp_nberr': 0,  # here for ordering
                }

    new_dict['struct_rules'], n_struct_errors = _process_struct_errors(
        nested_db['struct_rules'])
    new_dict['regexp_rules'], n_regexp_errors = _process_regexp_errors(
        nested_db['regexp_rules'])

    new_dict['children'] = children = []
    for child in nested_db['children']:
        child_errors = _count_errors_dict(child, rate_fnc)
        children.append(child_errors)

        n_struct_errors += child_errors['struct_nberr']
        n_regexp_errors += child_errors['regexp_nberr']

    new_dict['struct_nberr'] = n_struct_errors
    new_dict['regexp_nberr'] = n_regexp_errors

    if callable(rate_fnc):
        new_dict['rate'] = rate_fnc(nested_db['size'], n_struct_errors,
                                    n_regexp_errors)

    return new_dict


def get_rates(count_nested_dict):
    new_dict = {'path': count_nested_dict['path'],
                'rate': compute_rate(count_nested_dict['size'],
                                     count_nested_dict['struct_nberr'],
                                     count_nested_dict['regexp_nberr'])}

    new_dict['children'] = [get_rates(child) for child in count_nested_dict['children']]

    return new_dict


def get_project_rate(nested_db):
    count_dict = count_errors(nested_db)
    rates = get_rates(count_dict)

    return rates['rate']


def get_most_common_errors(nested_db):
    aggr_db = aggregate_rules(nested_db)
    count_dict = count_errors(aggr_db)

    regexp_errors = [(key, value) for key, value in count_dict['regexp_rules'].items()]
    struct_errors = [(key, value) for key, value in count_dict['struct_rules'].items()]

    # order by worst
    regexp_errors.sort(key=lambda x: x[1], reverse=True)
    struct_errors.sort(key=lambda x: x[1], reverse=True)

    return regexp_errors, struct_errors


def _process_regexp_errors(errors):
    count_dict = dict()
    total = 0
    for key, value in errors.items():
        n_errors = len(value)
        total += n_errors
        count_dict[key] = n_errors

    return count_dict, total


def _process_struct_errors(errors):
    count_dict = dict()
    total = 0
    for key, value in errors.items():
        process_fnc = MAP_KEY_TO_PROCESS_FNC.get(key)
        if type(value) is dict:
            n_errors = process_fnc(value)
        else:  # to work with aggregates
            n_errors = sum([process_fnc(value_) for value_ in value])
        total += n_errors
        count_dict[key] = n_errors

    return count_dict, total


def _process_too_many_lines(value):
    return _process_exceeding(value['num_lines'], value['max_allowed'])


def _process_too_many_locals(value):
    return _process_exceeding(value['num_locals'], value['max_allowed'])


def _process_vars_size(value):
    return len(value['names'])


def _process_too_many_levels(value):
    return _process_exceeding(value['depth'], value['max_allowed'])


def _process_too_many_args(value):
    return _process_exceeding(value['num_args'], value['max_allowed'])


def _process_exceeding(value, max_allowed):
    return value // max_allowed


MAP_KEY_TO_PROCESS_FNC = {
    'too-many-lines': _process_too_many_lines,
    'too-many-locals': _process_too_many_locals,
    'short-varnames': _process_vars_size,
    'long-varnames': _process_vars_size,
    'too-many-levels': _process_too_many_levels,
    'too-many-arguments': _process_too_many_args,
    'short-argnames': _process_vars_size,
    'long-argnames': _process_vars_size
}

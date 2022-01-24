
import os


def unnest_to_file_level(nested_dict, fully=True):
    """Unnest database to file level.

    `fully` allows to specify if nesting is completely removed (rules are
    aggregated in parents).
    """

    def _unnest_rec(nested_dict):
        if nested_dict['type'] == 'file':
            if fully:
                nested_dict = aggregate_rules(nested_dict)

            new_list.append(nested_dict)
            return

        for child in nested_dict['children']:
            _unnest_rec(child)

    new_list = list()
    _unnest_rec(nested_dict)

    return new_list


def aggregate_rules(nested_dict, append_file_path=False):
    """Aggregates children rules until root.

    Notes:
        `append_file_path` allows to keep a meaningful database when the
        aggregation is performed on folders.
    """

    # copy dict
    new_dict = {key: value for key, value in nested_dict.items()
                if key not in {'children', 'regexp_rules', 'struct_rules'}}

    # transform regexp rules
    regexp_rules = {}
    for key, value in nested_dict['regexp_rules'].items():
        regexp_rules[key] = value.copy()

    # transform struct rules
    struct_rules = {}
    for key, value in nested_dict['struct_rules'].items():
        new_value = value.copy()
        new_value['path'] = new_dict['path']
        struct_rules[key] = [new_value]

    for child in nested_dict['children']:
        child_new_dict = aggregate_rules(child)

        # update regex rules
        for key, child_value in child_new_dict['regexp_rules'].items():
            rules_ls = regexp_rules.get(key, [])
            rules_ls.extend(child_value)

            if key not in regexp_rules:
                regexp_rules[key] = rules_ls

        # update struct rules
        for key, child_value in child_new_dict['struct_rules'].items():
            rules_ls = struct_rules.get(key, [])

            if type(rules_ls) is dict:
                value['path'] = child['path']
                rules_ls = [value]

            # by design type of children is list
            rules_ls.extend(child_value)

            if key not in struct_rules:
                struct_rules[key] = rules_ls

    if append_file_path and new_dict['type'] == 'file':
        for key, values_ls in regexp_rules.items():

            regexp_rules[key] = [dict(dict_, path=new_dict['path'])
                                 for dict_ in values_ls]

    new_dict['regexp_rules'] = regexp_rules
    new_dict['struct_rules'] = struct_rules
    new_dict['children'] = []  # to keep working structure

    return new_dict


def get_subtree(nested_dict, path):
    """Prunes tree based on path value.
    """
    subtree_path = nested_dict['path']
    if subtree_path == path:
        return nested_dict

    if len(path.split('/')) > len(subtree_path.split('/')):
        for child in nested_dict['children']:
            output = get_subtree(child, path)
            if output:
                return output

    return False


def remove_keys_from_nested(nested_dict, key_names):
    for key in key_names:
        try:
            del nested_dict[key]
        except KeyError:
            pass

    for child in nested_dict['children']:
        remove_keys_from_nested(child, key_names=key_names)


def _get_clean_path(path):
    return '/'.join(path.split(os.path.sep)[:-1])


def _complete_clean_paths(clean_paths):
    # ensure all paths exist, even when without files
    new_clean_paths = clean_paths.copy()

    i = -1
    while True:
        i += 1
        if i >= len(new_clean_paths):
            break

        key = new_clean_paths[i]
        parent = '/'.join(key.split('/')[:-1])
        if not parent:
            continue

        if parent not in new_clean_paths:
            new_clean_paths.append(parent)

    return new_clean_paths


def _get_default_dict(path):
    default_dict = {'type': 'folder',
                    'name': path,
                    'path': path,
                    'size': 0,
                    'struct_rules': {},
                    'regexp_rules': {},
                    'children': []}

    return default_dict


def _nest_data_recursive(level, ordered_keys, unnested_data):
    keys = []
    while len(ordered_keys) > 0:
        key = ordered_keys[0]
        if key.count('/') == level:
            keys.append(ordered_keys.pop(0))
        else:
            break

    children = []
    for parent_key in keys:
        data = unnested_data.get(parent_key, _get_default_dict(parent_key))

        children_keys = [key for key in ordered_keys if key.startswith(parent_key)]

        if len(children_keys) > 0:
            data['children'].extend(_nest_data_recursive(
                level + 1, children_keys, unnested_data))

        children.append(data)

    return children


def nest_data(raw_data_ls):
    # TODO: think about alphabetical ordering

    # collect paths
    paths = [data['path'] for data in raw_data_ls]
    clean_paths = _complete_clean_paths(
        list(set(_get_clean_path(path) for path in paths)))

    # create nest struct for each directory
    unnested_raw_data = {path: _get_default_dict(path) for path in clean_paths}
    for data in raw_data_ls:
        clean_path = _get_clean_path(data['path'])
        unnested_raw_data[clean_path]['children'].append(data)

    # order directory keys
    ordered_keys = sorted(clean_paths, key=lambda x: x.count('/'))

    # nest data
    nested_raw_data = unnested_raw_data[ordered_keys[0]]

    nested_raw_data['children'].extend(_nest_data_recursive(
        1, ordered_keys[1:], unnested_raw_data))

    _update_sizes(nested_raw_data)

    return nested_raw_data


def flatten(nested_db, not_append_types=('folder',)):

    def _flatten_rec(nested_dict):
        if nested_dict['type'] not in not_append_types:
            new_dict = {key: value for key, value in nested_dict.items() if key != 'children'}
            new_dict['children'] = []
            flat_db.append(new_dict)

        for child in nested_dict['children']:
            _flatten_rec(child)

    flat_db = list()
    if type(nested_db) is dict:
        _flatten_rec(nested_db)
    else:
        for nested_dict in nested_db:
            _flatten_rec(nested_dict)

    return flat_db


def _update_sizes(nested_db):
    # acts on input dict
    if nested_db['type'] == 'file':
        return nested_db['size']

    size = 0
    for child in nested_db['children']:
        size += _update_sizes(child)

    nested_db['size'] = size

    return size

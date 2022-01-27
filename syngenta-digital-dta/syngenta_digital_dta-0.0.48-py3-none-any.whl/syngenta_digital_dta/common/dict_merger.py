import copy

import simplejson as json


def merge(original_data, new_data, **kwargs):
    updated_data = copy.deepcopy(original_data)
    _walk_dict(updated_data, new_data, **kwargs)
    return updated_data


def _walk_dict(old_data, new_data, **kwargs):
    for new_key in new_data.keys():
        if old_data.get(new_key) and isinstance(new_data[new_key], dict):
            _walk_dict(old_data[new_key], new_data[new_key], **kwargs)
        elif isinstance(old_data.get(new_key), list) and isinstance(new_data[new_key], list):
            old_data[new_key] = _merge_lists(old_data[new_key], new_data[new_key],
                                             kwargs.get('update_list_operation', 'add'))
        else:
            _merge_dicts(new_key, old_data, new_data, kwargs.get('update_dict_operation', 'upsert'))


def _merge_dicts(dict_key, old_dict, new_dict, update_dict_operation='upsert'):
    if update_dict_operation == 'remove':
        old_dict.pop(dict_key, None)
    else:
        old_dict[dict_key] = new_dict[dict_key]


def _merge_lists(old_list, new_list, update_list_operation='add'):
    if update_list_operation == 'remove':
        _remove_item_in_list(old_list, new_list)
    elif update_list_operation == 'add':
        _add_unique_item_in_list(old_list, new_list)
    elif update_list_operation == 'replace':
        old_list = new_list
    return old_list


def _remove_item_in_list(old_list, new_list):
    for old_item in old_list:
        old = sorted(old_item.items()) if isinstance(old_item, dict) else old_item
        new = sorted(new_list[0].items()) if isinstance(new_list[0], dict) else new_list[0]
        if json.dumps(old) == json.dumps(new):
            old_list.remove(old_item)


def _add_unique_item_in_list(old_list, new_list):
    for item in new_list:
        if item not in old_list:
            old_list.append(item)

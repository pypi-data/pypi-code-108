from collections import defaultdict


def get_objs_diff(old_obj, new_obj, path: str = '', result: dict = None) -> dict:
    """ Возвращает отличия двух объектов """
    def _full_path(part2: str):
        return f'{path}.{part2}' if path else part2

    if type(old_obj) != type(new_obj):
        raise Exception(f'Object {str(old_obj)} and object {str(new_obj)} are of different types')

    if result is None:
        result = defaultdict(dict)

    if old_obj == new_obj:
        return result

    if isinstance(old_obj, dict):
        result['inserted'].update({_full_path(k): new_obj[k] for k in new_obj.keys() - old_obj.keys()})
        deleted_keys = old_obj.keys() - new_obj.keys()
        result['deleted'].update({_full_path(k): old_obj[k] for k in deleted_keys})
        for k in old_obj.keys() - deleted_keys:
            if old_obj[k] != new_obj[k]:
                result = get_objs_diff(old_obj[k], new_obj[k], k if not path else _full_path(k), result)
        return result

    elif isinstance(old_obj, list):
        old_dict = {x.get('name') or x.get('id') if isinstance(x, dict) else x: (i, x) for i, x in enumerate(old_obj)}
        new_dict = {x.get('name') or x.get('id') if isinstance(x, dict) else x: (i, x) for i, x in enumerate(new_obj)}
        inserted_keys = new_dict.keys() - old_dict.keys()
        deleted_keys = old_dict.keys() - new_dict.keys()
        result['inserted'].update({f'{path}[{new_dict[k][0]}]': new_dict[k][1] for k in inserted_keys})
        result['deleted'].update({f'{path}[{old_dict[k][0]}]': old_dict[k][1] for k in deleted_keys})
        for k in old_dict.keys() - deleted_keys:
            if old_dict[k][1] != new_dict[k][1]:
                result = get_objs_diff(old_dict[k][1], new_dict[k][1], f'{path}[{old_dict[k][0]}]', result)
        return result

    result['updated'].update({path: {'old': old_obj, 'new': new_obj}})
    return result

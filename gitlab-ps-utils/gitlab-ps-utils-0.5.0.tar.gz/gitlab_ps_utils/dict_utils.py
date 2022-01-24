import hashlib
from json import dumps as json_dumps
from gitlab_ps_utils.xml_utils import safe_xml_parse

def rewrite_list_into_dict(l, comparison_key, prefix="", lowercase=False):
    """
    Rewrites list of dictionaries into a dictionary for easier nested dict lookup

        :param: l: (list) list to convert to a dictionary
        :param: comparison_key: (str) key to use for lookup. Needs to be a unique value within the nested dictionaries like an ID
        :param: prefix: (str) optional string to use as a prefix for the key lookup
        :param: lowercase: (bool) will convert all comparison keys to lowercase to avoid any issues with case sensitive key lookups
        :return: (dict) rewritten dictionary
    """
    rewritten_obj = {}
    for i, _ in enumerate(l):
        new_obj = l[i]
        key = l[i][comparison_key]
        if prefix:
            key = prefix + str(key)
        if lowercase:
            rewritten_obj[str(key).lower()] = new_obj
        else:
            rewritten_obj[key] = new_obj

    return rewritten_obj


def rewrite_json_list_into_dict(l):
    """
        Converts a JSON list:
        [
            {
                "hello": {
                    "world": "how are you"
                }
            },
            {
                "world": {
                    "how": "are you"
                }
            }
        ]

        to:
        {
            "hello": {
                "world": "how are you"
            },
            "world": {
                "how": "are you"
            }
        }

        Note: The top level keys in the nested objects must be unique or else data will be overwritten
    """
    new_dict = {}
    for i, _ in enumerate(l):
        key = list(l[i].keys())[0]
        new_dict[key] = l[i][key]
    return new_dict

def sanitize_booleans_in_dict(d):
    """
        Helper method to convert string representations of boolean values to boolean type
    """
    for k, v in d.items():
        if isinstance(v, dict):
            sanitize_booleans_in_dict(v)
        if isinstance(v, str):
            if v.lower() == 'false':
                d[k] = False
            elif v.lower() == 'true':
                d[k] = True
    return d

def find(key, dictionary):
    """
        Nested dictionary lookup from https://gist.github.com/douglasmiranda/5127251
    """
    if isinstance(dictionary, dict):
        for k, v in dictionary.items():
            if k == key:
                yield v
            elif isinstance(v, dict):
                for result in find(key, v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in find(key, d):
                        yield result


def dig(dictionary, *args, default=None):
    """
        Recursive dictionary key lookup function

        Example:
            dig({"nest": {"hello": {"world": "this is nested"}}}, "nest", "hello")
            >>>> {'world': 'this is nested'}

        :param dictionary: (dict) dictionary to traverse
        :param *args: (tuple) series of keys to dig through
        :return: If the most nested key is found, the value of the key

    """
    if not args:
        return dictionary
    if isinstance(dictionary, dict):
        for i, arg in enumerate(args):
            found = dictionary.get(arg, None)
            if found is not None:
                if isinstance(found, dict):
                    args = args[i + 1:]
                    return dig(found, *args, default=default)
                return found
            return default
    return default


def list_to_dict(lst):
    """
    Convert list to dictionary for unique key comparison
    Example input:
        [1, 2, 3, 4, 5]
    Example output:
        {
            1: True,
            2: True,
            3: True,
            4: True,
            5L True
        }

        :param lst: list to convert
        :return: dictionary converted from list
    """
    res_dct = {lst[i]: True for i in range(0, len(lst), 2)}
    return res_dct


def get_hash_of_dict(d):
    SHAhash = hashlib.sha1()
    SHAhash.update(bytes(json_dumps(d), encoding="UTF-8"))
    return SHAhash.hexdigest()


def are_keys_in_dict(list_of_keys, dictionary):
    keys_in_dict = False
    for k in list_of_keys:
        if k in dictionary.keys():
            keys_in_dict = True
    return keys_in_dict


def is_nested_dict(d):
    if isinstance(d, dict):
        return any(isinstance(i, dict) for i in d.values())
    return False


def pop_multiple_keys(src, keys):
    for k in keys:
        src.pop(k, None)
    return src


def sort_dict(d):
    """
        Sorts dictionary by key name in descending order
    """
    return {k: d[k] for k in sorted(d.keys())}


def xml_to_dict(data):
    return sanitize_booleans_in_dict(safe_xml_parse(data))

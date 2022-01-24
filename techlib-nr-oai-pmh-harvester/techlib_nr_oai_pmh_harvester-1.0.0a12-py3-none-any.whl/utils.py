import pycountry
from dojson.utils import GroupableOrderedDict


def transform_to_dict(source):
    if isinstance(source, (dict, GroupableOrderedDict)):
        target = {}
        for k, v in source.items():
            if k.startswith("__"):
                continue
            target[k] = transform_to_dict(v)
    elif isinstance(source, (list, tuple)):
        target = []
        for _ in source:
            target.append(transform_to_dict(_))
    else:
        target = source
    return target


def get_alpha2_lang(lang):
    py_lang = pycountry.languages.get(alpha_3=lang) or pycountry.languages.get(
        bibliographic=lang)
    if not py_lang:
        return "ukn"
    return py_lang.alpha_2
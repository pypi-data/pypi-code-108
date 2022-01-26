def check_path(file_path):
    import pathlib
    pathlib.Path(file_path).mkdir(parents=True, exist_ok=True)


def get_ip():
    from requests import get
    ip = get('https://api.ipify.org').text
    ipv6 = get('https://api6.ipify.org').text
    return ip, ipv6


class DictToProps(object):
    def __init__(self, d):
        if type(d) is list():
            print('Essa é uma lista')
        for a, b in d.items():
            if isinstance(b, (list, tuple)):
                setattr(self, a, [DictToProps(x) if isinstance(
                    x, dict) else x for x in b])
            else:
                setattr(self, a, DictToProps(b) if isinstance(b, dict) else b)


class ListToProps(object):
    def __init__(self, obj):
        self.obj = obj

    def __getitem__(self, key):
        return dict_to_prop(self.obj[key])

    # you probably also want to proxy important list properties along like
    # __iter__ and __len__


def dict_to_prop(value):
    if isinstance(value, dict):
        return DictToProps(value)
    if isinstance(value, (tuple, list)):
        return ListToProps(value)
    return value


def join_path(*paths):
    import os
    return os.path.join(*paths)

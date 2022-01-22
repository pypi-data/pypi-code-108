import importlib
from typing import List

import requests

config = {
    "w_import": False
}


def __write_import_area(file_path, import_list: List = None):
    if not config.get("w_import", False):
        return
    else:
        return

    ready_imports = []
    with open(file_path, "r") as f:
        data = f.read()
    for i in import_list:
        if i not in data:
            ready_imports.append(i)

    new_imports = "\n".join(ready_imports) + "\n"
    new_data = new_imports + data
    with open(file_path, "w") as f:
        f.write(new_data)


def _import(globals: dict, url: str, name=None, imports: List = None, source_file_path: str = None):
    """
    :param url:
    :param name:
    :param imports:
    :return:
    """

    if name is None:
        name = url.split("/")[-1].split(".")[0]
    try:
        content = requests.get(url)
        if content.status_code != 200:
            return
        with open(f"{name}.py", "w") as f:
            f.write(content.text)
    except Exception as e:
        print(e)
        return
    _mod = f"{name}"

    mdl = importlib.import_module(_mod)

    if imports is not None and len(imports) > 0:
        if "__all__" in mdl.__dict__:
            names = mdl.__dict__["__all__"]
        else:
            names = [x for x in mdl.__dict__ if not x.startswith("_")]

        import_list = []
        for k in names:
            if k not in imports:
                continue
            globals.update({k: getattr(mdl, k)})
            import_list.append(f"from {name} import {k}")
        return import_list
    elif "__all__" in mdl.__dict__:
        names = mdl.__dict__["__all__"]
        globals.update({k: getattr(mdl, k) for k in names})
    else:
        # otherwise we import all names that don't begin with _
        names = [x for x in mdl.__dict__ if not x.startswith("_")]
        globals.update({k: getattr(mdl, k) for k in names})


def import_all(url, imports: List = None):
    def decorator(func):
        def wrapper(*args, **kw):
            _import(func.__globals__, url)
            return func(*args, **kw)

        return wrapper

    return decorator


def import_attr(url, attr_name: str = None):
    def decorator(func):
        def wrapper(*args, **kw):
            import_list = _import(func.__globals__, url, imports=[attr_name])
            return func(*args, **kw)

        return wrapper

    return decorator

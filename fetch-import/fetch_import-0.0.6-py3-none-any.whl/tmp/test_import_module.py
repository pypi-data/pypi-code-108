from pprint import pprint

from example import sets
from fetch_import import im_fetch

_fetch_module = {}

url = "https://fastly.jsdelivr.net/gh/zmaplex/fetch_import@0.0.1/example/sets.py"


@im_fetch(url, _globals=_fetch_module)
def main():
    res = {" standard_import": {"sets": globals()["sets"]},
           "fetch_import": _fetch_module}
    pprint(res)

    standard_import_attr = {k: v for k, v in sets.__dict__.items() if not k.startswith("_")}
    fetch_import_attr = {k: v for k, v in _fetch_module["sets"].__dict__.items() if not k.startswith("_")}
    pprint(standard_import_attr)
    pprint(fetch_import_attr)


if __name__ == '__main__':
    main()

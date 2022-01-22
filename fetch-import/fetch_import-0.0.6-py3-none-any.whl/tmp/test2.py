from pprint import pprint
from fetch_import import im_fetch
import importlib
url = "https://fastly.jsdelivr.net/gh/zmaplex/fetch_import@0.0.1/example/sets.py"


def main():
    pprint(globals())



if __name__ == '__main__':

    main()
    pprint(globals())
    a = importlib.import_module("sets")
    print(a)

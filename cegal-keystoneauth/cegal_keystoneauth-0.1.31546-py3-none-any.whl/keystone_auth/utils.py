import os
from pathlib import Path


def local_storage_location():
    """The location of the auth database.

    By default ~/.cegal-keystone/auth.db, can be override by the
    environment variable CEGAL_KEYSTONE_AUTH_DB
    """
    var_name = "CEGAL_KEYSTONE_AUTH_DB"
    if var_name in os.environ:
        return os.environ[var_name]
    else:
        return f"{Path.home()}/.cegal-keystone/auth.db"


def pp_dict(d):
    """Pretty-prints dictionary"""

    def pp_internal(d, indent):
        print(r"{" + (indent + 1) * " ", end="")
        keys = d.keys()
        count = len(keys)
        for idx, k in enumerate(keys):
            if idx > 0:
                spacing = " " * (indent + 2)
            else:
                spacing = ""
            value = d[k]
            v = str(value)
            if type(value) is str:
                v = f"'{value}'"
            if type(value) is list:
                v = value
            print(f"{spacing}'{k}': {v}", end="")
            if idx < count - 1:
                print(", ")
            else:
                print(" ", end="")

        print("}")

    pp_internal(d, 0)

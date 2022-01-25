import getpass
from typing import Optional

_current_username = None


def _get_databricks_user() -> Optional[str]:
    try:
        import IPython

        ipy = IPython.get_ipython()
        if ipy is None:
            return None
        dbutils = ipy.user_ns.get("dbutils")
        if dbutils is None:
            return None
        else:
            return dbutils.notebook.entry_point.getDbutils().notebook().getContext().tags().apply("user")
    except ImportError as e:
        pass
    return None


def _get_system_user():
    return getpass.getuser()


def get_current_username() -> str:
    global _current_username
    if _current_username is None:
        _current_username = _get_current_username_uncached()
    return _current_username


def _get_current_username_uncached() -> str:
    for f in (_get_databricks_user, _get_system_user):
        user = f()
        if user:
            return user
    else:
        return ""

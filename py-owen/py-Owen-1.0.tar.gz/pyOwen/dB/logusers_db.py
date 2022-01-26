
from .. import udB


def get_logger():
    return udB.get_key("LOGUSERS") or []


def is_logger(id_):
    return id_ in get_logger()


def log_user(id_):
    pmperm = get_logger()
    pmperm.append(id_)
    return udB.set_key("LOGUSERS", pmperm)


def nolog_user(id_):
    pmperm = get_logger()
    pmperm.remove(id_)
    return udB.set_key("LOGUSERS", pmperm)

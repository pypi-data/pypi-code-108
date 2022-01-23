import abc
from abc import ABCMeta
from typing import Dict, Any
import multiprocessing as mp

PM = mp.Manager()
PNS = PM.Namespace()
_PNS_Instances = PM.Namespace()
PLock = PM.Lock()

_Instances = {}


def get_process_manager():
    return PM


def get_process_namespace(name=None):
    global PNS
    if name is None:
        return PNS
    else:
        return getattr(PNS, name)


def chk_process_namespace(name=None):
    global PNS
    _hasattr = hasattr(PNS, name)
    return _hasattr


def set_process_namespace(name: str, obj):
    global PNS
    setattr(PNS, name, obj)
    print(f"Save to Namespace object finish.")



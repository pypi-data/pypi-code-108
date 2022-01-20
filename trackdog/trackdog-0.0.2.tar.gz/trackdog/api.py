import logging
import os

from varname import argname

from trackdog.store import LocalStore
from trackdog.trackdog import Tracker


def init(project=None, run=None, debug=False):
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)
    global dog
    store = LocalStore()
    store.init(project, run)
    dog = Tracker(store)

def track(val, epoch=None, step=None):
    dog.track(val, argname("val"))

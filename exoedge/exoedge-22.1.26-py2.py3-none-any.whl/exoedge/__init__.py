"""

"""
import threading
from .__version__ import __version__

def get_thread_by_name(name):
    for thread in threading.enumerate():
        if thread.getName() == name:
            return thread
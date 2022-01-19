import multiprocessing


MANAGER = None


def set_manager(m=None):
    global MANAGER
    MANAGER = multiprocessing.Manager()


def get_manager():
    return MANAGER

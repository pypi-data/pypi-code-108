import os


def in_ipynb():
    try:
        get_ipython()
        return True
    except NameError:
        return False


def create_if_not_exists(folder):
    if not os.path.exists(folder):
        os.mkdir(folder)

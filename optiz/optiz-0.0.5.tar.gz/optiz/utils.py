import os


def in_ipynb():
    try:
        cfg = get_ipython().config
        if cfg['IPKernelApp']['parent_appname'] == 'ipython-notebook':
            return True
        else:
            return False
    except NameError:
        return False


def create_if_not_exists(folder):
    if not os.path.exists(folder):
        os.mkdir(folder)

from upyog.imports import *


logger.opt(colors=True)
tqdm.pandas()
ImageFile.LOAD_TRUNCATED_IMAGES = True


# https://stackoverflow.com/questions/15411967/how-can-i-check-if-code-is-executed-in-the-ipython-notebook
def in_notebook():
    try:
        from IPython import get_ipython

        if "IPKernelApp" not in get_ipython().config:  # pragma: no cover
            return False
    except ImportError:
        return False
    except AttributeError:
        return False
    return True


if not in_notebook():
    install()

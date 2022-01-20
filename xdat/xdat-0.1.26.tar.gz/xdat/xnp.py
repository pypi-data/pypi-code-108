import numpy
try:
    import accupy
except (ImportError, ModuleNotFoundError):
    pass

from . import xsettings


def x_sum(a, accu_method=None):
    """
    A much slower, but more accurate sum routine
    (see https://github.com/nschloe/accupy)
    """

    accu_method = xsettings.get_default(xsettings.ACCU_METHOD, accu_method)

    if accu_method == 'fsum':
        aa = accupy.fsum(a)
    elif accu_method == 'ksum':
        aa = accupy.ksum(a)
    elif accu_method == 'kahan_sum':
        aa = accupy.kahan_sum(a)
    else:
        raise ValueError(accu_method)

    return aa


def x_dot(a1, a2):
    """
    A much slower, but more accurate dot product
    (see https://github.com/nschloe/accupy)
    """
    a1 = a1.astype(float)
    a2 = a2.astype(float)
    return accupy.fdot(a1, a2)


def monkey_patch():
    numpy.x_sum = x_sum
    numpy.x_dot = x_dot

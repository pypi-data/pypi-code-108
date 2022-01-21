'''_1678.py

SupportToleranceLocationDesignation
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_SUPPORT_TOLERANCE_LOCATION_DESIGNATION = python_net_import('SMT.MastaAPI.Bearings.Tolerances', 'SupportToleranceLocationDesignation')


__docformat__ = 'restructuredtext en'
__all__ = ('SupportToleranceLocationDesignation',)


class SupportToleranceLocationDesignation(Enum):
    '''SupportToleranceLocationDesignation

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _SUPPORT_TOLERANCE_LOCATION_DESIGNATION

    __hash__ = None

    a = 0
    b = 1
    c = 2
    cd = 3
    d = 4
    e = 5
    ef = 6
    f = 7
    fg = 8
    g = 9
    h = 10
    js = 11
    j = 12
    k = 13
    m = 14
    n = 15
    p = 16
    r = 17
    s = 18
    t = 19
    u = 20
    v = 21
    x = 22
    y = 23
    z = 24
    za = 25
    zb = 26
    zc = 27
    A = 28
    B = 29
    C = 30
    CD = 31
    D = 32
    E = 33
    EF = 34
    F = 35
    FG = 36
    G = 37
    H = 38
    JS = 39
    J = 40
    K = 41
    M = 42
    N = 43
    P = 44
    R = 45
    S = 46
    T = 47
    U = 48
    V = 49
    X = 50
    Y = 51
    Z = 52
    ZA = 53
    ZB = 54
    ZC = 55


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


SupportToleranceLocationDesignation.__setattr__ = __enum_setattr
SupportToleranceLocationDesignation.__delattr__ = __enum_delattr

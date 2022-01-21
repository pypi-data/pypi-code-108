'''_1162.py

GearDesignAnalysis
'''


from mastapy.gears.analysis import _1159
from mastapy._internal.python_net import python_net_import

_GEAR_DESIGN_ANALYSIS = python_net_import('SMT.MastaAPI.Gears.Analysis', 'GearDesignAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('GearDesignAnalysis',)


class GearDesignAnalysis(_1159.AbstractGearAnalysis):
    '''GearDesignAnalysis

    This is a mastapy class.
    '''

    TYPE = _GEAR_DESIGN_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearDesignAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

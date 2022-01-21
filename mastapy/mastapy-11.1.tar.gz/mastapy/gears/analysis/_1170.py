'''_1170.py

GearSetDesignAnalysis
'''


from mastapy.gears.analysis import _1161
from mastapy._internal.python_net import python_net_import

_GEAR_SET_DESIGN_ANALYSIS = python_net_import('SMT.MastaAPI.Gears.Analysis', 'GearSetDesignAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('GearSetDesignAnalysis',)


class GearSetDesignAnalysis(_1161.AbstractGearSetAnalysis):
    '''GearSetDesignAnalysis

    This is a mastapy class.
    '''

    TYPE = _GEAR_SET_DESIGN_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearSetDesignAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

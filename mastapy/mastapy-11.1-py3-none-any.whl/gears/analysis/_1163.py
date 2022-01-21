'''_1163.py

GearImplementationAnalysis
'''


from mastapy.gears.analysis import _1162
from mastapy._internal.python_net import python_net_import

_GEAR_IMPLEMENTATION_ANALYSIS = python_net_import('SMT.MastaAPI.Gears.Analysis', 'GearImplementationAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('GearImplementationAnalysis',)


class GearImplementationAnalysis(_1162.GearDesignAnalysis):
    '''GearImplementationAnalysis

    This is a mastapy class.
    '''

    TYPE = _GEAR_IMPLEMENTATION_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearImplementationAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

'''_790.py

CylindricalGearFilletNodeStressResultsRow
'''


from mastapy._internal import constructor
from mastapy.gears.ltca import _799
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_FILLET_NODE_STRESS_RESULTS_ROW = python_net_import('SMT.MastaAPI.Gears.LTCA', 'CylindricalGearFilletNodeStressResultsRow')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearFilletNodeStressResultsRow',)


class CylindricalGearFilletNodeStressResultsRow(_799.GearFilletNodeStressResultsRow):
    '''CylindricalGearFilletNodeStressResultsRow

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_FILLET_NODE_STRESS_RESULTS_ROW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearFilletNodeStressResultsRow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def distance_along_fillet(self) -> 'float':
        '''float: 'DistanceAlongFillet' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DistanceAlongFillet

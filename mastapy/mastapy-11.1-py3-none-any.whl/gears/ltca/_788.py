'''_788.py

CylindricalGearFilletNodeStressResults
'''


from mastapy._internal import constructor
from mastapy.gears.ltca import _797
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_FILLET_NODE_STRESS_RESULTS = python_net_import('SMT.MastaAPI.Gears.LTCA', 'CylindricalGearFilletNodeStressResults')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearFilletNodeStressResults',)


class CylindricalGearFilletNodeStressResults(_797.GearFilletNodeStressResults):
    '''CylindricalGearFilletNodeStressResults

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_FILLET_NODE_STRESS_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearFilletNodeStressResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def face_width_position(self) -> 'float':
        '''float: 'FaceWidthPosition' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FaceWidthPosition

    @property
    def distance_along_fillet(self) -> 'float':
        '''float: 'DistanceAlongFillet' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DistanceAlongFillet

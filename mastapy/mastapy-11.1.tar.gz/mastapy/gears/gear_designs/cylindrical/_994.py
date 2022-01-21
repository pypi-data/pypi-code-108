'''_994.py

CylindricalMeshLinearBacklashSpecification
'''


from mastapy._internal import constructor
from mastapy.gears.gear_designs.cylindrical import _1037, _956
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_MESH_LINEAR_BACKLASH_SPECIFICATION = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'CylindricalMeshLinearBacklashSpecification')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalMeshLinearBacklashSpecification',)


class CylindricalMeshLinearBacklashSpecification(_1037.TolerancedValueSpecification['_956.BacklashSpecification']):
    '''CylindricalMeshLinearBacklashSpecification

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_MESH_LINEAR_BACKLASH_SPECIFICATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalMeshLinearBacklashSpecification.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def measurement_type(self) -> 'str':
        '''str: 'MeasurementType' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeasurementType

'''_1066.py

LinearCylindricalGearTriangularEndModification
'''


from mastapy.gears.gear_designs.cylindrical.micro_geometry import _1078
from mastapy._internal.python_net import python_net_import

_LINEAR_CYLINDRICAL_GEAR_TRIANGULAR_END_MODIFICATION = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical.MicroGeometry', 'LinearCylindricalGearTriangularEndModification')


__docformat__ = 'restructuredtext en'
__all__ = ('LinearCylindricalGearTriangularEndModification',)


class LinearCylindricalGearTriangularEndModification(_1078.SingleCylindricalGearTriangularEndModification):
    '''LinearCylindricalGearTriangularEndModification

    This is a mastapy class.
    '''

    TYPE = _LINEAR_CYLINDRICAL_GEAR_TRIANGULAR_END_MODIFICATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LinearCylindricalGearTriangularEndModification.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

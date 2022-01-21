'''_1012.py

ISO6336GeometryManufactured
'''


from mastapy._internal import constructor
from mastapy.gears.gear_designs.cylindrical import _1010
from mastapy._internal.python_net import python_net_import

_ISO6336_GEOMETRY_MANUFACTURED = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'ISO6336GeometryManufactured')


__docformat__ = 'restructuredtext en'
__all__ = ('ISO6336GeometryManufactured',)


class ISO6336GeometryManufactured(_1010.ISO6336GeometryBase):
    '''ISO6336GeometryManufactured

    This is a mastapy class.
    '''

    TYPE = _ISO6336_GEOMETRY_MANUFACTURED

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ISO6336GeometryManufactured.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def iso6336_tooth_root_chord(self) -> 'float':
        '''float: 'ISO6336ToothRootChord' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ISO6336ToothRootChord

    @property
    def iso6336_root_fillet_radius(self) -> 'float':
        '''float: 'ISO6336RootFilletRadius' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ISO6336RootFilletRadius

'''_1010.py

ISO6336GeometryBase
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_ISO6336_GEOMETRY_BASE = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'ISO6336GeometryBase')


__docformat__ = 'restructuredtext en'
__all__ = ('ISO6336GeometryBase',)


class ISO6336GeometryBase(_0.APIBase):
    '''ISO6336GeometryBase

    This is a mastapy class.
    '''

    TYPE = _ISO6336_GEOMETRY_BASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ISO6336GeometryBase.TYPE'):
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

    @property
    def virtual_number_of_teeth(self) -> 'float':
        '''float: 'VirtualNumberOfTeeth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.VirtualNumberOfTeeth

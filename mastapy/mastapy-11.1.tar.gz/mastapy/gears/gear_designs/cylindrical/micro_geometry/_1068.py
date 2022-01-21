'''_1068.py

MeshAlignment
'''


from mastapy.gears.gear_designs.cylindrical.micro_geometry import _1062
from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_MESH_ALIGNMENT = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical.MicroGeometry', 'MeshAlignment')


__docformat__ = 'restructuredtext en'
__all__ = ('MeshAlignment',)


class MeshAlignment(_0.APIBase):
    '''MeshAlignment

    This is a mastapy class.
    '''

    TYPE = _MESH_ALIGNMENT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MeshAlignment.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def gear_a_alignment(self) -> '_1062.GearAlignment':
        '''GearAlignment: 'GearAAlignment' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1062.GearAlignment)(self.wrapped.GearAAlignment) if self.wrapped.GearAAlignment is not None else None

    @property
    def gear_b_alignment(self) -> '_1062.GearAlignment':
        '''GearAlignment: 'GearBAlignment' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1062.GearAlignment)(self.wrapped.GearBAlignment) if self.wrapped.GearBAlignment is not None else None

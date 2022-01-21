'''_1145.py

GearMeshFEModel
'''


from mastapy._internal import constructor
from mastapy.gears.analysis import _1169
from mastapy._internal.python_net import python_net_import

_GEAR_MESH_FE_MODEL = python_net_import('SMT.MastaAPI.Gears.FEModel', 'GearMeshFEModel')


__docformat__ = 'restructuredtext en'
__all__ = ('GearMeshFEModel',)


class GearMeshFEModel(_1169.GearMeshImplementationDetail):
    '''GearMeshFEModel

    This is a mastapy class.
    '''

    TYPE = _GEAR_MESH_FE_MODEL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearMeshFEModel.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def number_of_loads_per_contact(self) -> 'int':
        '''int: 'NumberOfLoadsPerContact' is the original name of this property.'''

        return self.wrapped.NumberOfLoadsPerContact

    @number_of_loads_per_contact.setter
    def number_of_loads_per_contact(self, value: 'int'):
        self.wrapped.NumberOfLoadsPerContact = int(value) if value else 0

    @property
    def number_of_rotations(self) -> 'int':
        '''int: 'NumberOfRotations' is the original name of this property.'''

        return self.wrapped.NumberOfRotations

    @number_of_rotations.setter
    def number_of_rotations(self, value: 'int'):
        self.wrapped.NumberOfRotations = int(value) if value else 0

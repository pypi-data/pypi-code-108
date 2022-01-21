'''_803.py

GearMeshLoadedContactLine
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.gears.ltca import _804
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_GEAR_MESH_LOADED_CONTACT_LINE = python_net_import('SMT.MastaAPI.Gears.LTCA', 'GearMeshLoadedContactLine')


__docformat__ = 'restructuredtext en'
__all__ = ('GearMeshLoadedContactLine',)


class GearMeshLoadedContactLine(_0.APIBase):
    '''GearMeshLoadedContactLine

    This is a mastapy class.
    '''

    TYPE = _GEAR_MESH_LOADED_CONTACT_LINE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearMeshLoadedContactLine.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def contact_line_index(self) -> 'int':
        '''int: 'ContactLineIndex' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactLineIndex

    @property
    def mesh_position_index(self) -> 'int':
        '''int: 'MeshPositionIndex' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeshPositionIndex

    @property
    def loaded_contact_strip_end_points(self) -> 'List[_804.GearMeshLoadedContactPoint]':
        '''List[GearMeshLoadedContactPoint]: 'LoadedContactStripEndPoints' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.LoadedContactStripEndPoints, constructor.new(_804.GearMeshLoadedContactPoint))
        return value

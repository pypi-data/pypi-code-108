'''_2244.py

MountableComponentFromCAD
'''


from mastapy._internal import constructor
from mastapy.system_model.part_model.import_from_cad import _2235
from mastapy._internal.python_net import python_net_import

_MOUNTABLE_COMPONENT_FROM_CAD = python_net_import('SMT.MastaAPI.SystemModel.PartModel.ImportFromCAD', 'MountableComponentFromCAD')


__docformat__ = 'restructuredtext en'
__all__ = ('MountableComponentFromCAD',)


class MountableComponentFromCAD(_2235.ComponentFromCAD):
    '''MountableComponentFromCAD

    This is a mastapy class.
    '''

    TYPE = _MOUNTABLE_COMPONENT_FROM_CAD

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MountableComponentFromCAD.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def offset(self) -> 'float':
        '''float: 'Offset' is the original name of this property.'''

        return self.wrapped.Offset

    @offset.setter
    def offset(self, value: 'float'):
        self.wrapped.Offset = float(value) if value else 0.0

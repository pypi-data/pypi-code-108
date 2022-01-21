'''_699.py

MutatableFillet
'''


from mastapy._internal import constructor
from mastapy.gears.manufacturing.cylindrical.cutters import _697
from mastapy._internal.python_net import python_net_import

_MUTATABLE_FILLET = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.Cutters', 'MutatableFillet')


__docformat__ = 'restructuredtext en'
__all__ = ('MutatableFillet',)


class MutatableFillet(_697.MutatableCommon):
    '''MutatableFillet

    This is a mastapy class.
    '''

    TYPE = _MUTATABLE_FILLET

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MutatableFillet.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def radius(self) -> 'float':
        '''float: 'Radius' is the original name of this property.'''

        return self.wrapped.Radius

    @radius.setter
    def radius(self, value: 'float'):
        self.wrapped.Radius = float(value) if value else 0.0

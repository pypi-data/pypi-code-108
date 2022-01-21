'''_2190.py

Datum
'''


from mastapy._internal import constructor
from mastapy.system_model.part_model import _2186
from mastapy._internal.python_net import python_net_import

_DATUM = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'Datum')


__docformat__ = 'restructuredtext en'
__all__ = ('Datum',)


class Datum(_2186.Component):
    '''Datum

    This is a mastapy class.
    '''

    TYPE = _DATUM

    __hash__ = None

    def __init__(self, instance_to_wrap: 'Datum.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def offset(self) -> 'float':
        '''float: 'Offset' is the original name of this property.'''

        return self.wrapped.Offset

    @offset.setter
    def offset(self, value: 'float'):
        self.wrapped.Offset = float(value) if value else 0.0

    @property
    def drawing_diameter(self) -> 'float':
        '''float: 'DrawingDiameter' is the original name of this property.'''

        return self.wrapped.DrawingDiameter

    @drawing_diameter.setter
    def drawing_diameter(self, value: 'float'):
        self.wrapped.DrawingDiameter = float(value) if value else 0.0

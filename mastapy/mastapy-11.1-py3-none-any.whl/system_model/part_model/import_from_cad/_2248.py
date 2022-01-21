'''_2248.py

RollingBearingFromCAD
'''


from mastapy._internal import constructor
from mastapy.system_model.part_model.import_from_cad import _2237
from mastapy._internal.python_net import python_net_import

_ROLLING_BEARING_FROM_CAD = python_net_import('SMT.MastaAPI.SystemModel.PartModel.ImportFromCAD', 'RollingBearingFromCAD')


__docformat__ = 'restructuredtext en'
__all__ = ('RollingBearingFromCAD',)


class RollingBearingFromCAD(_2237.ConnectorFromCAD):
    '''RollingBearingFromCAD

    This is a mastapy class.
    '''

    TYPE = _ROLLING_BEARING_FROM_CAD

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RollingBearingFromCAD.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def width(self) -> 'float':
        '''float: 'Width' is the original name of this property.'''

        return self.wrapped.Width

    @width.setter
    def width(self, value: 'float'):
        self.wrapped.Width = float(value) if value else 0.0

    @property
    def bore(self) -> 'float':
        '''float: 'Bore' is the original name of this property.'''

        return self.wrapped.Bore

    @bore.setter
    def bore(self, value: 'float'):
        self.wrapped.Bore = float(value) if value else 0.0

    @property
    def outer_diameter(self) -> 'float':
        '''float: 'OuterDiameter' is the original name of this property.'''

        return self.wrapped.OuterDiameter

    @outer_diameter.setter
    def outer_diameter(self, value: 'float'):
        self.wrapped.OuterDiameter = float(value) if value else 0.0

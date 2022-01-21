'''_2246.py

PulleyFromCAD
'''


from mastapy._internal import constructor
from mastapy.system_model.part_model.import_from_cad import _2244
from mastapy._internal.python_net import python_net_import

_PULLEY_FROM_CAD = python_net_import('SMT.MastaAPI.SystemModel.PartModel.ImportFromCAD', 'PulleyFromCAD')


__docformat__ = 'restructuredtext en'
__all__ = ('PulleyFromCAD',)


class PulleyFromCAD(_2244.MountableComponentFromCAD):
    '''PulleyFromCAD

    This is a mastapy class.
    '''

    TYPE = _PULLEY_FROM_CAD

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PulleyFromCAD.TYPE'):
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
    def outer_diameter(self) -> 'float':
        '''float: 'OuterDiameter' is the original name of this property.'''

        return self.wrapped.OuterDiameter

    @outer_diameter.setter
    def outer_diameter(self, value: 'float'):
        self.wrapped.OuterDiameter = float(value) if value else 0.0

    @property
    def centre_distance(self) -> 'float':
        '''float: 'CentreDistance' is the original name of this property.'''

        return self.wrapped.CentreDistance

    @centre_distance.setter
    def centre_distance(self, value: 'float'):
        self.wrapped.CentreDistance = float(value) if value else 0.0

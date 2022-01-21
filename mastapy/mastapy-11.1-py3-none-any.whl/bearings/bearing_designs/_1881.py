'''_1881.py

DummyRollingBearing
'''


from mastapy._internal import constructor
from mastapy.bearings.bearing_designs import _1879
from mastapy._internal.python_net import python_net_import

_DUMMY_ROLLING_BEARING = python_net_import('SMT.MastaAPI.Bearings.BearingDesigns', 'DummyRollingBearing')


__docformat__ = 'restructuredtext en'
__all__ = ('DummyRollingBearing',)


class DummyRollingBearing(_1879.BearingDesign):
    '''DummyRollingBearing

    This is a mastapy class.
    '''

    TYPE = _DUMMY_ROLLING_BEARING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'DummyRollingBearing.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

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

    @property
    def width(self) -> 'float':
        '''float: 'Width' is the original name of this property.'''

        return self.wrapped.Width

    @width.setter
    def width(self, value: 'float'):
        self.wrapped.Width = float(value) if value else 0.0

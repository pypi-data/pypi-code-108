'''_23.py

ShaftKey
'''


from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.shafts import _42, _21
from mastapy._internal.python_net import python_net_import

_SHAFT_KEY = python_net_import('SMT.MastaAPI.Shafts', 'ShaftKey')


__docformat__ = 'restructuredtext en'
__all__ = ('ShaftKey',)


class ShaftKey(_21.ShaftFeature):
    '''ShaftKey

    This is a mastapy class.
    '''

    TYPE = _SHAFT_KEY

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ShaftKey.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def depth(self) -> 'float':
        '''float: 'Depth' is the original name of this property.'''

        return self.wrapped.Depth

    @depth.setter
    def depth(self, value: 'float'):
        self.wrapped.Depth = float(value) if value else 0.0

    @property
    def fillet_radius(self) -> 'float':
        '''float: 'FilletRadius' is the original name of this property.'''

        return self.wrapped.FilletRadius

    @fillet_radius.setter
    def fillet_radius(self, value: 'float'):
        self.wrapped.FilletRadius = float(value) if value else 0.0

    @property
    def width(self) -> 'float':
        '''float: 'Width' is the original name of this property.'''

        return self.wrapped.Width

    @width.setter
    def width(self, value: 'float'):
        self.wrapped.Width = float(value) if value else 0.0

    @property
    def number_of_keys(self) -> 'int':
        '''int: 'NumberOfKeys' is the original name of this property.'''

        return self.wrapped.NumberOfKeys

    @number_of_keys.setter
    def number_of_keys(self, value: 'int'):
        self.wrapped.NumberOfKeys = int(value) if value else 0

    @property
    def surface_finish(self) -> '_42.SurfaceFinishes':
        '''SurfaceFinishes: 'SurfaceFinish' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.SurfaceFinish)
        return constructor.new(_42.SurfaceFinishes)(value) if value is not None else None

    @surface_finish.setter
    def surface_finish(self, value: '_42.SurfaceFinishes'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.SurfaceFinish = value

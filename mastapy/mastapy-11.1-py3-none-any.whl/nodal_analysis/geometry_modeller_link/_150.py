'''_150.py

SpaceClaimDimension
'''


from mastapy.nodal_analysis.geometry_modeller_link import _147
from mastapy._internal import enum_with_selected_value_runtime, constructor, conversion
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_SPACE_CLAIM_DIMENSION = python_net_import('SMT.MastaAPI.NodalAnalysis.GeometryModellerLink', 'SpaceClaimDimension')


__docformat__ = 'restructuredtext en'
__all__ = ('SpaceClaimDimension',)


class SpaceClaimDimension(_0.APIBase):
    '''SpaceClaimDimension

    This is a mastapy class.
    '''

    TYPE = _SPACE_CLAIM_DIMENSION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SpaceClaimDimension.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def type_(self) -> '_147.GeometryModellerDimensionType':
        '''GeometryModellerDimensionType: 'Type' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.Type)
        return constructor.new(_147.GeometryModellerDimensionType)(value) if value is not None else None

    @type_.setter
    def type_(self, value: '_147.GeometryModellerDimensionType'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.Type = value

    @property
    def value(self) -> 'float':
        '''float: 'Value' is the original name of this property.'''

        return self.wrapped.Value

    @value.setter
    def value(self, value: 'float'):
        self.wrapped.Value = float(value) if value else 0.0

'''_449.py

VDI2737SafetyFactorReportingObject
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_VDI2737_SAFETY_FACTOR_REPORTING_OBJECT = python_net_import('SMT.MastaAPI.Gears.Rating.Cylindrical', 'VDI2737SafetyFactorReportingObject')


__docformat__ = 'restructuredtext en'
__all__ = ('VDI2737SafetyFactorReportingObject',)


class VDI2737SafetyFactorReportingObject(_0.APIBase):
    '''VDI2737SafetyFactorReportingObject

    This is a mastapy class.
    '''

    TYPE = _VDI2737_SAFETY_FACTOR_REPORTING_OBJECT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'VDI2737SafetyFactorReportingObject.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def fatigue_fracture(self) -> 'float':
        '''float: 'FatigueFracture' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FatigueFracture

    @property
    def crack_initiation(self) -> 'float':
        '''float: 'CrackInitiation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CrackInitiation

    @property
    def permanent_deformation(self) -> 'float':
        '''float: 'PermanentDeformation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PermanentDeformation

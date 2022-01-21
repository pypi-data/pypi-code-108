'''_1231.py

SplineHalfRating
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_SPLINE_HALF_RATING = python_net_import('SMT.MastaAPI.DetailedRigidConnectors.Splines.Ratings', 'SplineHalfRating')


__docformat__ = 'restructuredtext en'
__all__ = ('SplineHalfRating',)


class SplineHalfRating(_0.APIBase):
    '''SplineHalfRating

    This is a mastapy class.
    '''

    TYPE = _SPLINE_HALF_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SplineHalfRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def allowable_bending_stress(self) -> 'float':
        '''float: 'AllowableBendingStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AllowableBendingStress

    @property
    def allowable_contact_stress(self) -> 'float':
        '''float: 'AllowableContactStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AllowableContactStress

    @property
    def allowable_compressive_stress(self) -> 'float':
        '''float: 'AllowableCompressiveStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AllowableCompressiveStress

    @property
    def allowable_shear_stress(self) -> 'float':
        '''float: 'AllowableShearStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AllowableShearStress

    @property
    def allowable_bursting_stress(self) -> 'float':
        '''float: 'AllowableBurstingStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AllowableBurstingStress

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name

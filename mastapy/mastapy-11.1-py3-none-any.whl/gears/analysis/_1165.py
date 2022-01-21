'''_1165.py

GearImplementationDetail
'''


from mastapy.utility.scripting import _1515
from mastapy._internal import constructor
from mastapy.gears.analysis import _1162
from mastapy._internal.python_net import python_net_import

_GEAR_IMPLEMENTATION_DETAIL = python_net_import('SMT.MastaAPI.Gears.Analysis', 'GearImplementationDetail')


__docformat__ = 'restructuredtext en'
__all__ = ('GearImplementationDetail',)


class GearImplementationDetail(_1162.GearDesignAnalysis):
    '''GearImplementationDetail

    This is a mastapy class.
    '''

    TYPE = _GEAR_IMPLEMENTATION_DETAIL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearImplementationDetail.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def user_specified_data(self) -> '_1515.UserSpecifiedData':
        '''UserSpecifiedData: 'UserSpecifiedData' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1515.UserSpecifiedData)(self.wrapped.UserSpecifiedData) if self.wrapped.UserSpecifiedData is not None else None

'''_1175.py

GearSetImplementationDetail
'''


from mastapy._internal import constructor
from mastapy.utility.scripting import _1515
from mastapy.gears.analysis import _1170
from mastapy._internal.python_net import python_net_import

_GEAR_SET_IMPLEMENTATION_DETAIL = python_net_import('SMT.MastaAPI.Gears.Analysis', 'GearSetImplementationDetail')


__docformat__ = 'restructuredtext en'
__all__ = ('GearSetImplementationDetail',)


class GearSetImplementationDetail(_1170.GearSetDesignAnalysis):
    '''GearSetImplementationDetail

    This is a mastapy class.
    '''

    TYPE = _GEAR_SET_IMPLEMENTATION_DETAIL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearSetImplementationDetail.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.'''

        return self.wrapped.Name

    @name.setter
    def name(self, value: 'str'):
        self.wrapped.Name = str(value) if value else ''

    @property
    def user_specified_data(self) -> '_1515.UserSpecifiedData':
        '''UserSpecifiedData: 'UserSpecifiedData' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1515.UserSpecifiedData)(self.wrapped.UserSpecifiedData) if self.wrapped.UserSpecifiedData is not None else None

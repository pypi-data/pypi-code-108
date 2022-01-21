'''_1709.py

LoadedLinearBearingResults
'''


from mastapy._internal import constructor
from mastapy.bearings.bearing_results import _1703
from mastapy._internal.python_net import python_net_import

_LOADED_LINEAR_BEARING_RESULTS = python_net_import('SMT.MastaAPI.Bearings.BearingResults', 'LoadedLinearBearingResults')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedLinearBearingResults',)


class LoadedLinearBearingResults(_1703.LoadedBearingResults):
    '''LoadedLinearBearingResults

    This is a mastapy class.
    '''

    TYPE = _LOADED_LINEAR_BEARING_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedLinearBearingResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def relative_misalignment(self) -> 'float':
        '''float: 'RelativeMisalignment' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeMisalignment

'''_1172.py

GearSetImplementationAnalysis
'''


from typing import Optional

from mastapy._internal import constructor
from mastapy.gears.analysis import _1173
from mastapy._internal.python_net import python_net_import

_GEAR_SET_IMPLEMENTATION_ANALYSIS = python_net_import('SMT.MastaAPI.Gears.Analysis', 'GearSetImplementationAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('GearSetImplementationAnalysis',)


class GearSetImplementationAnalysis(_1173.GearSetImplementationAnalysisAbstract):
    '''GearSetImplementationAnalysis

    This is a mastapy class.
    '''

    TYPE = _GEAR_SET_IMPLEMENTATION_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearSetImplementationAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def valid_results_ready(self) -> 'bool':
        '''bool: 'ValidResultsReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ValidResultsReady

    def results_ready_for(self, run_all_planetary_meshes: Optional['bool'] = True) -> 'bool':
        ''' 'ResultsReadyFor' is the original name of this method.

        Args:
            run_all_planetary_meshes (bool, optional)

        Returns:
            bool
        '''

        run_all_planetary_meshes = bool(run_all_planetary_meshes)
        method_result = self.wrapped.ResultsReadyFor(run_all_planetary_meshes if run_all_planetary_meshes else False)
        return method_result

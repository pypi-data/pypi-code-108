'''_297.py

GearSetOptimisationResults
'''


from typing import List
from datetime import datetime

from mastapy.gears import _296
from mastapy._internal import constructor, conversion
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_GEAR_SET_OPTIMISATION_RESULTS = python_net_import('SMT.MastaAPI.Gears', 'GearSetOptimisationResults')


__docformat__ = 'restructuredtext en'
__all__ = ('GearSetOptimisationResults',)


class GearSetOptimisationResults(_0.APIBase):
    '''GearSetOptimisationResults

    This is a mastapy class.
    '''

    TYPE = _GEAR_SET_OPTIMISATION_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearSetOptimisationResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def results(self) -> 'List[_296.GearSetOptimisationResult]':
        '''List[GearSetOptimisationResult]: 'Results' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Results, constructor.new(_296.GearSetOptimisationResult))
        return value

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.'''

        return self.wrapped.Name

    @name.setter
    def name(self, value: 'str'):
        self.wrapped.Name = str(value) if value else ''

    @property
    def optimiser_settings_report_table(self) -> 'str':
        '''str: 'OptimiserSettingsReportTable' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.OptimiserSettingsReportTable

    @property
    def report(self) -> 'str':
        '''str: 'Report' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Report

    @property
    def run_time(self) -> 'datetime':
        '''datetime: 'RunTime' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_datetime(self.wrapped.RunTime)
        return value

    def delete_all_results(self):
        ''' 'DeleteAllResults' is the original name of this method.'''

        self.wrapped.DeleteAllResults()

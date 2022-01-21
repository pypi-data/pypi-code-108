'''_1705.py

LoadedConceptAxialClearanceBearingResults
'''


from mastapy._internal import constructor
from mastapy.bearings.bearing_results import _1706
from mastapy._internal.python_net import python_net_import

_LOADED_CONCEPT_AXIAL_CLEARANCE_BEARING_RESULTS = python_net_import('SMT.MastaAPI.Bearings.BearingResults', 'LoadedConceptAxialClearanceBearingResults')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedConceptAxialClearanceBearingResults',)


class LoadedConceptAxialClearanceBearingResults(_1706.LoadedConceptClearanceBearingResults):
    '''LoadedConceptAxialClearanceBearingResults

    This is a mastapy class.
    '''

    TYPE = _LOADED_CONCEPT_AXIAL_CLEARANCE_BEARING_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedConceptAxialClearanceBearingResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def upper_angle_of_contact(self) -> 'float':
        '''float: 'UpperAngleOfContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.UpperAngleOfContact

    @property
    def lower_angle_of_contact(self) -> 'float':
        '''float: 'LowerAngleOfContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LowerAngleOfContact

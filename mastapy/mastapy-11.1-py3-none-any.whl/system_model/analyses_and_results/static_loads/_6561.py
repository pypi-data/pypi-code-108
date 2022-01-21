'''_6561.py

ConicalGearSetHarmonicLoadData
'''


from typing import List

from mastapy.gears import _315
from mastapy._internal import enum_with_selected_value_runtime, constructor, conversion
from mastapy.math_utility import _1312
from mastapy.system_model.analyses_and_results.static_loads import _6609
from mastapy._internal.python_net import python_net_import

_CONICAL_GEAR_SET_HARMONIC_LOAD_DATA = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'ConicalGearSetHarmonicLoadData')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalGearSetHarmonicLoadData',)


class ConicalGearSetHarmonicLoadData(_6609.GearSetHarmonicLoadData):
    '''ConicalGearSetHarmonicLoadData

    This is a mastapy class.
    '''

    TYPE = _CONICAL_GEAR_SET_HARMONIC_LOAD_DATA

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalGearSetHarmonicLoadData.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def te_specification_type(self) -> '_315.TESpecificationType':
        '''TESpecificationType: 'TESpecificationType' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.TESpecificationType)
        return constructor.new(_315.TESpecificationType)(value) if value is not None else None

    @te_specification_type.setter
    def te_specification_type(self, value: '_315.TESpecificationType'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.TESpecificationType = value

    @property
    def excitations(self) -> 'List[_1312.FourierSeries]':
        '''List[FourierSeries]: 'Excitations' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Excitations, constructor.new(_1312.FourierSeries))
        return value

    def read_data_from_gleason_gemsxml(self):
        ''' 'ReadDataFromGleasonGEMSXML' is the original name of this method.'''

        self.wrapped.ReadDataFromGleasonGEMSXML()

    def read_data_from_ki_mo_sxml(self):
        ''' 'ReadDataFromKIMoSXML' is the original name of this method.'''

        self.wrapped.ReadDataFromKIMoSXML()

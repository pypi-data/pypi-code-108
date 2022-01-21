'''_564.py

PlasticSNCurve
'''


from typing import List

from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.materials import _256, _253, _254
from mastapy.gears.materials import _563
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_PLASTIC_SN_CURVE = python_net_import('SMT.MastaAPI.Gears.Materials', 'PlasticSNCurve')


__docformat__ = 'restructuredtext en'
__all__ = ('PlasticSNCurve',)


class PlasticSNCurve(_0.APIBase):
    '''PlasticSNCurve

    This is a mastapy class.
    '''

    TYPE = _PLASTIC_SN_CURVE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PlasticSNCurve.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def flank_temperature(self) -> 'float':
        '''float: 'FlankTemperature' is the original name of this property.'''

        return self.wrapped.FlankTemperature

    @flank_temperature.setter
    def flank_temperature(self, value: 'float'):
        self.wrapped.FlankTemperature = float(value) if value else 0.0

    @property
    def note_1(self) -> 'str':
        '''str: 'Note1' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Note1

    @property
    def note_2(self) -> 'str':
        '''str: 'Note2' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Note2

    @property
    def root_temperature(self) -> 'float':
        '''float: 'RootTemperature' is the original name of this property.'''

        return self.wrapped.RootTemperature

    @root_temperature.setter
    def root_temperature(self, value: 'float'):
        self.wrapped.RootTemperature = float(value) if value else 0.0

    @property
    def life_cycles(self) -> 'float':
        '''float: 'LifeCycles' is the original name of this property.'''

        return self.wrapped.LifeCycles

    @life_cycles.setter
    def life_cycles(self, value: 'float'):
        self.wrapped.LifeCycles = float(value) if value else 0.0

    @property
    def nominal_stress_number_bending(self) -> 'float':
        '''float: 'NominalStressNumberBending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NominalStressNumberBending

    @property
    def allowable_stress_number_bending(self) -> 'float':
        '''float: 'AllowableStressNumberBending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AllowableStressNumberBending

    @property
    def allowable_stress_number_contact(self) -> 'float':
        '''float: 'AllowableStressNumberContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AllowableStressNumberContact

    @property
    def lubricant(self) -> '_256.VDI2736LubricantType':
        '''VDI2736LubricantType: 'Lubricant' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.Lubricant)
        return constructor.new(_256.VDI2736LubricantType)(value) if value is not None else None

    @lubricant.setter
    def lubricant(self, value: '_256.VDI2736LubricantType'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.Lubricant = value

    @property
    def number_of_rows_in_the_bending_sn_table(self) -> 'int':
        '''int: 'NumberOfRowsInTheBendingSNTable' is the original name of this property.'''

        return self.wrapped.NumberOfRowsInTheBendingSNTable

    @number_of_rows_in_the_bending_sn_table.setter
    def number_of_rows_in_the_bending_sn_table(self, value: 'int'):
        self.wrapped.NumberOfRowsInTheBendingSNTable = int(value) if value else 0

    @property
    def number_of_rows_in_the_contact_sn_table(self) -> 'int':
        '''int: 'NumberOfRowsInTheContactSNTable' is the original name of this property.'''

        return self.wrapped.NumberOfRowsInTheContactSNTable

    @number_of_rows_in_the_contact_sn_table.setter
    def number_of_rows_in_the_contact_sn_table(self, value: 'int'):
        self.wrapped.NumberOfRowsInTheContactSNTable = int(value) if value else 0

    @property
    def material(self) -> '_563.PlasticCylindricalGearMaterial':
        '''PlasticCylindricalGearMaterial: 'Material' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_563.PlasticCylindricalGearMaterial)(self.wrapped.Material) if self.wrapped.Material is not None else None

    @property
    def bending_stress_cycle_data(self) -> 'List[_253.StressCyclesDataForTheBendingSNCurveOfAPlasticMaterial]':
        '''List[StressCyclesDataForTheBendingSNCurveOfAPlasticMaterial]: 'BendingStressCycleData' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BendingStressCycleData, constructor.new(_253.StressCyclesDataForTheBendingSNCurveOfAPlasticMaterial))
        return value

    @property
    def contact_stress_cycle_data(self) -> 'List[_254.StressCyclesDataForTheContactSNCurveOfAPlasticMaterial]':
        '''List[StressCyclesDataForTheContactSNCurveOfAPlasticMaterial]: 'ContactStressCycleData' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ContactStressCycleData, constructor.new(_254.StressCyclesDataForTheContactSNCurveOfAPlasticMaterial))
        return value

    @property
    def bending_stress_cycle_data_for_damage_tables(self) -> 'List[_253.StressCyclesDataForTheBendingSNCurveOfAPlasticMaterial]':
        '''List[StressCyclesDataForTheBendingSNCurveOfAPlasticMaterial]: 'BendingStressCycleDataForDamageTables' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BendingStressCycleDataForDamageTables, constructor.new(_253.StressCyclesDataForTheBendingSNCurveOfAPlasticMaterial))
        return value

    @property
    def contact_stress_cycle_data_for_damage_tables(self) -> 'List[_254.StressCyclesDataForTheContactSNCurveOfAPlasticMaterial]':
        '''List[StressCyclesDataForTheContactSNCurveOfAPlasticMaterial]: 'ContactStressCycleDataForDamageTables' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ContactStressCycleDataForDamageTables, constructor.new(_254.StressCyclesDataForTheContactSNCurveOfAPlasticMaterial))
        return value

    @property
    def report_names(self) -> 'List[str]':
        '''List[str]: 'ReportNames' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ReportNames, str)
        return value

    def output_default_report_to(self, file_path: 'str'):
        ''' 'OutputDefaultReportTo' is the original name of this method.

        Args:
            file_path (str)
        '''

        file_path = str(file_path)
        self.wrapped.OutputDefaultReportTo(file_path if file_path else '')

    def get_default_report_with_encoded_images(self) -> 'str':
        ''' 'GetDefaultReportWithEncodedImages' is the original name of this method.

        Returns:
            str
        '''

        method_result = self.wrapped.GetDefaultReportWithEncodedImages()
        return method_result

    def output_active_report_to(self, file_path: 'str'):
        ''' 'OutputActiveReportTo' is the original name of this method.

        Args:
            file_path (str)
        '''

        file_path = str(file_path)
        self.wrapped.OutputActiveReportTo(file_path if file_path else '')

    def output_active_report_as_text_to(self, file_path: 'str'):
        ''' 'OutputActiveReportAsTextTo' is the original name of this method.

        Args:
            file_path (str)
        '''

        file_path = str(file_path)
        self.wrapped.OutputActiveReportAsTextTo(file_path if file_path else '')

    def get_active_report_with_encoded_images(self) -> 'str':
        ''' 'GetActiveReportWithEncodedImages' is the original name of this method.

        Returns:
            str
        '''

        method_result = self.wrapped.GetActiveReportWithEncodedImages()
        return method_result

    def output_named_report_to(self, report_name: 'str', file_path: 'str'):
        ''' 'OutputNamedReportTo' is the original name of this method.

        Args:
            report_name (str)
            file_path (str)
        '''

        report_name = str(report_name)
        file_path = str(file_path)
        self.wrapped.OutputNamedReportTo(report_name if report_name else '', file_path if file_path else '')

    def output_named_report_as_masta_report(self, report_name: 'str', file_path: 'str'):
        ''' 'OutputNamedReportAsMastaReport' is the original name of this method.

        Args:
            report_name (str)
            file_path (str)
        '''

        report_name = str(report_name)
        file_path = str(file_path)
        self.wrapped.OutputNamedReportAsMastaReport(report_name if report_name else '', file_path if file_path else '')

    def output_named_report_as_text_to(self, report_name: 'str', file_path: 'str'):
        ''' 'OutputNamedReportAsTextTo' is the original name of this method.

        Args:
            report_name (str)
            file_path (str)
        '''

        report_name = str(report_name)
        file_path = str(file_path)
        self.wrapped.OutputNamedReportAsTextTo(report_name if report_name else '', file_path if file_path else '')

    def get_named_report_with_encoded_images(self, report_name: 'str') -> 'str':
        ''' 'GetNamedReportWithEncodedImages' is the original name of this method.

        Args:
            report_name (str)

        Returns:
            str
        '''

        report_name = str(report_name)
        method_result = self.wrapped.GetNamedReportWithEncodedImages(report_name if report_name else '')
        return method_result

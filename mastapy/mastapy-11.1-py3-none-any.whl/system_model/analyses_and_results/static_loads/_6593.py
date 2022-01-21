'''_6593.py

ElectricMachineHarmonicLoadExcelImportOptions
'''


from mastapy.system_model.analyses_and_results.static_loads import _6595
from mastapy._internal.python_net import python_net_import

_ELECTRIC_MACHINE_HARMONIC_LOAD_EXCEL_IMPORT_OPTIONS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'ElectricMachineHarmonicLoadExcelImportOptions')


__docformat__ = 'restructuredtext en'
__all__ = ('ElectricMachineHarmonicLoadExcelImportOptions',)


class ElectricMachineHarmonicLoadExcelImportOptions(_6595.ElectricMachineHarmonicLoadImportOptionsBase):
    '''ElectricMachineHarmonicLoadExcelImportOptions

    This is a mastapy class.
    '''

    TYPE = _ELECTRIC_MACHINE_HARMONIC_LOAD_EXCEL_IMPORT_OPTIONS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ElectricMachineHarmonicLoadExcelImportOptions.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

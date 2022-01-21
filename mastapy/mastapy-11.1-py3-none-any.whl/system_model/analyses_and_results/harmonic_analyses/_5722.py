'''_5722.py

ElectricMachineStatorToothAxialLoadsExcitationDetail
'''


from mastapy.system_model.analyses_and_results.harmonic_analyses import _5723
from mastapy._internal.python_net import python_net_import

_ELECTRIC_MACHINE_STATOR_TOOTH_AXIAL_LOADS_EXCITATION_DETAIL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses', 'ElectricMachineStatorToothAxialLoadsExcitationDetail')


__docformat__ = 'restructuredtext en'
__all__ = ('ElectricMachineStatorToothAxialLoadsExcitationDetail',)


class ElectricMachineStatorToothAxialLoadsExcitationDetail(_5723.ElectricMachineStatorToothLoadsExcitationDetail):
    '''ElectricMachineStatorToothAxialLoadsExcitationDetail

    This is a mastapy class.
    '''

    TYPE = _ELECTRIC_MACHINE_STATOR_TOOTH_AXIAL_LOADS_EXCITATION_DETAIL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ElectricMachineStatorToothAxialLoadsExcitationDetail.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

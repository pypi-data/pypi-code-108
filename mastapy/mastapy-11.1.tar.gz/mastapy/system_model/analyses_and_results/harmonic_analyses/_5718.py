'''_5718.py

ElectricMachineRotorXMomentPeriodicExcitationDetail
'''


from mastapy.system_model.analyses_and_results.harmonic_analyses import _5716
from mastapy._internal.python_net import python_net_import

_ELECTRIC_MACHINE_ROTOR_X_MOMENT_PERIODIC_EXCITATION_DETAIL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses', 'ElectricMachineRotorXMomentPeriodicExcitationDetail')


__docformat__ = 'restructuredtext en'
__all__ = ('ElectricMachineRotorXMomentPeriodicExcitationDetail',)


class ElectricMachineRotorXMomentPeriodicExcitationDetail(_5716.ElectricMachinePeriodicExcitationDetail):
    '''ElectricMachineRotorXMomentPeriodicExcitationDetail

    This is a mastapy class.
    '''

    TYPE = _ELECTRIC_MACHINE_ROTOR_X_MOMENT_PERIODIC_EXCITATION_DETAIL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ElectricMachineRotorXMomentPeriodicExcitationDetail.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

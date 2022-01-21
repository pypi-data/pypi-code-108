'''_253.py

StressCyclesDataForTheBendingSNCurveOfAPlasticMaterial
'''


from mastapy._internal import constructor
from mastapy.materials import _208
from mastapy._internal.python_net import python_net_import

_STRESS_CYCLES_DATA_FOR_THE_BENDING_SN_CURVE_OF_A_PLASTIC_MATERIAL = python_net_import('SMT.MastaAPI.Materials', 'StressCyclesDataForTheBendingSNCurveOfAPlasticMaterial')


__docformat__ = 'restructuredtext en'
__all__ = ('StressCyclesDataForTheBendingSNCurveOfAPlasticMaterial',)


class StressCyclesDataForTheBendingSNCurveOfAPlasticMaterial(_208.AbstractStressCyclesDataForAnSNCurveOfAPlasticMaterial):
    '''StressCyclesDataForTheBendingSNCurveOfAPlasticMaterial

    This is a mastapy class.
    '''

    TYPE = _STRESS_CYCLES_DATA_FOR_THE_BENDING_SN_CURVE_OF_A_PLASTIC_MATERIAL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'StressCyclesDataForTheBendingSNCurveOfAPlasticMaterial.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def bending_fatigue_strength_under_pulsating_stress(self) -> 'float':
        '''float: 'BendingFatigueStrengthUnderPulsatingStress' is the original name of this property.'''

        return self.wrapped.BendingFatigueStrengthUnderPulsatingStress

    @bending_fatigue_strength_under_pulsating_stress.setter
    def bending_fatigue_strength_under_pulsating_stress(self, value: 'float'):
        self.wrapped.BendingFatigueStrengthUnderPulsatingStress = float(value) if value else 0.0

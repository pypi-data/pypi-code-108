'''_254.py

StressCyclesDataForTheContactSNCurveOfAPlasticMaterial
'''


from mastapy._internal import constructor
from mastapy.materials import _208
from mastapy._internal.python_net import python_net_import

_STRESS_CYCLES_DATA_FOR_THE_CONTACT_SN_CURVE_OF_A_PLASTIC_MATERIAL = python_net_import('SMT.MastaAPI.Materials', 'StressCyclesDataForTheContactSNCurveOfAPlasticMaterial')


__docformat__ = 'restructuredtext en'
__all__ = ('StressCyclesDataForTheContactSNCurveOfAPlasticMaterial',)


class StressCyclesDataForTheContactSNCurveOfAPlasticMaterial(_208.AbstractStressCyclesDataForAnSNCurveOfAPlasticMaterial):
    '''StressCyclesDataForTheContactSNCurveOfAPlasticMaterial

    This is a mastapy class.
    '''

    TYPE = _STRESS_CYCLES_DATA_FOR_THE_CONTACT_SN_CURVE_OF_A_PLASTIC_MATERIAL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'StressCyclesDataForTheContactSNCurveOfAPlasticMaterial.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def contact_fatigue_strength_under_pulsating_stress(self) -> 'float':
        '''float: 'ContactFatigueStrengthUnderPulsatingStress' is the original name of this property.'''

        return self.wrapped.ContactFatigueStrengthUnderPulsatingStress

    @contact_fatigue_strength_under_pulsating_stress.setter
    def contact_fatigue_strength_under_pulsating_stress(self, value: 'float'):
        self.wrapped.ContactFatigueStrengthUnderPulsatingStress = float(value) if value else 0.0

'''_14.py

GenericStressConcentrationFactor
'''


from mastapy._internal import constructor
from mastapy.shafts import _21
from mastapy._internal.python_net import python_net_import

_GENERIC_STRESS_CONCENTRATION_FACTOR = python_net_import('SMT.MastaAPI.Shafts', 'GenericStressConcentrationFactor')


__docformat__ = 'restructuredtext en'
__all__ = ('GenericStressConcentrationFactor',)


class GenericStressConcentrationFactor(_21.ShaftFeature):
    '''GenericStressConcentrationFactor

    This is a mastapy class.
    '''

    TYPE = _GENERIC_STRESS_CONCENTRATION_FACTOR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GenericStressConcentrationFactor.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def tension_factor(self) -> 'float':
        '''float: 'TensionFactor' is the original name of this property.'''

        return self.wrapped.TensionFactor

    @tension_factor.setter
    def tension_factor(self, value: 'float'):
        self.wrapped.TensionFactor = float(value) if value else 0.0

    @property
    def bending_factor(self) -> 'float':
        '''float: 'BendingFactor' is the original name of this property.'''

        return self.wrapped.BendingFactor

    @bending_factor.setter
    def bending_factor(self, value: 'float'):
        self.wrapped.BendingFactor = float(value) if value else 0.0

    @property
    def torsion_factor(self) -> 'float':
        '''float: 'TorsionFactor' is the original name of this property.'''

        return self.wrapped.TorsionFactor

    @torsion_factor.setter
    def torsion_factor(self, value: 'float'):
        self.wrapped.TorsionFactor = float(value) if value else 0.0

    @property
    def length(self) -> 'float':
        '''float: 'Length' is the original name of this property.'''

        return self.wrapped.Length

    @length.setter
    def length(self, value: 'float'):
        self.wrapped.Length = float(value) if value else 0.0

    def add_new_generic_scf(self):
        ''' 'AddNewGenericSCF' is the original name of this method.'''

        self.wrapped.AddNewGenericSCF()

'''_1268.py

BoltMaterial
'''


from mastapy.bolts import _1283, _1264
from mastapy._internal import enum_with_selected_value_runtime, constructor, conversion
from mastapy._internal.python_net import python_net_import

_BOLT_MATERIAL = python_net_import('SMT.MastaAPI.Bolts', 'BoltMaterial')


__docformat__ = 'restructuredtext en'
__all__ = ('BoltMaterial',)


class BoltMaterial(_1264.BoltedJointMaterial):
    '''BoltMaterial

    This is a mastapy class.
    '''

    TYPE = _BOLT_MATERIAL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BoltMaterial.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def strength_grade(self) -> '_1283.StrengthGrades':
        '''StrengthGrades: 'StrengthGrade' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.StrengthGrade)
        return constructor.new(_1283.StrengthGrades)(value) if value is not None else None

    @strength_grade.setter
    def strength_grade(self, value: '_1283.StrengthGrades'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.StrengthGrade = value

    @property
    def minimum_tensile_strength(self) -> 'float':
        '''float: 'MinimumTensileStrength' is the original name of this property.'''

        return self.wrapped.MinimumTensileStrength

    @minimum_tensile_strength.setter
    def minimum_tensile_strength(self, value: 'float'):
        self.wrapped.MinimumTensileStrength = float(value) if value else 0.0

    @property
    def shearing_strength(self) -> 'float':
        '''float: 'ShearingStrength' is the original name of this property.'''

        return self.wrapped.ShearingStrength

    @shearing_strength.setter
    def shearing_strength(self, value: 'float'):
        self.wrapped.ShearingStrength = float(value) if value else 0.0

    @property
    def proof_stress(self) -> 'float':
        '''float: 'ProofStress' is the original name of this property.'''

        return self.wrapped.ProofStress

    @proof_stress.setter
    def proof_stress(self, value: 'float'):
        self.wrapped.ProofStress = float(value) if value else 0.0

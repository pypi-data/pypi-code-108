'''_4115.py

ParametricStudyDOEResultVariable
'''


from mastapy.math_utility.optimisation import _1354, _1352
from mastapy._internal import enum_with_selected_value_runtime, constructor, conversion
from mastapy._internal.python_net import python_net_import

_PARAMETRIC_STUDY_DOE_RESULT_VARIABLE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools', 'ParametricStudyDOEResultVariable')


__docformat__ = 'restructuredtext en'
__all__ = ('ParametricStudyDOEResultVariable',)


class ParametricStudyDOEResultVariable(_1352.ParetoOptimisationVariableBase):
    '''ParametricStudyDOEResultVariable

    This is a mastapy class.
    '''

    TYPE = _PARAMETRIC_STUDY_DOE_RESULT_VARIABLE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ParametricStudyDOEResultVariable.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def target(self) -> '_1354.PropertyTargetForDominantCandidateSearch':
        '''PropertyTargetForDominantCandidateSearch: 'Target' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.Target)
        return constructor.new(_1354.PropertyTargetForDominantCandidateSearch)(value) if value is not None else None

    @target.setter
    def target(self, value: '_1354.PropertyTargetForDominantCandidateSearch'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.Target = value

    @property
    def parameter_name(self) -> 'str':
        '''str: 'ParameterName' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ParameterName

    @property
    def entity_name(self) -> 'str':
        '''str: 'EntityName' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EntityName

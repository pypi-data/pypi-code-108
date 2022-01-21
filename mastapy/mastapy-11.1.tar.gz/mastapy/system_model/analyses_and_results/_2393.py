'''_2393.py

DesignEntitySingleContextAnalysis
'''


from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results import _2391
from mastapy._internal.python_net import python_net_import

_DESIGN_ENTITY_SINGLE_CONTEXT_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults', 'DesignEntitySingleContextAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('DesignEntitySingleContextAnalysis',)


class DesignEntitySingleContextAnalysis(_2391.DesignEntityAnalysis):
    '''DesignEntitySingleContextAnalysis

    This is a mastapy class.
    '''

    TYPE = _DESIGN_ENTITY_SINGLE_CONTEXT_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'DesignEntitySingleContextAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def parametric_study_index_1(self) -> 'int':
        '''int: 'ParametricStudyIndex1' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ParametricStudyIndex1

    @property
    def parametric_study_index_2(self) -> 'int':
        '''int: 'ParametricStudyIndex2' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ParametricStudyIndex2

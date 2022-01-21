'''_2367.py

DynamicModelAtAStiffnessAnalysis
'''


from mastapy.system_model.analyses_and_results import _2360
from mastapy._internal.python_net import python_net_import

_DYNAMIC_MODEL_AT_A_STIFFNESS_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults', 'DynamicModelAtAStiffnessAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('DynamicModelAtAStiffnessAnalysis',)


class DynamicModelAtAStiffnessAnalysis(_2360.SingleAnalysis):
    '''DynamicModelAtAStiffnessAnalysis

    This is a mastapy class.
    '''

    TYPE = _DYNAMIC_MODEL_AT_A_STIFFNESS_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'DynamicModelAtAStiffnessAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

'''_4355.py

DynamicModelAtAStiffness
'''


from mastapy.system_model.analyses_and_results.dynamic_analyses import _2366
from mastapy._internal.python_net import python_net_import

_DYNAMIC_MODEL_AT_A_STIFFNESS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtAStiffness', 'DynamicModelAtAStiffness')


__docformat__ = 'restructuredtext en'
__all__ = ('DynamicModelAtAStiffness',)


class DynamicModelAtAStiffness(_2366.DynamicAnalysis):
    '''DynamicModelAtAStiffness

    This is a mastapy class.
    '''

    TYPE = _DYNAMIC_MODEL_AT_A_STIFFNESS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'DynamicModelAtAStiffness.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

'''_4118.py

ParametricStudyStaticLoad
'''


from mastapy.system_model.analyses_and_results.static_loads import _6519
from mastapy._internal.python_net import python_net_import

_PARAMETRIC_STUDY_STATIC_LOAD = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools', 'ParametricStudyStaticLoad')


__docformat__ = 'restructuredtext en'
__all__ = ('ParametricStudyStaticLoad',)


class ParametricStudyStaticLoad(_6519.StaticLoadCase):
    '''ParametricStudyStaticLoad

    This is a mastapy class.
    '''

    TYPE = _PARAMETRIC_STUDY_STATIC_LOAD

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ParametricStudyStaticLoad.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

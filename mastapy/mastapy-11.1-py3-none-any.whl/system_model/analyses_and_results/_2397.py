'''_2397.py

PartAnalysis
'''


from mastapy.system_model.analyses_and_results import _2393
from mastapy._internal.python_net import python_net_import

_PART_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults', 'PartAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('PartAnalysis',)


class PartAnalysis(_2393.DesignEntitySingleContextAnalysis):
    '''PartAnalysis

    This is a mastapy class.
    '''

    TYPE = _PART_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PartAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

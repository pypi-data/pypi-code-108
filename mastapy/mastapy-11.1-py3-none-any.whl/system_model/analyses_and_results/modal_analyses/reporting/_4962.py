'''_4962.py

CampbellDiagramReport
'''


from mastapy.utility.report import _1529
from mastapy._internal.python_net import python_net_import

_CAMPBELL_DIAGRAM_REPORT = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses.Reporting', 'CampbellDiagramReport')


__docformat__ = 'restructuredtext en'
__all__ = ('CampbellDiagramReport',)


class CampbellDiagramReport(_1529.CustomReportChart):
    '''CampbellDiagramReport

    This is a mastapy class.
    '''

    TYPE = _CAMPBELL_DIAGRAM_REPORT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CampbellDiagramReport.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

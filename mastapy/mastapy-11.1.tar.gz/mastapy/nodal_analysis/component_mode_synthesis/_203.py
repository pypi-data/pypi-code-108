'''_203.py

HarmonicCMSResults
'''


from mastapy.nodal_analysis.component_mode_synthesis import _202
from mastapy._internal.python_net import python_net_import

_HARMONIC_CMS_RESULTS = python_net_import('SMT.MastaAPI.NodalAnalysis.ComponentModeSynthesis', 'HarmonicCMSResults')


__docformat__ = 'restructuredtext en'
__all__ = ('HarmonicCMSResults',)


class HarmonicCMSResults(_202.CMSResults):
    '''HarmonicCMSResults

    This is a mastapy class.
    '''

    TYPE = _HARMONIC_CMS_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'HarmonicCMSResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

'''_2567.py

TorsionalSystemDeflection
'''


from mastapy.system_model.analyses_and_results.system_deflections import _2560
from mastapy._internal.python_net import python_net_import

_TORSIONAL_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections', 'TorsionalSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('TorsionalSystemDeflection',)


class TorsionalSystemDeflection(_2560.SystemDeflection):
    '''TorsionalSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _TORSIONAL_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'TorsionalSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

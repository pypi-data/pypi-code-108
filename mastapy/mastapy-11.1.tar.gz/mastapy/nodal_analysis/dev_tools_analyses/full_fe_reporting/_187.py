'''_187.py

ElementPropertiesSolid
'''


from mastapy.nodal_analysis.dev_tools_analyses.full_fe_reporting import _189
from mastapy._internal.python_net import python_net_import

_ELEMENT_PROPERTIES_SOLID = python_net_import('SMT.MastaAPI.NodalAnalysis.DevToolsAnalyses.FullFEReporting', 'ElementPropertiesSolid')


__docformat__ = 'restructuredtext en'
__all__ = ('ElementPropertiesSolid',)


class ElementPropertiesSolid(_189.ElementPropertiesWithMaterial):
    '''ElementPropertiesSolid

    This is a mastapy class.
    '''

    TYPE = _ELEMENT_PROPERTIES_SOLID

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ElementPropertiesSolid.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

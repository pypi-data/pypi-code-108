'''_182.py

ElementPropertiesBeam
'''


from mastapy.fe_tools.vis_tools_global.vis_tools_global_enums import _1178
from mastapy._internal import enum_with_selected_value_runtime, constructor, conversion
from mastapy.nodal_analysis.dev_tools_analyses.full_fe_reporting import _189
from mastapy._internal.python_net import python_net_import

_ELEMENT_PROPERTIES_BEAM = python_net_import('SMT.MastaAPI.NodalAnalysis.DevToolsAnalyses.FullFEReporting', 'ElementPropertiesBeam')


__docformat__ = 'restructuredtext en'
__all__ = ('ElementPropertiesBeam',)


class ElementPropertiesBeam(_189.ElementPropertiesWithMaterial):
    '''ElementPropertiesBeam

    This is a mastapy class.
    '''

    TYPE = _ELEMENT_PROPERTIES_BEAM

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ElementPropertiesBeam.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def section_type(self) -> '_1178.BeamSectionType':
        '''BeamSectionType: 'SectionType' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_enum(self.wrapped.SectionType)
        return constructor.new(_1178.BeamSectionType)(value) if value is not None else None

    @property
    def section_dimensions(self) -> 'str':
        '''str: 'SectionDimensions' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SectionDimensions

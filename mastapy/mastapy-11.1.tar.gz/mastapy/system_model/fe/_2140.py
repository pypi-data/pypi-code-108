'''_2140.py

MaterialPropertiesWithSelection
'''


from mastapy.nodal_analysis.dev_tools_analyses.full_fe_reporting import _190
from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_MATERIAL_PROPERTIES_WITH_SELECTION = python_net_import('SMT.MastaAPI.SystemModel.FE', 'MaterialPropertiesWithSelection')


__docformat__ = 'restructuredtext en'
__all__ = ('MaterialPropertiesWithSelection',)


class MaterialPropertiesWithSelection(_0.APIBase):
    '''MaterialPropertiesWithSelection

    This is a mastapy class.
    '''

    TYPE = _MATERIAL_PROPERTIES_WITH_SELECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MaterialPropertiesWithSelection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def material_properties(self) -> '_190.MaterialPropertiesReporting':
        '''MaterialPropertiesReporting: 'MaterialProperties' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_190.MaterialPropertiesReporting)(self.wrapped.MaterialProperties) if self.wrapped.MaterialProperties is not None else None

    def select_nodes(self):
        ''' 'SelectNodes' is the original name of this method.'''

        self.wrapped.SelectNodes()

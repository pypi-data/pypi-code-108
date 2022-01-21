'''_2177.py

AbstractAssembly
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.system_model.part_model import _2186, _2209
from mastapy._internal.python_net import python_net_import

_ABSTRACT_ASSEMBLY = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'AbstractAssembly')


__docformat__ = 'restructuredtext en'
__all__ = ('AbstractAssembly',)


class AbstractAssembly(_2209.Part):
    '''AbstractAssembly

    This is a mastapy class.
    '''

    TYPE = _ABSTRACT_ASSEMBLY

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AbstractAssembly.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def mass_of_assembly(self) -> 'float':
        '''float: 'MassOfAssembly' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MassOfAssembly

    @property
    def components_with_unknown_mass_properties(self) -> 'List[_2186.Component]':
        '''List[Component]: 'ComponentsWithUnknownMassProperties' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentsWithUnknownMassProperties, constructor.new(_2186.Component))
        return value

    @property
    def components_with_zero_mass_properties(self) -> 'List[_2186.Component]':
        '''List[Component]: 'ComponentsWithZeroMassProperties' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentsWithZeroMassProperties, constructor.new(_2186.Component))
        return value

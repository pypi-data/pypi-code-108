'''_2683.py

ShaftDutyCycleSystemDeflection
'''


from typing import List

from mastapy.system_model.part_model.shaft_model import _2223
from mastapy._internal import constructor, conversion
from mastapy.shafts import _19
from mastapy.system_model.analyses_and_results.system_deflections import _2539
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_SHAFT_DUTY_CYCLE_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Compound', 'ShaftDutyCycleSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('ShaftDutyCycleSystemDeflection',)


class ShaftDutyCycleSystemDeflection(_0.APIBase):
    '''ShaftDutyCycleSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _SHAFT_DUTY_CYCLE_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ShaftDutyCycleSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def shaft_design(self) -> '_2223.Shaft':
        '''Shaft: 'ShaftDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2223.Shaft)(self.wrapped.ShaftDesign) if self.wrapped.ShaftDesign is not None else None

    @property
    def shaft_damage_results(self) -> '_19.ShaftDamageResults':
        '''ShaftDamageResults: 'ShaftDamageResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_19.ShaftDamageResults)(self.wrapped.ShaftDamageResults) if self.wrapped.ShaftDamageResults is not None else None

    @property
    def shaft_static_analyses(self) -> 'List[_2539.ShaftSystemDeflection]':
        '''List[ShaftSystemDeflection]: 'ShaftStaticAnalyses' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ShaftStaticAnalyses, constructor.new(_2539.ShaftSystemDeflection))
        return value

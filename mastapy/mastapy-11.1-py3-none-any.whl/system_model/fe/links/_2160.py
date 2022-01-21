'''_2160.py

ElectricMachineStatorFELink
'''


from mastapy.system_model.fe import _2116
from mastapy._internal import constructor
from mastapy.system_model.fe.links import _2166
from mastapy._internal.python_net import python_net_import

_ELECTRIC_MACHINE_STATOR_FE_LINK = python_net_import('SMT.MastaAPI.SystemModel.FE.Links', 'ElectricMachineStatorFELink')


__docformat__ = 'restructuredtext en'
__all__ = ('ElectricMachineStatorFELink',)


class ElectricMachineStatorFELink(_2166.MultiNodeFELink):
    '''ElectricMachineStatorFELink

    This is a mastapy class.
    '''

    TYPE = _ELECTRIC_MACHINE_STATOR_FE_LINK

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ElectricMachineStatorFELink.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def electric_machine_dynamic_load_data(self) -> '_2116.ElectricMachineDynamicLoadData':
        '''ElectricMachineDynamicLoadData: 'ElectricMachineDynamicLoadData' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2116.ElectricMachineDynamicLoadData)(self.wrapped.ElectricMachineDynamicLoadData) if self.wrapped.ElectricMachineDynamicLoadData is not None else None

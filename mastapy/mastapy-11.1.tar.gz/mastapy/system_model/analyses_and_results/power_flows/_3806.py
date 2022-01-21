'''_3806.py

CVTPowerFlow
'''


from mastapy.system_model.part_model.couplings import _2326
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.power_flows import _3775
from mastapy._internal.python_net import python_net_import

_CVT_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows', 'CVTPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('CVTPowerFlow',)


class CVTPowerFlow(_3775.BeltDrivePowerFlow):
    '''CVTPowerFlow

    This is a mastapy class.
    '''

    TYPE = _CVT_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CVTPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2326.CVT':
        '''CVT: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2326.CVT)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

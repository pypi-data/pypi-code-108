'''_860.py

CylindricalGearTwoDimensionalFEAnalysis
'''


from mastapy._internal import constructor
from mastapy.nodal_analysis.dev_tools_analyses import _159
from mastapy.gears.gear_two_d_fe_analysis import _861
from mastapy.nodal_analysis.states import _119
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_TWO_DIMENSIONAL_FE_ANALYSIS = python_net_import('SMT.MastaAPI.Gears.GearTwoDFEAnalysis', 'CylindricalGearTwoDimensionalFEAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearTwoDimensionalFEAnalysis',)


class CylindricalGearTwoDimensionalFEAnalysis(_0.APIBase):
    '''CylindricalGearTwoDimensionalFEAnalysis

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_TWO_DIMENSIONAL_FE_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearTwoDimensionalFEAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def number_of_stress_states(self) -> 'int':
        '''int: 'NumberOfStressStates' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NumberOfStressStates

    @property
    def fe_model(self) -> '_159.FEModel':
        '''FEModel: 'FEModel' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_159.FEModel)(self.wrapped.FEModel) if self.wrapped.FEModel is not None else None

    @property
    def findley_critical_plane_analysis(self) -> '_861.FindleyCriticalPlaneAnalysis':
        '''FindleyCriticalPlaneAnalysis: 'FindleyCriticalPlaneAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_861.FindleyCriticalPlaneAnalysis)(self.wrapped.FindleyCriticalPlaneAnalysis) if self.wrapped.FindleyCriticalPlaneAnalysis is not None else None

    def get_stress_states(self, index: 'int') -> '_119.NodeVectorState':
        ''' 'GetStressStates' is the original name of this method.

        Args:
            index (int)

        Returns:
            mastapy.nodal_analysis.states.NodeVectorState
        '''

        index = int(index)
        method_result = self.wrapped.GetStressStates(index if index else 0)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def perform(self):
        ''' 'Perform' is the original name of this method.'''

        self.wrapped.Perform()

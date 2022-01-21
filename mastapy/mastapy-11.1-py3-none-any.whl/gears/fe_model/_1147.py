'''_1147.py

GearSetFEModel
'''


from typing import List

from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.nodal_analysis import _55
from mastapy.gears.fe_model import _1145, _1144
from mastapy import _7275
from mastapy._internal.python_net import python_net_import
from mastapy.gears.analysis import _1175

_TASK_PROGRESS = python_net_import('SMT.MastaAPIUtility', 'TaskProgress')
_GEAR_SET_FE_MODEL = python_net_import('SMT.MastaAPI.Gears.FEModel', 'GearSetFEModel')


__docformat__ = 'restructuredtext en'
__all__ = ('GearSetFEModel',)


class GearSetFEModel(_1175.GearSetImplementationDetail):
    '''GearSetFEModel

    This is a mastapy class.
    '''

    TYPE = _GEAR_SET_FE_MODEL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearSetFEModel.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def number_of_coupled_teeth_either_side(self) -> 'int':
        '''int: 'NumberOfCoupledTeethEitherSide' is the original name of this property.'''

        return self.wrapped.NumberOfCoupledTeethEitherSide

    @number_of_coupled_teeth_either_side.setter
    def number_of_coupled_teeth_either_side(self, value: 'int'):
        self.wrapped.NumberOfCoupledTeethEitherSide = int(value) if value else 0

    @property
    def element_order(self) -> '_55.ElementOrder':
        '''ElementOrder: 'ElementOrder' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.ElementOrder)
        return constructor.new(_55.ElementOrder)(value) if value is not None else None

    @element_order.setter
    def element_order(self, value: '_55.ElementOrder'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.ElementOrder = value

    @property
    def comment(self) -> 'str':
        '''str: 'Comment' is the original name of this property.'''

        return self.wrapped.Comment

    @comment.setter
    def comment(self, value: 'str'):
        self.wrapped.Comment = str(value) if value else ''

    @property
    def mesh_fe_models(self) -> 'List[_1145.GearMeshFEModel]':
        '''List[GearMeshFEModel]: 'MeshFEModels' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.MeshFEModels, constructor.new(_1145.GearMeshFEModel))
        return value

    @property
    def gear_fe_models(self) -> 'List[_1144.GearFEModel]':
        '''List[GearFEModel]: 'GearFEModels' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.GearFEModels, constructor.new(_1144.GearFEModel))
        return value

    def generate_stiffness_from_fe(self):
        ''' 'GenerateStiffnessFromFE' is the original name of this method.'''

        self.wrapped.GenerateStiffnessFromFE()

    def generate_stress_influence_coefficients_from_fe(self):
        ''' 'GenerateStressInfluenceCoefficientsFromFE' is the original name of this method.'''

        self.wrapped.GenerateStressInfluenceCoefficientsFromFE()

    def calculate_stiffness_from_fe(self):
        ''' 'CalculateStiffnessFromFE' is the original name of this method.'''

        self.wrapped.CalculateStiffnessFromFE()

    def calculate_stiffness_from_fe_with_progress(self, progress: '_7275.TaskProgress'):
        ''' 'CalculateStiffnessFromFE' is the original name of this method.

        Args:
            progress (mastapy.TaskProgress)
        '''

        self.wrapped.CalculateStiffnessFromFE.Overloads[_TASK_PROGRESS](progress.wrapped if progress else None)

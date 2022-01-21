'''_1168.py

GearMeshImplementationAnalysisDutyCycle
'''


from mastapy.gears.analysis import _1166
from mastapy._internal.python_net import python_net_import

_GEAR_MESH_IMPLEMENTATION_ANALYSIS_DUTY_CYCLE = python_net_import('SMT.MastaAPI.Gears.Analysis', 'GearMeshImplementationAnalysisDutyCycle')


__docformat__ = 'restructuredtext en'
__all__ = ('GearMeshImplementationAnalysisDutyCycle',)


class GearMeshImplementationAnalysisDutyCycle(_1166.GearMeshDesignAnalysis):
    '''GearMeshImplementationAnalysisDutyCycle

    This is a mastapy class.
    '''

    TYPE = _GEAR_MESH_IMPLEMENTATION_ANALYSIS_DUTY_CYCLE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearMeshImplementationAnalysisDutyCycle.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

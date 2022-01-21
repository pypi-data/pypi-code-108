'''_3812.py

CylindricalGearGeometricEntityDrawStyle
'''


from mastapy.system_model.analyses_and_results.power_flows import _3854
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_GEOMETRIC_ENTITY_DRAW_STYLE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows', 'CylindricalGearGeometricEntityDrawStyle')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearGeometricEntityDrawStyle',)


class CylindricalGearGeometricEntityDrawStyle(_3854.PowerFlowDrawStyle):
    '''CylindricalGearGeometricEntityDrawStyle

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_GEOMETRIC_ENTITY_DRAW_STYLE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearGeometricEntityDrawStyle.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

'''_2481.py

CylindricalGearSystemDeflectionTimestep
'''


from mastapy.system_model.analyses_and_results.system_deflections import _2480
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_SYSTEM_DEFLECTION_TIMESTEP = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections', 'CylindricalGearSystemDeflectionTimestep')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearSystemDeflectionTimestep',)


class CylindricalGearSystemDeflectionTimestep(_2480.CylindricalGearSystemDeflection):
    '''CylindricalGearSystemDeflectionTimestep

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_SYSTEM_DEFLECTION_TIMESTEP

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearSystemDeflectionTimestep.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

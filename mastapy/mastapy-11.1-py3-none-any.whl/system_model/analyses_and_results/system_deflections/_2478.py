'''_2478.py

CylindricalGearSetSystemDeflectionTimestep
'''


from mastapy.system_model.analyses_and_results.system_deflections import _2477
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_SET_SYSTEM_DEFLECTION_TIMESTEP = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections', 'CylindricalGearSetSystemDeflectionTimestep')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearSetSystemDeflectionTimestep',)


class CylindricalGearSetSystemDeflectionTimestep(_2477.CylindricalGearSetSystemDeflection):
    '''CylindricalGearSetSystemDeflectionTimestep

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_SET_SYSTEM_DEFLECTION_TIMESTEP

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearSetSystemDeflectionTimestep.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

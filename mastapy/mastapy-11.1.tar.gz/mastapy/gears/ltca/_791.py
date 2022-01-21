'''_791.py

CylindricalGearRootFilletStressResults
'''


from mastapy.gears.ltca import _805
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_ROOT_FILLET_STRESS_RESULTS = python_net_import('SMT.MastaAPI.Gears.LTCA', 'CylindricalGearRootFilletStressResults')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearRootFilletStressResults',)


class CylindricalGearRootFilletStressResults(_805.GearRootFilletStressResults):
    '''CylindricalGearRootFilletStressResults

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_ROOT_FILLET_STRESS_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearRootFilletStressResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

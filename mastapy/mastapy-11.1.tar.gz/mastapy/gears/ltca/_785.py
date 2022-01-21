'''_785.py

ConicalGearFilletStressResults
'''


from mastapy.gears.ltca import _797
from mastapy._internal.python_net import python_net_import

_CONICAL_GEAR_FILLET_STRESS_RESULTS = python_net_import('SMT.MastaAPI.Gears.LTCA', 'ConicalGearFilletStressResults')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalGearFilletStressResults',)


class ConicalGearFilletStressResults(_797.GearFilletNodeStressResults):
    '''ConicalGearFilletStressResults

    This is a mastapy class.
    '''

    TYPE = _CONICAL_GEAR_FILLET_STRESS_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalGearFilletStressResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

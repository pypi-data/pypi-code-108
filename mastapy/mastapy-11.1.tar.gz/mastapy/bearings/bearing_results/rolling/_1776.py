'''_1776.py

LoadedNonBarrelRollerElement
'''


from mastapy._internal import constructor
from mastapy.bearings.bearing_results.rolling import _1777
from mastapy._internal.python_net import python_net_import

_LOADED_NON_BARREL_ROLLER_ELEMENT = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'LoadedNonBarrelRollerElement')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedNonBarrelRollerElement',)


class LoadedNonBarrelRollerElement(_1777.LoadedRollerBearingElement):
    '''LoadedNonBarrelRollerElement

    This is a mastapy class.
    '''

    TYPE = _LOADED_NON_BARREL_ROLLER_ELEMENT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedNonBarrelRollerElement.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def minimum_smt_rib_stress_safety_factor(self) -> 'float':
        '''float: 'MinimumSMTRibStressSafetyFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumSMTRibStressSafetyFactor

'''_1753.py

LoadedCrossedRollerBearingElement
'''


from mastapy.bearings.bearing_results.rolling import _1777
from mastapy._internal.python_net import python_net_import

_LOADED_CROSSED_ROLLER_BEARING_ELEMENT = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'LoadedCrossedRollerBearingElement')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedCrossedRollerBearingElement',)


class LoadedCrossedRollerBearingElement(_1777.LoadedRollerBearingElement):
    '''LoadedCrossedRollerBearingElement

    This is a mastapy class.
    '''

    TYPE = _LOADED_CROSSED_ROLLER_BEARING_ELEMENT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedCrossedRollerBearingElement.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

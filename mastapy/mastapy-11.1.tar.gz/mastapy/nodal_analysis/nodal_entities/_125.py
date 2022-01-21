'''_125.py

BearingAxialMountingClearance
'''


from mastapy.nodal_analysis.nodal_entities import _120
from mastapy._internal.python_net import python_net_import

_BEARING_AXIAL_MOUNTING_CLEARANCE = python_net_import('SMT.MastaAPI.NodalAnalysis.NodalEntities', 'BearingAxialMountingClearance')


__docformat__ = 'restructuredtext en'
__all__ = ('BearingAxialMountingClearance',)


class BearingAxialMountingClearance(_120.ArbitraryNodalComponent):
    '''BearingAxialMountingClearance

    This is a mastapy class.
    '''

    TYPE = _BEARING_AXIAL_MOUNTING_CLEARANCE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BearingAxialMountingClearance.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

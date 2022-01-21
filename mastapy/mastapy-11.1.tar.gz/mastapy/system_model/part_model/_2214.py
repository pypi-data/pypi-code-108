'''_2214.py

RadialInternalClearanceTolerance
'''


from mastapy.system_model.part_model import _2200
from mastapy._internal.python_net import python_net_import

_RADIAL_INTERNAL_CLEARANCE_TOLERANCE = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'RadialInternalClearanceTolerance')


__docformat__ = 'restructuredtext en'
__all__ = ('RadialInternalClearanceTolerance',)


class RadialInternalClearanceTolerance(_2200.InternalClearanceTolerance):
    '''RadialInternalClearanceTolerance

    This is a mastapy class.
    '''

    TYPE = _RADIAL_INTERNAL_CLEARANCE_TOLERANCE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RadialInternalClearanceTolerance.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

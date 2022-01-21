'''_2181.py

AxialInternalClearanceTolerance
'''


from mastapy.system_model.part_model import _2200
from mastapy._internal.python_net import python_net_import

_AXIAL_INTERNAL_CLEARANCE_TOLERANCE = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'AxialInternalClearanceTolerance')


__docformat__ = 'restructuredtext en'
__all__ = ('AxialInternalClearanceTolerance',)


class AxialInternalClearanceTolerance(_2200.InternalClearanceTolerance):
    '''AxialInternalClearanceTolerance

    This is a mastapy class.
    '''

    TYPE = _AXIAL_INTERNAL_CLEARANCE_TOLERANCE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AxialInternalClearanceTolerance.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

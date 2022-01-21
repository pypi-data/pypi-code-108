'''_1490.py

StiffnessPerUnitFaceWidth
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_STIFFNESS_PER_UNIT_FACE_WIDTH = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'StiffnessPerUnitFaceWidth')


__docformat__ = 'restructuredtext en'
__all__ = ('StiffnessPerUnitFaceWidth',)


class StiffnessPerUnitFaceWidth(_1398.MeasurementBase):
    '''StiffnessPerUnitFaceWidth

    This is a mastapy class.
    '''

    TYPE = _STIFFNESS_PER_UNIT_FACE_WIDTH

    __hash__ = None

    def __init__(self, instance_to_wrap: 'StiffnessPerUnitFaceWidth.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

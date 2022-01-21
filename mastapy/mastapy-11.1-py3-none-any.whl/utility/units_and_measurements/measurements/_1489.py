'''_1489.py

SquareRootOfUnitForcePerUnitArea
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_SQUARE_ROOT_OF_UNIT_FORCE_PER_UNIT_AREA = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'SquareRootOfUnitForcePerUnitArea')


__docformat__ = 'restructuredtext en'
__all__ = ('SquareRootOfUnitForcePerUnitArea',)


class SquareRootOfUnitForcePerUnitArea(_1398.MeasurementBase):
    '''SquareRootOfUnitForcePerUnitArea

    This is a mastapy class.
    '''

    TYPE = _SQUARE_ROOT_OF_UNIT_FORCE_PER_UNIT_AREA

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SquareRootOfUnitForcePerUnitArea.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

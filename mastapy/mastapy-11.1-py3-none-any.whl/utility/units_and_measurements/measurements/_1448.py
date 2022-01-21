'''_1448.py

KinematicViscosity
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_KINEMATIC_VISCOSITY = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'KinematicViscosity')


__docformat__ = 'restructuredtext en'
__all__ = ('KinematicViscosity',)


class KinematicViscosity(_1398.MeasurementBase):
    '''KinematicViscosity

    This is a mastapy class.
    '''

    TYPE = _KINEMATIC_VISCOSITY

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KinematicViscosity.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

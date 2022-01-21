'''_7277.py

MeasurementTypeExtensions
'''


from mastapy.units_and_measurements import _7276
from mastapy._internal import conversion, constructor
from mastapy._internal.python_net import python_net_import

_MEASUREMENT_TYPE_EXTENSIONS = python_net_import('SMT.MastaAPIUtility.UnitsAndMeasurements', 'MeasurementTypeExtensions')


__docformat__ = 'restructuredtext en'
__all__ = ('MeasurementTypeExtensions',)


class MeasurementTypeExtensions:
    '''MeasurementTypeExtensions

    This is a mastapy class.
    '''

    TYPE = _MEASUREMENT_TYPE_EXTENSIONS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MeasurementTypeExtensions.TYPE'):
        self.wrapped = instance_to_wrap

    @staticmethod
    def is_unmeasurable(measurement_type: '_7276.MeasurementType') -> 'bool':
        ''' 'IsUnmeasurable' is the original name of this method.

        Args:
            measurement_type (mastapy.units_and_measurements.MeasurementType)

        Returns:
            bool
        '''

        measurement_type = conversion.mp_to_pn_enum(measurement_type)
        method_result = MeasurementTypeExtensions.TYPE.IsUnmeasurable(measurement_type)
        return method_result

    @staticmethod
    def is_valid(measurement_type: '_7276.MeasurementType') -> 'bool':
        ''' 'IsValid' is the original name of this method.

        Args:
            measurement_type (mastapy.units_and_measurements.MeasurementType)

        Returns:
            bool
        '''

        measurement_type = conversion.mp_to_pn_enum(measurement_type)
        method_result = MeasurementTypeExtensions.TYPE.IsValid(measurement_type)
        return method_result

    @staticmethod
    def is_angle(measurement_type: '_7276.MeasurementType') -> 'bool':
        ''' 'IsAngle' is the original name of this method.

        Args:
            measurement_type (mastapy.units_and_measurements.MeasurementType)

        Returns:
            bool
        '''

        measurement_type = conversion.mp_to_pn_enum(measurement_type)
        method_result = MeasurementTypeExtensions.TYPE.IsAngle(measurement_type)
        return method_result

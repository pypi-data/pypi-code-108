'''_1561.py

OperationMode
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_OPERATION_MODE = python_net_import('SMT.MastaAPI.Utility.OperationModes', 'OperationMode')


__docformat__ = 'restructuredtext en'
__all__ = ('OperationMode',)


class OperationMode(Enum):
    '''OperationMode

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _OPERATION_MODE

    __hash__ = None

    UNKNOWN = 0
    DESIGN = 1
    LOAD_CASES_AND_DUTY_CYCLES = 2
    PRODUCT_DATABASE = 3
    FE_PARTS = 4
    POWER_FLOW = 5
    SYSTEM_DEFLECTION = 6
    ADVANCED_SYSTEM_DEFLECTION = 7
    HARMONIC_RESPONSE = 8
    NVH_ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION = 9
    ROTOR_DYNAMICS = 10
    PARAMETRIC_STUDY_TOOL = 11
    GEAR_MACRO_GEOMETRY = 12
    GEAR_MICRO_GEOMETRY = 13
    CYLINDRICAL_GEAR_MANUFACTURING = 14
    BEVEL_GEAR_MANUFACTURING = 15
    CYCLOIDAL_DESIGN = 16
    DRIVA_LOAD_CASE_SETUP = 17
    DRIVA = 18
    BENCHMARKING = 19
    SYNCHRONISER_SHIFT_ANALYSIS = 20
    FLEXIBLE_PIN_ANALYSIS = 21
    MES = 22


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


OperationMode.__setattr__ = __enum_setattr
OperationMode.__delattr__ = __enum_delattr

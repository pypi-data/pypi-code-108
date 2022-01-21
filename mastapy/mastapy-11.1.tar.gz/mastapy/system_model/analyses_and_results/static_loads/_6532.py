'''_6532.py

AnalysisType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_ANALYSIS_TYPE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'AnalysisType')


__docformat__ = 'restructuredtext en'
__all__ = ('AnalysisType',)


class AnalysisType(Enum):
    '''AnalysisType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _ANALYSIS_TYPE

    __hash__ = None

    NONE = 0
    SYSTEM_DEFLECTION = 1
    POWER_FLOW = 2
    ADVANCED_SYSTEM_DEFLECTION = 3
    HARMONIC_ANALYSIS = 4
    MULTIBODY_DYNAMICS_ANALYSIS = 5
    PARAMETRIC_STUDY_TOOL = 6
    COMPOUND_PARAMETRIC_STUDY_TOOL = 7
    STEADY_STATE_SYNCHRONOUS_RESPONSE = 8
    STEADY_STATE_SYNCHRONOUS_RESPONSE_AT_A_SPEED = 9
    STEADY_STATE_SYNCHRONOUS_RESPONSE_ON_A_SHAFT = 10
    MODAL_ANALYSIS = 11
    DYNAMIC_ANALYSIS = 12
    CRITICAL_SPEED_ANALYSIS = 13
    STABILITY_ANALYSIS = 14
    MODAL_ANALYSIS_AT_A_SPEED = 15
    MODAL_ANALYSIS_AT_A_STIFFNESS = 16
    TORSIONAL_SYSTEM_DEFLECTION = 17
    HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION = 18
    ADVANCED_SYSTEM_DEFLECTION_SUB_ANALYSIS = 19
    DYNAMIC_MODEL_FOR_HARMONIC_ANALYSIS = 20
    DYNAMIC_MODEL_FOR_STABILITY_ANALYSIS = 21
    DYNAMIC_MODEL_AT_A_STIFFNESS = 22
    DYNAMIC_MODEL_FOR_STEADY_STATE_SYNCHRONOUS_RESPONSE = 23
    MODAL_ANALYSIS_FOR_HARMONIC_ANALYSIS = 24
    ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION = 25
    HARMONIC_ANALYSIS_FOR_ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION = 26
    DYNAMIC_MODEL_FOR_MODAL_ANALYSIS = 27


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


AnalysisType.__setattr__ = __enum_setattr
AnalysisType.__delattr__ = __enum_delattr

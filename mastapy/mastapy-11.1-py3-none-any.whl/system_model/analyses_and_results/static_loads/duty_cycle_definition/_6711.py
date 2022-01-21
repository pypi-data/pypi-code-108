'''_6711.py

ForceInputOptions
'''


from mastapy.system_model.analyses_and_results.static_loads.duty_cycle_definition import _6716
from mastapy._internal.python_net import python_net_import

_FORCE_INPUT_OPTIONS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads.DutyCycleDefinition', 'ForceInputOptions')


__docformat__ = 'restructuredtext en'
__all__ = ('ForceInputOptions',)


class ForceInputOptions(_6716.PointLoadInputOptions):
    '''ForceInputOptions

    This is a mastapy class.
    '''

    TYPE = _FORCE_INPUT_OPTIONS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ForceInputOptions.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

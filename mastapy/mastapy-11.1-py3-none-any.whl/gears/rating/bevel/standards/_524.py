'''_524.py

SpiralBevelRateableMesh
'''


from mastapy._internal import constructor
from mastapy.gears.rating.agma_gleason_conical import _528
from mastapy._internal.python_net import python_net_import

_SPIRAL_BEVEL_RATEABLE_MESH = python_net_import('SMT.MastaAPI.Gears.Rating.Bevel.Standards', 'SpiralBevelRateableMesh')


__docformat__ = 'restructuredtext en'
__all__ = ('SpiralBevelRateableMesh',)


class SpiralBevelRateableMesh(_528.AGMAGleasonConicalRateableMesh):
    '''SpiralBevelRateableMesh

    This is a mastapy class.
    '''

    TYPE = _SPIRAL_BEVEL_RATEABLE_MESH

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SpiralBevelRateableMesh.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def safety_factor_scoring(self) -> 'float':
        '''float: 'SafetyFactorScoring' is the original name of this property.'''

        return self.wrapped.SafetyFactorScoring

    @safety_factor_scoring.setter
    def safety_factor_scoring(self, value: 'float'):
        self.wrapped.SafetyFactorScoring = float(value) if value else 0.0

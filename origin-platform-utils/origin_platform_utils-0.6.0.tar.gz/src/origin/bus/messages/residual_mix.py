from dataclasses import dataclass

from origin.bus import Message
from origin.models.residual_mix import \
    ResidualMixEmissions, ResidualMixTechnologyDistribution


@dataclass
class ResidualMixEmissionsUpdate(Message):
    """
    TODO
    """
    emissions: ResidualMixEmissions


@dataclass
class ResidualMixTechnologyDistributionUpdate(Message):
    """
    TODO
    """
    distributions: ResidualMixTechnologyDistribution

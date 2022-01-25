from typing import List
from datetime import datetime
from dataclasses import dataclass

from origin.serialize import Serializable
from origin.models.tech import TechnologyType

from .emissions import EmissionValues


# -- Residual Mix emissions --------------------------------------------------


@dataclass
class ResidualMixEmissions(Serializable):
    """
    Describes emissions in the general mix within a single
    sector (pricing area), and in a specific time-frame.
    """

    # Sector where energy is consumed
    sector: str

    # The time-frame where the distribution is valid.
    # TODO Is 'end' included or excluded in the period?
    begin: datetime
    end: datetime

    # Relative emissions (gram/Wh)
    emissions: EmissionValues


# -- Residual Mix technologies -----------------------------------------------


@dataclass
class ResidualMixTechnology(Serializable):
    """
    Describes a part of the residual mix consumption, specifically
    how large a percentage of the total energy consumed originates
    from a single type of technology.
    """
    technology: TechnologyType
    percent: float
    sector: str  # Sector where energy is produced


@dataclass
class ResidualMixTechnologyDistribution(Serializable):
    """
    Describes the distribution of technologies used to produce energy
    in the residual mix within a single sector (pricing area),
    and in a specific time-frame.
    """

    # Sector where energy is consumed
    sector: str

    # The time-frame where the distribution is valid.
    # TODO Is 'end' included or excluded in the period?
    begin: datetime
    end: datetime

    # Distribution of produced energy on technologies.
    # The list is unique on (technology, sector) (composite key).
    # The sum of ResidualMixTechnology.percent MUST be exactly 1.0.
    technologies: List[ResidualMixTechnology]

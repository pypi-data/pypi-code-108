from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.config.simulation.profile import ProfileConfig
from simses.commons.profile.power.file import FilePowerProfile


class LoadProfile(FilePowerProfile):
    """
    LoadProfile is a specific implementation of FilePowerProfile. It reads a file with a power and time series.
    Values with a positive sign are recognized as a load for the system.

    LoadProfiles require a specific header at the top of the file:\n
    # Annual load consumption in kWh: [Value]
    """

    ANNUAL_CONSUMPTION: str = 'Annual load consumption in kWh'
    """Header of load profile for scaling power values"""

    def __init__(self, profile_config: ProfileConfig, general_config: GeneralSimulationConfig):
        super().__init__(general_config, profile_config.load_profile,
                         scaling_factor=profile_config.load_scaling_factor)

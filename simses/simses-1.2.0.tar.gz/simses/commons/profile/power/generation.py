from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.config.simulation.profile import ProfileConfig
from simses.commons.profile.power.file import FilePowerProfile


class GenerationProfile(FilePowerProfile):
    """
    GenerationProfile is a specific implementation of FilePowerProfile. It reads a file with a power and time series.
    Values with a positive sign are recognized as a generation for the system.

    GenerationProfile require a specific header at the top of the file:\n
    # Nominal power in kWp: [Value]
    """

    PEAK_POWER: str = 'Nominal power in kWp'
    """Header of generation profile for scaling power values"""

    def __init__(self, profile_config: ProfileConfig, general_config: GeneralSimulationConfig):
        super().__init__(general_config, profile_config.generation_profile_file,
                         scaling_factor=profile_config.generation_scaling_factor)

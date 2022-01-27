from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.profile.file import FileProfile
from simses.commons.profile.power.power_profile import PowerProfile


class FilePowerProfile(PowerProfile):
    """
    FilePowerProfile is a generic implementation of a PowerProfile. It provides power values from a file using
    FileProfile library.
    """

    class Header:
        ANNUAL_CONSUMPTION: str = 'Annual load consumption in kWh'
        PEAK_POWER: str = 'Nominal power in kWp'

    def __init__(self, config: GeneralSimulationConfig, filename: str, delimiter: str = ',', scaling_factor: float = 1.0):
        """
        Constructor of FilePowerProfile

        Parameters
        ----------
        config :
            simulation configuration
        filename :
            path to file
        delimiter :
            delimter of values in file, default: ,
        scaling_factor :
            linear scaling of values, default: 1
        """
        super().__init__()
        self.__file: FileProfile = FileProfile(config, filename, delimiter, scaling_factor)

    def next(self, time: float) -> float:
        return self.__file.next(time)

    def profile_data_to_list(self, sign_factor=1) -> [float]:
        """
        Extracts the whole time series as a list and resets the pointer of the (internal) file afterwards

        Parameters
        ----------
        sign_factor :

        Returns
        -------
        list:
            profile values as a list

        """
        time, values = self.__file.profile_data_to_list(sign_factor)
        return values

    def close(self):
        self.__file.close()

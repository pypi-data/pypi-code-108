from simses.commons.profile.file import FileProfile
from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.config.simulation.profile import ProfileConfig
from simses.commons.profile.technical.technical import TechnicalProfile
import numpy as np

class BinaryProfile(TechnicalProfile):
    """
    BinaryProfile is a subclass of TechnicalProfile (like SocProfile). The binary profile should contain a timestep and
    a binary profile (0 or 1). This class is used for temporary unavailable storage systems, e.g. mobile applications
    like electric vehicles. Here zeros indicate that the car is on the road respectively not "at home" and ones indicate
    that the car is "at home" and could be charged.
    """

    def __init__(self, config: GeneralSimulationConfig, profile_config: ProfileConfig):
        super().__init__()
        self.__file: FileProfile = FileProfile(config, profile_config.binary_profile_file, delimiter=',')

        self.__temp: FileProfile = FileProfile(config, profile_config.binary_profile_file, delimiter=',')
        self.data = self.__temp.profile_data_to_list()
        self.time_profile = self.data[0]
        self.binary_profile = np.round(self.data[1])

    def next(self, time: float) -> float:
        return self.__file.next(time)

    def next_zero(self, time: float) -> float:

        time_idx= self.time_profile.index(time)
        binary_profile_fromidx=self.binary_profile[time_idx:]
        time_profile_fromidx= self.time_profile[time_idx:]
        try:
            nextzero=np.where(binary_profile_fromidx == 0)[0][0]
            return time_profile_fromidx[nextzero]
        except IndexError as error:
            print(' no zero elements found in binary profile')

    def close(self):
        self.__file.close()
        self.__temp.close()
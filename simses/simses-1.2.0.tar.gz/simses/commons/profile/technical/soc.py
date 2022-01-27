from simses.commons.profile.file import FileProfile
from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.config.simulation.profile import ProfileConfig
from simses.commons.profile.technical.technical import TechnicalProfile


class SocProfile(TechnicalProfile):

    def __init__(self, config: GeneralSimulationConfig, profile_config: ProfileConfig):
        super().__init__()
        self.__file: FileProfile = FileProfile(config, profile_config.soc_file, delimiter=',',
                                               value_index=profile_config.soc_file_value)

    def next(self, time: float) -> float:
        return self.__file.next(time)

    def close(self):
        self.__file.close()

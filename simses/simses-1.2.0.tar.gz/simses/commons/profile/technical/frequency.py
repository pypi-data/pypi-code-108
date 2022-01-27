from simses.commons.profile.file import FileProfile
from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.config.simulation.profile import ProfileConfig
from simses.commons.profile.technical.technical import TechnicalProfile


class FrequencyProfile(TechnicalProfile):

    def __init__(self, config: GeneralSimulationConfig, profile_config: ProfileConfig):
        super().__init__()
        self.__file: FileProfile = FileProfile(config, profile_config.frequency_file)
        #self.__file = open(profile_config.frequency_file, 'r', newline='')
        #self.__header_missing_exception = False
        #self.__first_line = None
        #self.__header_length = None
        #self.__header = self.get_header()
        # TODO Fix imported get header function:
        # self.__header = get_header_from(profile_config.frequency_file)

    def next(self, time) -> float:
        # Handling of profile files with and without header
        #if self.__header_missing_exception is True:
        #    __frequency = self.__first_line
        #    self.__header_missing_exception = False
        #else:
        #    __frequency = self.__file.readline()
        #return float(__frequency)
        return self.__file.next(time)

    #def get_header(self) -> dict:
    #   """
    #   Analyzes the header structure and saves it into a dict.
    #   Furthermore sets the __header_length parameter.
    #
    #   Returns
    #   -------
    #   dict
    #       Containing the header parameters and their values.
    #   """
    #
    #   __header = {}
    #   __line = self.__file.readline()
    #   __line_count = 1
    #   if __line not in ['"""\r\n']:
    #       self.__header_missing_exception = True
    #       self.__first_line = __line
    #       __header = None
    #   else:
    #       while __line not in ['\r\n']:
    #           if '#' in __line:
    #               key_raw, entry_raw = __line.split(sep=':', maxsplit=1)
    #               key = key_raw.strip('# ')
    #               entry = entry_raw.strip()
    #               __header[key] = entry
    #           __line = self.__file.readline()
    #           __line_count += 1
    #       self.__header_length = __line_count
    #   return __header

    def close(self):
        self.__file.close()

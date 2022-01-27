import gzip
import os
import sys
from datetime import datetime
from os.path import basename
from pytz import timezone
from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.error import EndOfFileError
from simses.commons.log import Logger
from simses.commons.timeseries.average.average import Average
from simses.commons.timeseries.average.mean_average import MeanAverage
from simses.commons.timeseries.interpolation.interpolation import Interpolation
from simses.commons.timeseries.interpolation.linear_interpolation import LinearInterpolation
from simses.commons.timeseries.timevalue import TimeValue
from simses.commons.utils.utilities import download_file


class FileProfile:
    """
    FileProfile is able to read time series from a file. It supports several unit and date formats, takes timezones into
    consideration (default: Berlin) and interpolates respectively averages values of the given time series. If no time series
    is given, a time generator generates the timestep according to the given sampling rate or simulation timestep.

    A header could inherit the given timezone, value unit, time unit and sampling rate:\n
    # Unit: W\n
    # Timezone: Berlin\n
    # Time: s\n
    # Sampling in s: 3600s\n
    """

    class Header:
        TIMEZONE: str = 'Timezone'
        UNIT: str = 'Unit'
        TIME: str = 'Time'
        SAMPLING: str = 'Sampling in s'
        LATITUDE: str = 'Latitude'
        LONGITUDE: str = 'Longitude'

    __UNITS: dict = {'W': 1, 'kW': 1e3, 'MW': 1e6, 'GW': 1e9, 's': 1, 'ms': 0.001, 'EUR': 1, 'TEUR': 1e3, 'Hz': 1, '%': 0.01, 'W/m2': 1, 'C': 1}
    """List of recognized unit formats of FileProfile"""

    __TIME_IDX: int = 0

    __EPOCH_FORMAT: str = 'epoch'
    __DATE_FORMATS: [str] = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%d.%m.%Y %H:%M:%S', '%d.%m.%Y %H:%M',
                             __EPOCH_FORMAT]
    """List of supported date formats"""

    __UTC: timezone = timezone('UTC')
    __BERLIN: timezone = timezone('Europe/Berlin')

    __EXT_GZIP: str = '.gz'
    __EXT_CSV: str = '.csv'
    __SUPPORTED_EXTENSIONS: [str] = list()
    __SUPPORTED_EXTENSIONS.append(__EXT_CSV + __EXT_GZIP)
    __SUPPORTED_EXTENSIONS.append(__EXT_GZIP)
    __SUPPORTED_EXTENSIONS.append(__EXT_CSV)

    __ERROR = None

    __URL: str = 'https://syncandshare.lrz.de/dl/fiDZgUQ5uygrVfHTwa7BxiEZ/Profile/'
    """URL to folder of profiles to download"""

    def __init__(self, config: GeneralSimulationConfig, filename: str, delimiter: str = ',', scaling_factor: float = 1,
                 value_index: int = 1, interpolation: Interpolation = LinearInterpolation(),
                 average: Average = MeanAverage()):
        """
        Constructor of FileProfile

        Parameters
        ----------
        config :
            simulation configuration
        filename :
            path to file
        delimiter :
            delimiter of values in file, default: ,
        scaling_factor :
            linear scaling of values, default: 1
        value_index :
            column index for values, default: 1
        interpolation:
            provides an Interpolation object, default: LinearInterpolation
        average:
            provides an Average object, default: MeanAverage
        """
        self.__log: Logger = Logger(type(self).__name__)
        self.__log.info('Preparing ' + filename)
        self.__filename: str = filename
        self.__delimiter: str = delimiter
        self.__scaling_factor: float = scaling_factor
        self.__VALUE_IDX: int = value_index
        self.__timestep: float = config.timestep
        self.__start: float = config.start
        self.__end: float = config.end
        self.__time_offset: int = 0
        self.__file = None
        self.__date_format = None
        self.__last_data: [TimeValue] = list()
        self.__last_time: float = self.__start
        self.__interpolation: Interpolation = interpolation
        self.__average: Average = average
        header: dict = self.get_header_from(self.__filename)
        self.__unit_factor: float = self.__get_value_unit_from(header)
        self.__time_factor: float = self.__get_time_unit_from(header)
        self.__timezone: timezone = self.__get_timezone_from(header)
        self.__sampling_time: float = self.__get_sampling_time_from(header)
        self.__time_generator = self.__get_sampling_time_generator()
        self.__latitude: float = self.__get_latitude_from(header)
        self.__longitude: float = self.__get_longitude_from(header)
        self.initialize_file()

    def next(self, time: float) -> float:
        """
        Retrieves the next value for given time from file time series

        Parameters
        ----------
        time :
            time as epoch timestamp

        Returns
        -------
        float :
            (interpolated/averaged) value for given time
        """
        try:
            data: [TimeValue] = self.__get_data_until(time)
            values: [TimeValue] = self.__filter_current_values(time, data)
            if not values and len(data) < 2:
                value: float = self.__average.average(data)
            elif not values:
                value: float = self.__interpolation.interpolate(time, data[-1], data[-2])
            else:
                value: float = self.__average.average(values)
            self.__last_data = self.__filter_last_values(data)
            self.__last_time = time
            return value * self.__scaling_factor
        except EndOfFileError as err:
            self.__log.warn(str(err))
            return 0.0

    def initialize_file(self) -> None:
        """
        Allows to re-initialize the profile to start reading values from the beginning again
        """
        if self.__file is not None:
            if not self.__file.closed:
                self.__file.close()
        self.__file = self.open_file(self.__filename)
        self.__last_data = self.__get_initial_data()

    @classmethod
    def open_file(cls, filename: str):
        """
        Opens file with filename depending on the file type. Currently .gz and .csv are supported.
        The file type extension is added if necessary.

        Parameters
        ----------
        filename :
            path to file

        Returns
        -------
            file object (needs to be closed manually)
        """
        filename: str = cls.__add_extension_to(filename)
        try:
            if filename.endswith(cls.__EXT_GZIP):
                return gzip.open(filename, 'rt')
            elif filename.endswith(cls.__EXT_CSV):
                return open(filename, 'r', newline='')
            else:
                raise FileNotFoundError('Format of ' + filename + ' is currently not supported. Please check your '
                                            'file type. Following file types are supported: ' + str(cls.__SUPPORTED_EXTENSIONS))
        except FileNotFoundError as err:
            if cls.__URL is cls.__ERROR:
                raise err
            print(filename + ' is not available. Searching for file on server...')
            if cls.__profile_downloaded(filename):
                return cls.open_file(filename)
            else:
                raise FileNotFoundError(basename(filename) + ' is currently not available for download.', err)

    @classmethod
    def __profile_downloaded(cls, filename: str) -> bool:
        found: bool = False
        for file in cls.__possible_file_names(filename):
            try:
                download_file(cls.__URL + basename(file), file)
                found = True
                break
            except FileNotFoundError:
                print(basename(file) + ' could not be found on server')
        return found

    @classmethod
    def __possible_file_names(cls, filename: str) -> [str]:
        possible_file_names: [str] = list()
        if cls.__has_extension(filename):
            possible_file_names.append(filename)
        else:
            for extension in cls.__SUPPORTED_EXTENSIONS:
                possible_file_names.append(filename + extension)
        return possible_file_names

    @classmethod
    def __has_extension(cls, filename: str) -> bool:
        has_extension: bool = False
        for extension in cls.__SUPPORTED_EXTENSIONS:
            has_extension |= filename.endswith(extension)
        return has_extension

    @classmethod
    def __add_extension_to(cls, filename: str) -> str:
        has_extension: bool = cls.__has_extension(filename)
        if not has_extension:
            for extension in cls.__SUPPORTED_EXTENSIONS:
                if os.path.isfile(filename + extension):
                    filename += extension
                    break
        return filename

    def __filter_current_values(self, time: float, data: [TimeValue]) -> [TimeValue]:
        values: [TimeValue] = list()
        data_iterator = iter(data)
        try:
            while True:
                value = next(data_iterator)
                if self.__last_time < value.time <= time:
                    values.append(value)
        except StopIteration:
            pass
        return values

    def __filter_last_values(self, data: [TimeValue]) -> [TimeValue]:
        return data[-2:]
        # values: [TimeValue] = list()
        # data_iterator = iter(data)
        # try:
        #     while True:
        #         value = next(data_iterator)
        #         if self.__last_time < value.time:
        #             values.append(value)
        # except StopIteration:
        #     pass
        # return values

    def __get_data_until(self, time: float) -> [TimeValue]:
        values: list = list()
        data = self.__last_data[-1]
        while data.time < time:
            data = self.__get_next_data()
            values.append(data)
        values.extend(self.__last_data)
        TimeValue.sort_by_time(values)
        return values

    def __get_next_data(self) -> TimeValue:
        while True:
            line: str = ''
            try:
                line = self.__file.readline()
                if line.startswith('#') or line.startswith('"') or line in ['\r\n', '\n']:# or self.__delimiter not in line:
                    continue
                if line == '':  # end of file_name
                    raise EndOfFileError('End of Profile ' + self.__filename + ' reached.')
                data = line.split(self.__delimiter)
                if len(data) < 2:
                    time: float = next(self.__time_generator) + self.__time_offset
                    value: float = float(data[self.__VALUE_IDX - 1]) * self.__unit_factor
                else:
                    time: float = self.__format_time(data[self.__TIME_IDX]) * self.__time_factor + self.__time_offset
                    value: float = float(data[self.__VALUE_IDX]) * self.__unit_factor
                return TimeValue(time, value)
            except ValueError:
                self.__log.error('No value found for ' + line)

    def __get_sampling_time_generator(self):
        return self.__get_time_generator(self.__sampling_time)

    def __get_timestep_time_generator(self):
        return self.__get_time_generator(self.__timestep)

    def __get_time_generator(self, time_increment: float):
        time: float = self.__start
        while True:
            yield time
            time += time_increment

    def __format_time(self, time: str) -> float:
        if self.__date_format is None:
            self.__date_format = self.__find_date_format_for(time)
            self.__log.info('Found format: ' + str(self.__date_format))
        if self.__date_format == self.__EPOCH_FORMAT:
            return float(time)
        else:
            return self.__extract_timestamp_from(time, self.__date_format)

    def __find_date_format_for(self, time: str) -> str:
        for date_format in self.__DATE_FORMATS:
            try:
                if date_format == self.__EPOCH_FORMAT:
                    float(time)
                    return date_format
                else:
                    self.__extract_timestamp_from(time, date_format)
                    return date_format
            except ValueError:
                pass
        raise Exception('Unknown date format for ' + time)

    def __extract_timestamp_from(self, time: str, date_format: str) -> float:
        date: datetime = datetime.strptime(time, date_format)
        date = self.__get_local_datetime_from(date=date)
        return date.timestamp()

    def __get_local_datetime_from(self, date: datetime = None, tstmp: float = None) -> datetime:
        if date is None:
            if tstmp is None:
                tstmp = datetime.now()
            date = datetime.fromtimestamp(tstmp)
        return self.__timezone.localize(date, is_dst=None)

    def __get_initial_data(self) -> [TimeValue]:
        timestamp: float = self.__start
        data = self.__get_next_data()
        self.__set_time_offset(data.time, timestamp)
        data.time += self.__time_offset
        while data.time < timestamp:
            data = self.__get_next_data()
        return [data]

    def __set_time_offset(self, file_tstmp: float, simulation_tstmp: float) -> None:
        #Set profile year to simulation year
        file_date = self.__get_local_datetime_from(tstmp=file_tstmp)
        simulation_date = self.__get_local_datetime_from(tstmp=simulation_tstmp)
        if file_date.year == simulation_date.year:
            return
        adapted_file_tstmp = file_date.replace(year=simulation_date.year).timestamp()
        self.__time_offset = adapted_file_tstmp - file_tstmp
        if not self.__time_offset == 0:
            self.__log.warn('Time offset is ' + str(self.__time_offset) + ' s. \n'
                            'File time: ' + str(self.__get_local_datetime_from(tstmp=file_tstmp)) + ', \n'
                            'Simulation time: ' + str(self.__get_local_datetime_from(tstmp=simulation_tstmp)))

    def __get_timezone_from(self, header: dict) -> timezone:
        try:
            tz: str = header[self.Header.TIMEZONE]
            return timezone(tz)
        except KeyError:
            self.__log.warn('No timezone for profile is given, UTC timzone is assumed.')
            return self.__UTC

    def __get_latitude_from(self, header: dict) -> float:
        try:
            lat: str = header[self.Header.LATITUDE]
            return float(lat)
        except KeyError:
            return self.__ERROR

    def __get_longitude_from(self, header: dict) -> float:
        try:
            lon: str = header[self.Header.LONGITUDE]
            return float(lon)
        except KeyError:
            return self.__ERROR

    @classmethod
    def __get_unit_from(cls, header: dict, identifier: str) -> float:
        try:
            unit: str = header[identifier]
            return cls.__UNITS[unit]
        except KeyError:
            # print('Unit is unknown. Valid types are ' + str(cls.__UNITS.keys()) + '.')
            return 1.0

    @classmethod
    def __get_value_unit_from(self, header: dict) -> float:
        return self.__get_unit_from(header, self.Header.UNIT)

    @classmethod
    def __get_time_unit_from(cls, header: dict) -> float:
        return cls.__get_unit_from(header, cls.Header.TIME)

    def __get_sampling_time_from(self, header: dict) -> float:
        try:
            sampling_time: str = header[self.Header.SAMPLING]
            return float(sampling_time)
        except KeyError:
            return self.__timestep

    def profile_data_to_list(self, sign_factor=1) -> ([float], [float]):
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
        profile_data: [float] = list()
        time_data: [float] = list()
        time_generator = self.__get_timestep_time_generator()
        time: float = next(time_generator)
        while time <= self.__end:
            time_data.append(time)
            profile_data.append(self.next(time) * sign_factor)
            time = next(time_generator)
        self.initialize_file()
        return time_data, profile_data

    def get_latitude(self) -> float:
        """

        Returns
        -------
        float:
            Latitude value of profile location, raises an exception if not available
        """
        if self.__latitude is self.__ERROR:
            raise Exception('No latitude value given in profile. Please add the header for latitude.')
        return self.__latitude

    def get_longitude(self) -> float:
        """

        Returns
        -------
        float:
            Longitude value of profile location, raises an exception if not available
        """
        if self.__longitude is self.__ERROR:
            raise Exception('No longitude value given in profile. Please add the header for longitude.')
        return self.__longitude

    def get_timezone(self) -> timezone:
        """

        Returns
        -------
        float:
            timezone for profile location, raises an exception if not available
        """
        if self.__timezone is self.__ERROR:
            raise Exception('No timezone value given in profile. Please add the header for timezone.')
        return self.__timezone

    @classmethod
    def get_header_from(cls, filename: str) -> dict:
        """
        Extracts header from given file

        Attention: Only searches in the first ten lines for a header!

        Parameters
        ----------
        filename :

        Returns
        -------
        dict:
            header with key/value pairs

        """
        header: dict = dict()
        file = cls.open_file(filename)
        # with open(filename, 'r', newline='') as file:
        line = file.readline()
        line_count: int = 0
        while True:
            if '#' in line:
                try:
                    key_raw, entry_raw = line.split(sep=':', maxsplit=1)
                    key = key_raw.strip('# ')
                    entry = entry_raw.strip()
                    header[key] = entry
                except ValueError:
                    sys.stderr.write('WARNING: Could not interpret ' + line)
                    sys.stderr.flush()
            line = file.readline()
            if line_count > 20:
                break
            else:
                line_count += 1
        file.close()
        return header

    @classmethod
    def get_max_value_of(cls, filename: str, delimiter: str = ',', value_idx: int = 1, start: float = 0.0) -> float:
        """
        Searching for maximum value within given file

        Attention: This method could be very time consuming depending on the profile to read.

        Parameters
        ----------
        filename :
            filename of profile which is read in
        delimiter :
            delimiter for values in one line, default: ','
        value_idx :
            column number of line for value which should be considered, default: 1
        start :
            start value for search

        Returns
        -------
        float:
            maximum value of given profile
        """
        # ts_before = time.time()
        header: dict = cls.get_header_from(filename)
        unit_factor: float = cls.__get_value_unit_from(header)
        file = cls.open_file(filename)
        max_value: float = start
        for line in file:
            if line.startswith('#') or line.startswith('"') or line in ['\r\n', '\n']:
                continue
            data: [str] = line.split(delimiter)
            if len(data) < 2:
                value: float = float(data[0])
            else:
                value: float = float(data[value_idx])
            max_value = max(value * unit_factor, max_value)
        file.close()
        # print(max_value, unit_factor)
        # print(str(time.time() - ts_before))
        return max_value

    def close(self):
        self.__log.close()
        self.__file.close()

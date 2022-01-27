import datetime
import datetime as dt
import time
import numpy as np
from pytz import timezone
from simses.commons.config.simulation.profile import ProfileConfig
from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.profile.file import FileProfile
from simses.system.housing.abstract_housing import Housing
from simses.system.housing.twenty_ft_container import TwentyFtContainer
from simses.system.thermal.ambient.location_temperature import LocationAmbientTemperature
from simses.system.thermal.solar_irradiation.solar_irradiation_model import SolarIrradiationModel


def get_orbital_inclination(time_stamp: float) -> float:
    time_struct = time.gmtime(time_stamp)
    days_in_year = determine_leap_year(time_struct)
    day_number = time_struct.tm_yday
    orbital_inclination = 360 * (day_number / days_in_year)  # in °
    return orbital_inclination


def get_equation_of_time(orbital_inclination) -> float:
    equation_of_time_float = 60 * (0.0066 + 7.3525 * np.cos(np.deg2rad(orbital_inclination + 85.9)) +
                                   9.9359 * np.cos(np.deg2rad(2 * orbital_inclination + 108.9))
                                   + 0.3387 * np.cos(np.deg2rad(3 * orbital_inclination + 105.2)))  # in s
    equation_of_time = int(round(equation_of_time_float))  # in s
    return equation_of_time


def determine_leap_year(time_struct) -> float:
    year = time_struct.tm_year
    if (year % 4) == 0:
        if (year % 100) == 0:
            if (year % 400) == 0:
                days_in_year = 366
            else:
                days_in_year = 365
        else:
            days_in_year = 366
    else:
        days_in_year = 365
    return days_in_year


def get_sun_declination(orbital_inclination) -> float:
    sun_declination = 0.3948 - 23.2559 * np.cos(np.deg2rad(9.1 + orbital_inclination)) - 0.3915 * np.cos(
        np.deg2rad(2 * orbital_inclination + 5.4)) - 0.1764 * np.cos(np.deg2rad(3 * orbital_inclination + 26))  # in °
    return sun_declination


def get_hour_angle(true_local_time) -> float:
    hour_angle = (43200 - true_local_time.tm_hour * 3600 - true_local_time.tm_min * 60 - true_local_time.tm_sec) \
                 * 15 / 3600  # in °
    return hour_angle


def get_extraterrestrial_radiation_horizontal(time_struct, sun_elevation) -> float:
    quantity1 = (1 + 0.03344 * np.cos(np.deg2rad(time_struct.tm_yday * 0.9856 - 2.72))) * 1367  # in [w/m^2]
    extraterrestrial_radiation_horizontal = quantity1 * np.sin(np.deg2rad(sun_elevation))  # in [W/m^2]
    return extraterrestrial_radiation_horizontal


def get_diffuse_radiation_horizontal(global_radiation_horizontal, extraterrestrial_radiation_horizontal,
                                     sun_elevation) -> float:
    # kt is a determining factor
    if sun_elevation > 0:
        kt = global_radiation_horizontal / extraterrestrial_radiation_horizontal
    else:
        kt = 0
    if kt > 0:
        if kt <= 0.3:
            diffuse_radiation_horizontal = global_radiation_horizontal * (
                        1.020 - 0.254 * kt + 0.0123 * np.sin(np.deg2rad(sun_elevation)))  # in [W/m^2]
        elif 1 > kt >= 0.78:
            diffuse_radiation_horizontal = global_radiation_horizontal * (
                        0.486 - 0.182 * np.sin(np.deg2rad(sun_elevation)))  # in [W/m^2]
        elif 0.3 < kt < 0.78:
            diffuse_radiation_horizontal = global_radiation_horizontal * (
                        1.4 - 1.749 * kt + 0.177 * np.sin(np.deg2rad(sun_elevation)))  # in [W/m^2]
        elif kt > 1:
            diffuse_radiation_horizontal = 0
    else:
        diffuse_radiation_horizontal = 0  # in [W/m^2]
    return diffuse_radiation_horizontal


def get_direct_radiation_horizontal(global_radiation_horizontal, diffuse_radiation_horizontal) -> float:
    if diffuse_radiation_horizontal > 0:
        direct_radiation_horizontal = global_radiation_horizontal - diffuse_radiation_horizontal  # in [W/m^2]
    else:
        direct_radiation_horizontal = 0  # in [W/m^2]
    return direct_radiation_horizontal


def get_total_power_radiation(power_radiation_one, power_radiation_two, power_radiation_three,
                              power_radiation_four, power_radiation_five) -> float:
    power_radiation = power_radiation_one + power_radiation_two + power_radiation_three + power_radiation_four + power_radiation_five  # in W
    return power_radiation
    # todo (PL) determine energy for required timestep


class LocationSolarIrradiationModel(SolarIrradiationModel):
    """
        LocationSolarIrradiationModel calculates the total incident solar irradiation on the selected housing object at any
        given time for a specified location.
        Solar irradiation time series data from various sources:
        - German Weather Service (Deutscher Wetterdienst - DWD)
        - Oskar-von-Miller tower - LMU Garching

        """

    def __init__(self, profile_config: ProfileConfig, general_config: GeneralSimulationConfig,
                 housing: Housing):
        super().__init__()
        self.__file: FileProfile = FileProfile(general_config, profile_config.global_horizontal_irradiation_profile_file)
        self.__albedo: float = housing.albedo
        self.__container_azimuth: float = housing.azimuth
        self.__container_outer_layer_absorptivity: float = housing.outer_layer.absorptivity
        self.__small_container_area: float = housing.outer_layer.surface_area_short_side
        self.__tall_container_area: float = housing.outer_layer.surface_area_long_side
        self.__roof_container_area: float = housing.outer_layer.surface_area_roof
        self.__timezone: timezone = self.__file.get_timezone()
        self.__latitude = self.__file.get_latitude()
        self.__longitude = self.__file.get_longitude()

        self.__profile_config: ProfileConfig = profile_config
        self.__general_config: GeneralSimulationConfig = general_config
        self.__housing: Housing = housing

    def get_heat_load(self, time_stamp: float) -> float:
        # time_stamp = float(time_stamp)
        global_radiation_horizontal = self.__file.next(time_stamp)
        orbital_inclination = get_orbital_inclination(time_stamp)
        equation_of_time = get_equation_of_time(orbital_inclination)
        sun_declination = get_sun_declination(orbital_inclination)
        true_local_time = self.__get_true_local_time(equation_of_time, time_stamp)
        hour_angle = get_hour_angle(true_local_time)
        sun_elevation = self.__get_sun_elevation(hour_angle, sun_declination)
        solar_azimuth = self.__get_solar_azimuth(true_local_time, sun_elevation, sun_declination)
        time_struct = time.gmtime(time_stamp)
        extraterrestrial_radiation_horizontal = get_extraterrestrial_radiation_horizontal(time_struct,
                                                                                          sun_elevation)
        diffuse_radiation_horizontal = get_diffuse_radiation_horizontal(global_radiation_horizontal,
                                                                        extraterrestrial_radiation_horizontal,
                                                                        sun_elevation)
        direct_radiation_horizontal = get_direct_radiation_horizontal(global_radiation_horizontal,
                                                                      diffuse_radiation_horizontal)
        reflected_radiation_on_container_sides = self.__get_reflected_radiation_on_container_sides(sun_elevation,
                                                                                                   global_radiation_horizontal)

        # The areas below are defined and identified with the directions they face when azimuth = 0
        power_radiation_container_area_north = self.__get_radiation_container_area_north(
            reflected_radiation_on_container_sides, sun_elevation, solar_azimuth, direct_radiation_horizontal,
            diffuse_radiation_horizontal)
        power_radiation_container_area_south = self.__get_radiation_container_area_south(
            reflected_radiation_on_container_sides, sun_elevation, solar_azimuth, direct_radiation_horizontal,
            diffuse_radiation_horizontal)
        power_radiation_container_area_west = self.__get_radiation_container_area_west(
            reflected_radiation_on_container_sides, sun_elevation, solar_azimuth, direct_radiation_horizontal,
            diffuse_radiation_horizontal)
        power_radiation_container_area_east = self.__get_radiation_container_area_east(
            reflected_radiation_on_container_sides, sun_elevation, solar_azimuth, direct_radiation_horizontal,
            diffuse_radiation_horizontal)
        power_radiation_container_area_roof = self.__get_radiation_container_area_roof(sun_elevation,
                                                                                       direct_radiation_horizontal)
        power_radiation = get_total_power_radiation(power_radiation_container_area_north,
                                                    power_radiation_container_area_south,
                                                    power_radiation_container_area_west,
                                                    power_radiation_container_area_east,
                                                    power_radiation_container_area_roof)
        power_absorbed_radiation = power_radiation * self.__container_outer_layer_absorptivity  # in W
        return power_absorbed_radiation

    def get_global_horizontal_irradiance(self,time_step) -> float:
        return self.__file.next(time_step)  # in W/m2

    def __get_true_local_time(self, equation_of_time, time_stamp):
        local_time: datetime = dt.datetime.fromtimestamp(time_stamp)
        time_zone_data: datetime = self.__timezone.localize(local_time)
        time_zone_offset_seconds: float = time_zone_data.tzinfo._utcoffset.total_seconds()  # in s
        intermediate_quantity = 60 * 4 * (15 - self.__longitude)  # in s
        local_mean_time_epoch = time_stamp - time_zone_offset_seconds + 3600 - intermediate_quantity  # in s
        true_local_time_epoch = local_mean_time_epoch + equation_of_time  # in s
        true_local_time = time.gmtime(true_local_time_epoch)  # as datetime
        return true_local_time

    def __get_sun_elevation(self, hour_angle, sun_declination) -> float:
        sun_elevation = np.rad2deg(np.arcsin(
            np.cos(np.deg2rad(hour_angle)) * np.cos(np.deg2rad(self.__latitude)) * np.cos(
                np.deg2rad(sun_declination)) + np.sin(np.deg2rad(self.__latitude)) * np.sin(
                np.deg2rad(sun_declination))))  # in °
        if sun_elevation < 0:
            sun_elevation = 0  # in °
        return sun_elevation

    def __get_solar_azimuth(self, true_local_time, sun_elevation, sun_declination) -> float:
        quantity1 = np.rad2deg(np.arccos((np.sin(np.deg2rad(sun_elevation)) * np.sin(np.deg2rad(self.__latitude))
                                          - np.sin(np.deg2rad(sun_declination))) / (
                                                     np.cos(np.deg2rad(sun_elevation)) * np.cos(
                                                 np.deg2rad(self.__latitude)))))  # in °
        if sun_elevation >= 0:
            if true_local_time.tm_hour < 12:
                solar_azimuth = 180 - quantity1  # in °
            else:
                solar_azimuth = 180 + quantity1  # in °
        else:
            solar_azimuth = 0  # in °
        return solar_azimuth

    def __get_reflected_radiation_on_container_sides(self, sun_elevation, global_radiation_horizontal) -> float:
        if sun_elevation > 0:
            reflected_radiation_on_container_sides = global_radiation_horizontal * self.__albedo * 0.5  # in [W/m^2]
        else:
            reflected_radiation_on_container_sides = 0  # in [W/m^2]
        return reflected_radiation_on_container_sides

    def __get_radiation_container_area_north(self, reflected_radiation_on_container_sides, sun_elevation,
                                             solar_azimuth, direct_radiation_horizontal,
                                             diffuse_radiation_horizontal) -> float:
        if sun_elevation > 0:
            angle_of_incidence = np.rad2deg(np.arccos(-np.cos(np.deg2rad(sun_elevation)) * np.cos(
                np.deg2rad(solar_azimuth - self.__container_azimuth))))  # in °
            diffuse_radiation = diffuse_radiation_horizontal * 0.5  # in [W/m^2]
        else:
            angle_of_incidence = 0  # in °
            diffuse_radiation = 0  # in [W/m^2]
        if angle_of_incidence > 90:
            angle_of_incidence = 0  # in °
        else:
            angle_of_incidence = angle_of_incidence
        if angle_of_incidence > 0:
            direct_radiation = direct_radiation_horizontal * np.cos(np.deg2rad(angle_of_incidence)) / np.sin(
                np.deg2rad(sun_elevation))  # in [W/m^2]
        else:
            direct_radiation = 0  # in [W/m^2]
        power_radiation_one = self.__small_container_area * (
                    direct_radiation + diffuse_radiation + reflected_radiation_on_container_sides)  # in W
        return power_radiation_one

    def __get_radiation_container_area_south(self, reflected_radiation_on_container_sides, sun_elevation,
                                             solar_azimuth, direct_radiation_horizontal,
                                             diffuse_radiation_horizontal):
        if sun_elevation > 0:
            angle_of_incidence = np.rad2deg(np.arccos(-np.cos(np.deg2rad(sun_elevation)) * np.cos(
                np.deg2rad(solar_azimuth - self.__container_azimuth + 180))))  # in °
            diffuse_radiation = diffuse_radiation_horizontal * 0.5  # in [W/m^2]
        else:
            angle_of_incidence = 0  # in °
            diffuse_radiation = 0  # in [W/m^2]
        if angle_of_incidence > 90:
            angle_of_incidence = 0  # in °
        if angle_of_incidence > 0:
            direct_radiation = direct_radiation_horizontal * np.cos(np.deg2rad(angle_of_incidence)) / np.sin(
                np.deg2rad(sun_elevation))  # in [W/m^2]
        else:
            direct_radiation = 0  # in [W/m^2]
        power_radiation_two = self.__small_container_area * (
                    direct_radiation + diffuse_radiation + reflected_radiation_on_container_sides)  # in W
        return power_radiation_two

    def __get_radiation_container_area_west(self, reflected_radiation_on_container_sides, sun_elevation,
                                            solar_azimuth, direct_radiation_horizontal,
                                            diffuse_radiation_horizontal) -> float:
        if sun_elevation > 0:
            angle_of_incidence = np.rad2deg(np.arccos(-np.cos(np.deg2rad(sun_elevation)) * np.cos(
                np.deg2rad(solar_azimuth - self.__container_azimuth + 90))))  # in °
            diffuse_radiation = diffuse_radiation_horizontal * 0.5  # in [W/m^2]
        else:
            angle_of_incidence = 0  # in °
            diffuse_radiation = 0  # in [W/m^2]
        if angle_of_incidence > 90:
            angle_of_incidence = 0  # in °
        if angle_of_incidence > 0:
            direct_radiation = direct_radiation_horizontal * np.cos(np.deg2rad(angle_of_incidence)) / np.sin(
                np.deg2rad(sun_elevation))  # in [W/m^2]
        else:
            direct_radiation = 0  # in [W/m^2]
        power_radiation_three = self.__tall_container_area * (
                    direct_radiation + diffuse_radiation + reflected_radiation_on_container_sides)  # in W
        return power_radiation_three

    def __get_radiation_container_area_east(self, reflected_radiation_on_container_sides, sun_elevation,
                                            solar_azimuth, direct_radiation_horizontal,
                                            diffuse_radiation_horizontal) -> float:
        if sun_elevation > 0:
            angle_of_incidence = np.rad2deg(np.arccos(-np.cos(np.deg2rad(sun_elevation)) * np.cos(
                np.deg2rad(solar_azimuth - self.__container_azimuth + 270))))  # in °
            diffuse_radiation = diffuse_radiation_horizontal * 0.5  # in [W/m^2]
        else:
            angle_of_incidence = 0  # in °
            diffuse_radiation = 0  # in [W/m^2]
        if angle_of_incidence > 90:
            angle_of_incidence = 0  # in °
        if angle_of_incidence > 0:
            direct_radiation = direct_radiation_horizontal * np.cos(np.deg2rad(angle_of_incidence)) / np.sin(
                np.deg2rad(sun_elevation))  # in [W/m^2]
        else:
            direct_radiation = 0  # in [W/m^2]
        power_radiation_four = self.__tall_container_area * (
                    direct_radiation + diffuse_radiation + reflected_radiation_on_container_sides)  # in W
        return power_radiation_four

    def __get_radiation_container_area_roof(self, sun_elevation, direct_radiation_horizontal) -> float:
        if sun_elevation > 0:
            power_radiation_five = self.__roof_container_area * direct_radiation_horizontal * np.cos(
                np.deg2rad(1 / np.sin(np.deg2rad(sun_elevation))))  # in W
        else:
            power_radiation_five = 0  # in W
        return power_radiation_five

    def create_instance(self) -> SolarIrradiationModel:
        """
        reinstantiates the SolarIrradiationModel
        :return: SolarIrradiationModel
        """
        return LocationSolarIrradiationModel(self.__profile_config, self.__general_config, self.__housing)

    def close(self):
        self.__file.close()


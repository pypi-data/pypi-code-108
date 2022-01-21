"""Set of tools to model solar masks for a building.

Author: stephane.ploix@grenoble-inp.fr
"""

from abc import ABC
from buildingenergy import solar
import pyexcelerate
import matplotlib.pyplot
from math import pi

class Zone(ABC):
    """Abstract class standing for a single zone building. It can be used once specialized."""

    _azimut_min_max_in_rad: tuple = (-pi, pi)
    _altitude_min_max_in_rad: tuple = (0, pi / 2)
    _mask_plot_resolution: int = 20

    @staticmethod
    def set_max_plot_resolution(number_of_sample_per_axis):
        """Redefine the default grid max_plot resolution for plotting the zone.

        :param number_of_sample_per_axis: number of Solar Position per axis
        :return: None
        """
        Zone._mask_plot_resolution = number_of_sample_per_axis

    def __init__(self):
        """Create a zone."""
        pass

    def __contains__(self, solar_position):
        """Determine whether a solar_position of the sun in the sky defined by 2 angles (azimut and altitude) is contained by the zone or not.

        :param solar_position: solar solar_position in the sky
        :type solar_position: SolarPosition
        :return: True if contained, False otherwise
        :rtype: bool
        """
        raise NotImplementedError

    def plot(self, name=''):
        """Plot the mask according to the specified max_plot_resolution and print a description of the zone.

        :param name: file_name of the plot, default to ''
        :return: the zone
        """
        matplotlib.pyplot.figure()
        azimuts = [Zone._azimut_min_max_in_rad[0] + i * (Zone._azimut_min_max_in_rad[1] - Zone._azimut_min_max_in_rad[0]) / (Zone._mask_plot_resolution - 1) for i in range(Zone._mask_plot_resolution)]
        altitudes = [-Zone._altitude_min_max_in_rad[0] + i * (Zone._altitude_min_max_in_rad[1] - Zone._altitude_min_max_in_rad[0]) / (Zone._mask_plot_resolution - 1) for i in range(Zone._mask_plot_resolution)]
        axes = matplotlib.pyplot.gca()
        axes.set_xlim((180 / pi * Zone._azimut_min_max_in_rad[0], 180 / pi * Zone._azimut_min_max_in_rad[1]))
        axes.set_ylim((-180 / pi * Zone._altitude_min_max_in_rad[0], 180 / pi * Zone._altitude_min_max_in_rad[1]))
        for azimut in azimuts:
            for altitude in altitudes:
                if SolarPosition(azimut * 180 / pi, altitude * 180 / pi) in self:
                    matplotlib.pyplot.scatter(180/pi*azimut, 180/pi*altitude, c=0)
        matplotlib.pyplot.title(name)
        print('- %s' % name)
        print(self.__str__())
        return self


class SolarPosition:
    """Contain azimut and altitude angles of the sun for mask processing."""

    def __init__(self, azimut_in_deg, altitude_in_deg):
        """Create a solar position with azimut (south to west directed) and altitude (south to zenith directed) angles of the sun for mask processing.

        :param azimut_in_deg: solar angle with the south in degree, counted with trigonometric direction i.e. the azimut (0=South, 90=West, 180=North, -90=East)
        :type azimur_in_deg: float
        :param altitude_in_deg: zenital solar angle with the horizontal in degree i.e. the altitude (0=horizontal, 90=zenith)
        :type altitude_in_deg: float
        """
        self.azimut: float = azimut_in_deg/180*pi
        self.altitude: float = altitude_in_deg/180*pi

    @property
    def normalized_azimut_in_rad(self):
        """Return normalized solar azimut to belong to (-pi,pi) rad.

        :return: normalized azimut
        :rtype: float
        """
        return SolarPosition._normalize(self.azimut)

    @property
    def normalized_altitude_in_rad(self):
        """Return normalized solar altitude to belong to (-pi,pi) rad.

        :return: normalized altitude
        """
        return SolarPosition._normalize(self.altitude)

    @staticmethod
    def _normalize(angle):
        """Return a normalization of an angle for its value belongs to (-pi,pi) rad.

        :param angle: angle to be normalized
        :type angle: float
        :return: normalized angle in rad.
        :rtype: float
        """
        if angle % (2 * pi) > pi:
            angle = angle % (2 * pi) - 2 * pi
        if angle % (2 * pi) < -pi:
            angle = angle % (2 * pi) + 2 * pi
        return angle

    def __str__(self):
        """Return a description of the solar position.

        :return: string with normalized azimut and altitude angles in degree
        :rtype: str
        """
        return '(AZ:%frad,AL:%frad)' % (self.normalized_azimut_in_rad / pi * 180, self.normalized_altitude_in_rad / pi * 180)


class _BasicZone(Zone):
    """Abstract class that specifies basic zones."""

    def __init__(self):
        Zone.__init__(self)

    def __contains__(self, solar_position):
        raise NotImplemented


class _VerticalZone(_BasicZone):
    """A half vertical plan mask."""

    def __init__(self, solar_position, left):
        """Create a half vertical plan mask.

        :param solar_position: a solar position whose azimut is used to define the vertical half plan
        :type solar_position: SolarPosition
        :param left: define whether the left hand side should be considered (True) or the right hand side (False)
        :type left: bool
        """
        _BasicZone.__init__(self)
        self.position = solar_position
        self.left = left

    def __contains__(self, solar_position):
        """Check weither a position belong too the current half plan.

        :param solar_position:
        :type SolarPosition:
        :return: True if in the mask, False otherwise
        :rtype: bool
        """
        if self.left:
            if solar_position.normalized_azimut_in_rad <= self.position.normalized_azimut_in_rad:
                return True
        else:  # right
            if solar_position.normalized_azimut_in_rad >= self.position.normalized_azimut_in_rad:
                return True
        return False

    def __str__(self):
        """Return a representation of the half plan.

        :return: a descriptive string
        :rtype: str
        """
        if self.left:
            return '(left AZ:%f)' % (self.position.normalized_azimut_in_rad / pi * 180)
        else:
            return '(right AZ:%f)' % (self.position.normalized_azimut_in_rad / pi * 180)


class _HorizontalZone(_BasicZone):
    """A half horizontal plan mask."""

    def __init__(self, solar_position, low):
        """Create a half horizontal plan mask.

        :param solar_position: a solar position whose altitude is used to define the horizontal half plan
        :type solar_position: SolarPosition
        :param low: define whether the lower half plan should be considered (True) or the upper one (False)
        :type low: bool
        """
        _BasicZone.__init__(self)
        self.solar_position = solar_position
        self.low = low

    def __contains__(self, solar_position):
        """Check weither a position belong too the current half plan.

        :param solar_position: a solar position
        :type solar_position: SolarPosition
        :return: True if in the mask, False otherwise
        :rtype: bool
        """
        if solar_position.normalized_altitude_in_rad <= self.solar_position.normalized_altitude_in_rad:
            return self.low
        else:
            return not self.low

    def __str__(self):
        """Return a description of the half horizontal zone mask.

        :return: a string depicting the mask
        :rtype: str
        """
        if self.low:
            return '(lower AL:%f)' % (self.solar_position.normalized_altitude_in_rad / pi * 180)
        else:
            return '(upper AL:%f)' % (self.solar_position.normalized_altitude_in_rad / pi * 180)


class ComplexZone(Zone):
    """A complex zone is a set of masks with an intersection or a union in between."""

    def __init__(self, intersect: bool=True):
        """Create a complex zone.

        :param intersect: intersection if True, union otherwise
        :type intersect: bool
        """
        Zone.__init__(self)
        self.zones = list()
        self.intersect: bool = intersect
        self._inverse = False

    def inverse(self):
        """Invert the zone.

        :return: the inverted zone
        :rtype: ComplexZone
        """
        self._inverse = not self._inverse
        return self

    def union(self):
        """Transform the zone into a union.

        :return: the zone
        :rtype: ComplexZone
        """
        self.intersect: bool = False
        return self

    def intersection(self):
        """Transform the zone into an intersection.

        :return: the zone
        :rtype: ComplexZone
        """
        self.intersect: bool = True
        return self

    def add_vertical_strip_zone(self, left_solar_position, right_solar_position):
        """Create and add to the zone a vertical strip zone defined by the azimuts of two solar positions. The order matters: if the azimut of the right solar position is lower than the one of left solar position, it is understood than the strip include azimut 180°.

        :param left_solar_position: solar position specifying the left hand side azimut
        :type left_solar_position: SolarPosition
        :param right_solar_position: solar position specifying the right hand side azimut
        :type right_solar_position: SolarPosition
        :return: the zone
        :rtype: ComplexZone
        """
        if left_solar_position.normalized_azimut_in_rad <= right_solar_position.normalized_azimut_in_rad:
            vertical_strip_zone = ComplexZone(intersect=True)
            vertical_strip_zone.add_vertical_zone(left_solar_position, left=False)
            vertical_strip_zone.add_vertical_zone(right_solar_position, left=True)
        else:
            vertical_strip_zone = ComplexZone(intersect=False)
            vertical_strip_zone.add_vertical_zone(left_solar_position, left=False)
            vertical_strip_zone.add_vertical_zone(right_solar_position, left=True)
        self.zones.append(vertical_strip_zone)
        return self

    def add_horizontal_strip_zone(self, lower_solar_position, upper_solar_position):
        """Create and add to the zone a horizontal strip zone defined by the altitudes of two solar positions.

        :param lower_solar_position: solar position specifying the lower altitude
        :type lower_solar_position: SolarPosition
        :param upper_solar_position: solar position specifying the upper altitude
        :type upper_solar_position: SolarPosition
        :return: the zone
        :rtype: ComplexZone
        """
        complex_zone = ComplexZone(intersect=True)
        complex_zone.add_horizontal_zone(lower_solar_position, low=False)
        complex_zone.add_horizontal_zone(upper_solar_position, low=True)
        self.zones.append(complex_zone)
        return self

    def add_horizontal_zone(self, solar_position, low):
        """Create and add to the zone an horizontal half plan zone.

        :param solar_position: the solar position whose altitude specifies the horizontal half plan
        :type solar_position: SolarPosition
        :param low: lower half plan if True, upper otherwise
        :type low: bool
        :return: the zone
        :rtype: ComplexZone
        """
        self.zones.append(_HorizontalZone(solar_position, low=low))
        return self

    def add_vertical_zone(self, solar_position, left):
        """Create and add to the zone a vertical half plan zone.

        :param solar_position: the solar position whose azimut specifies the vertical half plan
        :type solar_position: SolarPosition
        :param left: left side if True, right side otherwise
        :type left: bool
        :return: the zone
        :rtype: ComplexZone
        """
        self.zones.append(_VerticalZone(solar_position, left=left))
        return self

    def add_rectangle_zone(self, lower_left_solar_position, upper_right_solar_position):
        """Create and add to the zone a rectangle defined by two solar positions. The order matters: if the azimut of the upper right solar position is lower than the one of lower left solar position, it is understood than the strip include azimut 180°.

        :param lower_left_solar_position: lower left solar position
        :type lower_left_solar_position: SolarPosition
        :param upper_right_solar_position: upper right solar position
        :type upper_right_solar_position: SolarPosition
        :return: the zone
        :rtype: ComplexZone
        """
        complex_zone = ComplexZone(intersect=True)
        complex_zone.add_vertical_strip_zone(lower_left_solar_position, upper_right_solar_position)
        complex_zone.add_horizontal_strip_zone(lower_left_solar_position, upper_right_solar_position)
        self.zones.append(complex_zone)
        return self

    def add_vertical_window_mask(self, south_relative_direction_in_deg=0, altitude_limitation_in_deg=90, azimut_limitation_in_deg=90):
        """Create and add a mask modeling the obstacles around a vertical window. The default parameters keep only the solar radiation in the south_relative_direction_in_deg +/- 90° in azimut and (0°,90°) in altitude. An upper solar protection reduces the range of possible solar altitudes. It can be modified by reducing altitude_limitation_in_deg. Left and right solar protections reduce the range of possible solar azimuts. It can be modified by asjusting azimut_limitation_in_deg.

        :param south_relative_direction_in_deg: direction perpendicular to the window, default to 0.
        :type south_relative_direction_in_deg: float
        :param altitude_limitation_in_deg: altitude limitation. 0 means no more direct solar radiation and 90° means no limitation on the altitude, default to 90.
        :type altitude_limitation_in_deg: float
        :param azimut_limitation_in_deg: limitation on the visible azimuts. 0 means no more direct solar radiation and 90° stands for no limitation on a plan perpendicular to the south_relative_direction_in_deg, default to 90.
        :type azimut_limitation_in_deg: float
        :return: the zone
        :rtype: ComplexZone
        """
        lower_left_position = SolarPosition(south_relative_direction_in_deg - azimut_limitation_in_deg, -altitude_limitation_in_deg)
        upper_right_position = SolarPosition(south_relative_direction_in_deg + azimut_limitation_in_deg, altitude_limitation_in_deg)
        self.add_rectangle_zone(lower_left_position, upper_right_position)
        return self

    def add_zone(self, zone):
        """Add a zone to the current one.

        :param zone: zone to be added
        :type zone: Zone
        :return: the zone
        :rtype: ComplexZone
        """
        self.zones.append(zone)
        return self

    def __contains__(self, solar_position):
        """Check weither the sun is masked or not.

        :param solar_position: azimut and altitude of the sun
        :type solar_position: SolarPosition
        :return: True if in the mask or False otherwise
        :rtype: bool
        """
        _inside = self.intersect
        for zone in self.zones:
            if self.intersect:
                _inside = _inside and (solar_position in zone)
            else:
                _inside = _inside or (solar_position in zone)
        if self._inverse:
            return not _inside
        return _inside

    def __str__(self):
        """Return a description of the complex zone.

        :return: a string describing the complex zone mask
        :rtype: bool
        """
        if self.intersect:
            string = 'Inter['
        else:
            string = 'Union['
        for i in range(len(self.zones)):
            string += self.zones[i].__str__()
            if i+1 < len(self.zones):
                string += ','
        return '\t' + string + ']'


class WindowMask(ComplexZone):
    """A specilized complex zone useful when mask is rectangular."""

    def __init__(self, azimut: tuple, altitude: tuple):
        """Create a window mask.

        :param azimut: east-west angle clockwise
        :type azumut: tuple[float]
        :param altitude: altitude or elevation angle in degree
        :type altitude: tuple[float]
        """
        super().__init__(intersect=True)
        self.add_rectangle_zone(SolarPosition(min(azimut), min(altitude)), SolarPosition(max(azimut), max(altitude)))


class Building:
    """A class used to obtain the solar gains through the windows of a building."""

    def __init__(self, site_weather_data, solar_mask: ComplexZone = None):
        """Create a parallelepipedic building with different windows with solar masks to estimate the solar gain.

        :param site_weather_data: wheather data
        :type site_weather_data: openweather.SiteWeatherData
        :param solar_mask: distant solar mask used for the whole building. None means no global solar masks
        :type solar_mask: ComplexZone
        """
        self.site_weather_data = site_weather_data
        self._stringdates, self._datetimes = self.site_weather_data.get('stringdate'), self.site_weather_data.get('datetime')
        if solar_mask is None:
            self.solar_mask = ComplexZone()
        else:
            self.solar_mask = solar_mask
        self.windows = dict()
        self.solar_model = solar.SolarModel(self.site_weather_data)

    def add_window(self, name, surface, exposure_in_deg=0, slope_in_deg=90, solar_factor=0.85, window_mask=None):
        """Add a window to the building.

        :param name: name of the window
        :type name: str
        :param surface: surface of the glass
        :type surface: float
        :param exposure_in_deg: exposure of the window (default: 0 = south) i.e. angle between the south direction and the normal to the surface projected in the tangential plan (0° means south directed, -90° east and 90° west
        :type exposure_in_deg: float
        :param slope_in_deg: slope of the window (default: 90 = vertical) i.e. angle between a tangential plan and the surface (0° means facing ground, 90° vertical and 180° facing the sky)
        :type slope_in_deg: float
        :param solar_factor: solar factor between 0 (opaque) and 100 (fully transparent)
        :type solar_factor: float
        :param window_mask: mask only for this window
        :type window_mask: WindowMask
        """
        if window_mask is not None:
            self.solar_mask.add_zone(window_mask)
        slope_in_deg = slope_in_deg - 90
        self.windows[name] = {'surface': surface, 'exposure_in_deg': exposure_in_deg, 'slope_in_deg': slope_in_deg, 'solar_factor': solar_factor}

    @property
    def datetimes(self):
        """Provide dates coming from weather data in a Python format.

        :return: list of dates in datetime.datetime format
        :rtype: list[datetime.datetime]
        """
        return self._datetimes

    @property
    def stringdates(self):
        """Return dates coming from weather data in a string format.

        :return: list of string dates
        :rtype: list[str]
        """
        return self._stringdates

    @property
    def solar_gain(self):
        """Return hourly solar gains coming through the windows.

        :return: list of total solar gains powers in Watt, and a dictionary of the detailed solar gains in Watts coming through each window
        :rtype: tuple[list[float], dict[str,list[float]]]
        """
        phi_total = list()
        phi_windows = dict()
        for window_name in self.window_names:
            phi_windows[window_name] = list()
        for k in range(len(self._datetimes)):
            phi_hour = 0
            current_datetime = self._datetimes[k]
            altitude_in_deg, azimuth_in_deg = self.solar_model.solar_angle(current_datetime)
            current_position = SolarPosition(azimuth_in_deg, altitude_in_deg)
            if altitude_in_deg > 0:
                for window_name in self.windows:
                    _, phi_direct_collected, phi_diffuse, phi_reflected = self.solar_model.solar_irradiation(self.windows[window_name]['exposure_in_deg'], self.windows[window_name]['slope_in_deg'], current_datetime, temperature=self.site_weather_data.get('temperature')[k], humidity=self.site_weather_data.get('humidity')[k], nebulosity_in_percentage=self.site_weather_data.get('cloudiness')[k], pollution=self.site_weather_data.pollution)
                    if self.solar_mask is None or current_position in self.solar_mask:
                        phi_window_hour = self.windows[window_name]['solar_factor'] * self.windows[window_name]['surface'] * (phi_direct_collected + phi_diffuse + phi_reflected)
                    else:
                        phi_window_hour = self.windows[window_name]['solar_factor'] * self.windows[window_name]['surface'] * (phi_diffuse + phi_reflected)
                    phi_hour += phi_window_hour
                    phi_windows[window_name].append(phi_window_hour)
                phi_total.append(phi_hour)
            else:
                phi_total.append(0)
                for window_name in self.windows:
                    phi_windows[window_name].append(0)
        return phi_total, phi_windows

    @property
    def window_names(self):
        """Return all the window names.

        :return: names of the windows
        :rtype: tuple[str]
        """
        return tuple(self.windows.keys())

    def window(self, name):
        """Return the solar gain through a window.

        :param name: name of a window
        :type name: str
        :return: list of solar powers crossing the window glass
        :rtype: list[float]
        """
        _, phi_windows = self.solar_gain
        return phi_windows[name]

    def day_averager(self, vector, average=True):
        """Compute the average or integration hour-time data to get day data.

        :param average: True to compute an average, False for integration
        :type average: bool
        :param vector: vector of values to be downsampled
        :return: list of floating numbers
        """
        current_day = self.datetimes[0].day
        day_integrated_vector = list()
        values = list()
        for k in range(len(self.datetimes)):
            if current_day == self.datetimes[k].day:
                values.append(vector[k])
            else:
                average_value = sum(values)
                if average:
                    average_value = average_value/len(values)
                day_integrated_vector.append(average_value)
                values = list()
            current_day = self.datetimes[k].day
        return day_integrated_vector

    def __len__(self):
        """Return the number of hours in the weather data.

        :return: number of hours in the weather data
        :rtype: int
        """
        return len(self.stringdates)

    def generate_xls(self, file_name='calculations', heat_temperature_reference=18,  cool_temperature_reference=26):
        """Save day degrees and solar gains per window for each day in an xls file.

        :param file_name: file name without extension, default to 'calculation'
        :type file_name: str
        :param temperature_reference: reference temperature for heating day degrees
        :type heat_temperature_reference: float
        :param cool_temperature_reference: reference temperature for cooling day degrees
        :type cool_temperature_reference: float
        """
        stringdate_days, average_temperature_days, min_temperature_days, max_temperature_days, dju_heat_days = self.site_weather_data.day_degrees(temperature_reference=heat_temperature_reference, heat=True)
        _, _, _, _, dju_cool_days = self.site_weather_data.day_degrees(temperature_reference=cool_temperature_reference, heat=False)

        data = [['date'], ['Tout'], ['Tout_min'], ['Tout_max'], ['dju_heat'], ['dju_cool']]
        data[0].extend(stringdate_days)
        data[1].extend(average_temperature_days)
        data[2].extend(min_temperature_days)
        data[3].extend(max_temperature_days)
        data[4].extend(dju_heat_days)
        data[5].extend(dju_cool_days)

        i=6
        for window_name in self.window_names:
            data.append([window_name+'(Wh)'])
            data[i].extend(self.day_averager(self.window(window_name), average=False))
            i += 1

        excel_workbook = pyexcelerate.Workbook()
        excel_worksheet = excel_workbook.new_sheet(file_name, data=list(map(list, zip(*data))))
        excel_workbook.save(file_name + '.xlsx')

"""DataContainer dedicated to H358 office.

Author: stephane.ploix@grenoble-inp.fr
"""
from buildingenergy import measurements, timemg


class DataContainer(measurements.DataContainer):
    """A H358 dedicated data container."""

    def __init__(self, csv_filename: str, skiprows: int = 0, nrows: int = None, initial_string_date=None, final_string_date=None):
        """Create a dedicated data container.

        :param csv_filename: file name of the csv file containing the data
        :type csv_filename: str
        :param skiprows: number of rows to ignore at the beginning of the csv file, defaults to 0
        :type skiprows: int, optional
        :param nrows: number of rows to keep (from row skiprows to skiprows+nrows), defaults to None
        :type nrows: int, optional
        :param initial_string_date: initial date in format 'dd/mm/YYYY HH:MM:SS', default to None, optional
        :type initial_string_date: str
        :param final_string_date: final date in format 'dd/mm/YYYY HH:MM:SS', default to None, optional
        :type final_string_date: str
        """
        super().__init__(csv_filename, skiprows=skiprows, nrows=nrows, initial_string_date=initial_string_date, final_string_date=final_string_date)
        datetime = self.get_variable('datetime')
        power_stephane = self.get_variable('power_stephane')
        power_khadija = self.get_variable('power_khadija')
        power_stagiaire = self.get_variable('power_stagiaire')
        detected_motion = self.get_variable('detected_motions')

        occupancy, presence = [], []
        for k in range(len(power_stephane)):
            working_day = int(datetime[k].weekday() < 5)
            working_hour = int(8 <= datetime[k].hour < 20)
            motion_detected = int(detected_motion[k]>0)
            estimation = int(power_stephane[k]>17) + int(power_khadija[k]>17) + int(power_stagiaire[k]>17)
            occupancy.append(working_day * working_hour * max(motion_detected, estimation))
            presence.append(occupancy[-1]>0)
        super().add_external_variable('occupancy', occupancy)
        super().add_external_variable('presence', presence)

if __name__ == '__main__':
    h358 = measurements.DataContainer('h358data_winter2015-2016.csv', initial_string_date='02/10/2015 00:00:00', final_string_date='03/10/2015 00:00:00')
    datetimes = h358.get_variable('datetime')
    CCO2 = h358.get_variable('office_CO2_concentration')
    Toffice_reference = h358.get_variable('Toffice_reference')
    Tout = h358.get_variable('Tout')
    Tcorridor = h358.get_variable('Tcorridor')
    occupancy = h358.get_variable('occupancy')
    window_opening = h358.get_variable('window_opening')
    door_opening = h358.get_variable('door_opening')
    dT_heat = h358.get_variable('dT_heat')

    ### put your code about waste calculation here  (useful variables: Toffice_reference, Tout, Tcorridor, dT_heat, CCO2, window_opening, door_opening)

    heat_needs = 0
    for i in range(len(datetimes)):
        if timemg.stringdate_to_datetime('1/01/2016 0:00:00') <= datetimes[i] < timemg.stringdate_to_datetime('1/01/2016 0:00:00'):
                heat_needs += 50 * max(0, dT_heat[i])/1000

    print('heat_needs:', heat_needs)
    h358.plot()

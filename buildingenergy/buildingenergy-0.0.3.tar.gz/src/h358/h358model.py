"""Knowledge model of the H358 office simulating both the indoor temperature and the CO2 concentration. 3 state space model for indoor temperature can be chosen: a second order model and 2 first order: one modelling slow dynamics and another one fast dynamics.

Author: stephane.ploix@grenoble-inp.fr
"""

import buildingenergy.thermics
import buildingenergy.solarbuilding
import buildingenergy.openweather
import buildingenergy.measurements
import buildingenergy.model
from scipy.signal import place_poles
from numpy import array, dot
import numpy

class H358Model(buildingenergy.model.Model):
    """
    A model for the H358 office. It must subclass buildingenergy.model.Model.

    :param buildingenergy: the super class
    :type buildingenergy: buildingenergy.model.Model
    """

    def __init__(self, sampling_time_in_secs: int, input_variable_names, influencing_variable_names,  possible_action_variable_names, output_variable_names, power_gain_variable_name: str) -> None:
        """
        Initialize a model for H358 officce.

        :param sampling_time_in_secs: time step of the related data in seconds
        :type sampling_time_in_secs: int
        :param input_variable_names: list of the input variable names that are used for the generated state space matrices
        :type input_variable_names: tuple[str]
        :param influencing_variable_names: list of the infuencing variable names (influencing state space matrices) that are used for the generated state space matrices
        :type influencing_variable_names: tuple[str]
        :param influencing_variable_max_values: list of the maximum values of the influencing variables for which the maximum matrices are provided
        :type influencing_variable_max_values: tuple[float]
        :param state_variable_names: list of the state variable names that are used for the generated state space matrices
        :type state_variable_names: tuple[str]
        :param output_variable_names: list of the output variable names that are used for the generated state space matrices
        :type output_variable_names: tuple[str]
        :param power_gain_variable_name: name of an input variable standing for internal gain power
        :type power_gain_variable_name: str
        :param use_state_observer: if True, the state vector will be replace by the state vector of the state observer once a day around midnight to better much measurements
        :type use_state_observer: bool
        """
        buildingenergy.model.Model.__init__(self, sampling_time_in_secs, input_variable_names, influencing_variable_names, possible_action_variable_names, output_variable_names, power_gain_variable_name)

    def parameter_calculations(self):
        """Calculate model parameters. This method called at initialization, which is used to isolate thermal calculations (but they could appear in the initializer."""
        self.room_volume = self.param('room_volume', 56, (45,100))
        self.co2_breath_production = self.param('co2_breath_production', 7, (3,12))
        self.body_metabolism = self.param('body_metabolism', 100, (70, 120))
        self.laptop_power_threshold_for_occupancy = 17
        self.concentrationCO2out = self.param('concentrationCO2out', 395, (390, 450))
        self.Tinit = self.param('Tinit', 20)
        self.heater_power_per_degree = self.param('heater_power_per_degree', 50, (20, 100))
        self.heater_max_power = self.param('heater_max_power', 1500)
        self.outdoor_infiltration = self.param('outdoor_infiltration', 0.0035, (0.001, 0.1))
        self.window_open_infiltration = self.param('window_open_infiltration', 0.01, (.001, .1))
        self.corridor_infiltration = self.param('corridor_infiltration', 0.0035, (0.001, 0.1))
        self.door_open_infiltration = self.param('door_open_infiltration', 0.007, (.001, 10))
        self.solar_factor = self.param('solar_factor', 0.85, (0, 2))
        self.window_direction = -13
        self.solar_mask = buildingenergy.solarbuilding.WindowMask((-73+self.window_direction, 73+self.window_direction), (20, 60))

        # corridor wall
        door_surface = 80e-2 * 200e-2
        glass_surface = 100e-2 * 100e-2
        internal_wall_thickness = 13e-3 + 34e-3 + 13e-3
        cupboard_corridor_surface = (185e-2 + internal_wall_thickness + 34e-2 + 20e-3) * 2.5
        corridor_wall_surface = (408e-2 + 406e-2 + internal_wall_thickness) * 2.5 - door_surface - glass_surface - cupboard_corridor_surface
        door = buildingenergy.thermics.Composition(position='vertical', first_layer_indoor=True, last_layer_indoor=True)
        door.add_layer('wood', 5e-3)
        door.add_layer('air', 15e-3)
        door.add_layer('wood', 5e-3)
        glass = buildingenergy.thermics.Composition(position='vertical', first_layer_indoor=True, last_layer_indoor=True)
        glass.add_layer('glass', 4e-3)
        cupboard = buildingenergy.thermics.Composition(position='vertical', first_layer_indoor=True, last_layer_indoor=True)
        cupboard.add_layer('plaster', 13e-3)
        cupboard.add_layer('foam', 34e-3)
        cupboard.add_layer('plaster', 13e-3)
        cupboard.add_layer('air', 50e-2 - 20e-3)
        cupboard.add_layer('wood', 20e-3)
        plain_corridor_wall = buildingenergy.thermics.Composition(position='vertical', first_layer_indoor=True, last_layer_indoor=True)
        plain_corridor_wall.add_layer('plaster', 13e-3)
        plain_corridor_wall.add_layer('foam', 34e-3)
        plain_corridor_wall.add_layer('plaster', 13e-3)
        corridor_wall = buildingenergy.thermics.Wall('corridor')
        corridor_wall.add_composition(door, door_surface)
        corridor_wall.add_composition(glass, glass_surface)
        corridor_wall.add_composition(cupboard, (185e-2 + internal_wall_thickness + 34e-2 + 20e-3) * 2.5)
        corridor_wall.add_composition(plain_corridor_wall, corridor_wall_surface)
        corridor_wall.add_infiltration(self.corridor_infiltration.val)
        corridor_wall.add_max_opening_air_flow(self.door_open_infiltration.val)
        self.Rcor_0 = self.param('Rcor_0', corridor_wall.R(0), (corridor_wall.R(0)*.1, corridor_wall.R(0)*10))
        self.Rcor_1 = self.param('Rcor_1', corridor_wall.R(1), (corridor_wall.R(1)*.1, corridor_wall.R(0)*10))
        print(corridor_wall)

        # outdoor wall
        west_glass_surface = 2 * 130e-2 * 52e-2 + 27e-2 * 52e-2 + 72e-2 * 52e-2
        east_glass_surface = 36e-2 * 56e-2
        windows_surface = west_glass_surface + east_glass_surface
        self.windows_surface = self.param('windows_surface', windows_surface)
        nocavity_surface = (685e-2 - 315e-2 - 60e-2) * 2.5 - east_glass_surface
        cavity_surface = 315e-2 * 2.5 - west_glass_surface
        windows = buildingenergy.thermics.Composition(first_layer_indoor=True, last_layer_indoor=False, position='vertical')
        windows.add_layer('glass', 4e-3)
        windows.add_layer('air', 12e-3)
        windows.add_layer('glass', 4e-3)
        nocavity = buildingenergy.thermics.Composition(first_layer_indoor=True, last_layer_indoor=False, position='vertical')
        nocavity.add_layer('concrete', 30e-2)
        cavity = buildingenergy.thermics.Composition(first_layer_indoor=False, last_layer_indoor=True, position='vertical')
        cavity.add_layer('concrete', 30e-2)
        cavity.add_layer('air', 34e-2)
        cavity.add_layer('wood', 20e-3)
        external_wall = buildingenergy.thermics.Wall('outdoor')
        external_wall.add_composition(windows, windows_surface)
        external_wall.add_composition(nocavity, nocavity_surface)
        external_wall.add_composition(cavity, cavity_surface)
        external_wall.add_bridge(0.5 * 0.99, 685e-2)  # ThBAT booklet 5, 3.1.1.2, 22B
        external_wall.add_infiltration(self.outdoor_infiltration.val)
        external_wall.add_max_opening_air_flow(self.window_open_infiltration.val)
        self.Rout_0 = self.param('Rout_0', external_wall.R(0), (external_wall.R(0)*.5, external_wall.R(0)*6))
        self.Rout_1 = self.param('Rout_1', external_wall.R(1), (external_wall.R(1)*.5, external_wall.R(1)*1.5))
        print(external_wall)

        # slab
        slab_effective_thickness = 11.9e-2
        slab_surface = (309e-2 + 20e-3 + 34e-2) * (406e-2 + internal_wall_thickness) + 408e-2 * (273e-2 - 60e-2) - 315e-2 * (34e-2 + 20e-3) - (185e-3 + internal_wall_thickness) * 50e-2
        print('slab surface:', slab_surface)
        slab = buildingenergy.thermics.Composition(first_layer_indoor=True, last_layer_indoor=None, position='horizontal')
        slab.add_layer('concrete', slab_effective_thickness/2)
        floor_inertia1 = buildingenergy.thermics.Wall('slab')
        floor_inertia1.add_composition(slab, slab_surface)
        print(floor_inertia1)
        Ci1 = buildingenergy.thermics.Composition.volumic_masses['concrete'] * buildingenergy.thermics.Composition.specific_heats['concrete'] * slab_surface * slab_effective_thickness
        self.Ci1 = self.param('Ci1', Ci1, (Ci1 * .5,  Ci1 * 5))
        self.Ri1 = self.param('Ri1', floor_inertia1.R(), (floor_inertia1.R()*.1, floor_inertia1.R()*100))

        slab_effective_thickness = 2.43e-2
        slab.add_layer('concrete', slab_effective_thickness/2)
        floor_inertia2 = buildingenergy.thermics.Wall('slab')
        floor_inertia2.add_composition(slab, slab_surface)
        print(floor_inertia1)
        Ci2 = buildingenergy.thermics.Composition.volumic_masses['concrete'] * buildingenergy.thermics.Composition.specific_heats['concrete'] * slab_surface * slab_effective_thickness
        self.Ci2 = self.param('Ci2', Ci2, (Ci2*.5, Ci2*1.5))
        self.Ri2 = self.param('Ri2', floor_inertia2.R(), (floor_inertia2.R()*.1, floor_inertia2.R()*1.5))

    def register_data(self, data_container: buildingenergy.measurements.DataContainer):
        """
        Store measurement data and weather data read respectively from a DataContainer and an OpenWeather objects. The DataContainer should be saved as self.data_container to get the plotting capabilities. The useful data must be stored into a [str, list[float]] dictionnary: self._data.

        :param measurement_file_name: csv file name containing measurement data from office
        :type measurement_file_name: str
        :param weather_file_name: json file name coming from openweather
        :type weather_file_name: str
        :param skiprows: list-like or integer Row numbers to skip (0-indexed) or number of rows to skip (int) at the start of the file
        :type skiprows: int, default is 0
        :param nrows: Number of rows of file to read. Useful for reading pieces of large files. Default is None
        :type nrows: int
        """
        site_weather_data = buildingenergy.openweather.OpenWeatherMapJsonReader('grenoble_weather2015-2019.json', from_stringdate=data_container.starting_stringdatetime, to_stringdate=data_container.ending_stringdatetime, sea_level_in_meter=330, albedo=.1).site_weather_data
        office_solar_gain = buildingenergy.solarbuilding.Building(site_weather_data)
        office_solar_gain.add_window('main', 1, exposure_in_deg=self.window_direction, slope_in_deg=90, solar_factor=1, window_mask=self.solar_mask)

        _data = dict()
        _data['datetime'] = data_container.get_variable('datetime')
        _data['stringtime'] = data_container.get_variable('stringtime')
        _data['phi_sun_out_1m2'], _ = office_solar_gain.solar_gain
        _data['Tout'] = office_solar_gain.site_weather_data.get('temperature')
        _data['office_CO2_concentration'] = data_container.get_variable('office_CO2_concentration')
        _data['corridor_CO2_concentration'] = data_container.get_variable('corridor_CO2_concentration')
        _data['Toffice_reference'] = data_container.get_variable('Toffice_reference')
        _data['Tcorridor'] = data_container.get_variable('Tcorridor')
        power_stephane = data_container.get_variable('power_stephane')
        power_khadija = data_container.get_variable('power_khadija')
        power_audrey = data_container.get_variable('power_audrey')
        power_stagiaire = data_container.get_variable('power_stagiaire')
        power_block_east = data_container.get_variable('power_block_east')
        power_block_west = data_container.get_variable('power_block_west')
        total_electric_power = []
        for i in range(data_container.size()):
            total_electric_power.append(power_block_east[i] + power_block_west[i])
        _data['total_electric_power'] = total_electric_power
        _data['window_opening'] = data_container.get_variable('window_opening')
        _data['door_opening'] = data_container.get_variable('door_opening')
        _data['dT_heat'] = data_container.get_variable('dT_heat')

        occupancy = []
        for k in range(data_container.size()):
            occupancy.append((power_stephane[k] > self.laptop_power_threshold_for_occupancy) + (power_khadija[k] > self.laptop_power_threshold_for_occupancy) + (power_audrey[k] > self.laptop_power_threshold_for_occupancy) + (power_stagiaire[k] > self.laptop_power_threshold_for_occupancy))
        _data['occupancy'] = occupancy
        _data['presence'] = [int(o > 0) for o in occupancy]
        heating = []
        for k in range(0, data_container.size(), 24):
            dT_heat_detected = 0
            for i in range(k, min(k+24, data_container.size())):
                if _data['dT_heat'][i] > 5:
                    dT_heat_detected = 1
                    break
            heating.extend([dT_heat_detected for _ in range(k, min(k+24, data_container.size()))])
        _data['heating'] = heating
        self._data = _data

    def init(self):
        """Initialise a simulation: must be called in case of parameter changes."""
        self._data['free_gain_power'] = [self.body_metabolism.val*self.data('occupancy')[k]+self.data('total_electric_power')[k]+self.solar_factor.val * self.windows_surface.val * self.data('phi_sun_out_1m2')[k] for k in range(len(self.data('datetime')))]
        self._data['heating_power'] = [self.heater_power_per_degree.val * self.data('dT_heat')[k] if self.data('dT_heat')[k]> 2 else 0 for k in range(len(self.data('datetime')))]
        if len(self.state_variable_names) == 2:
            X = array([[self.Tinit.val],[self.concentrationCO2out.val]])
        else:
            X = array([[self.Tinit.val],[self.Tinit.val],[self.concentrationCO2out.val]])
        return X

    def computeU(self, k: int, state_vector: array, influencing_variable_values, actions):
        """Compute the vector U of the state space representation together with the heating power, that can be the one that has been recorded or deduced from the temperature setpoint (assuming a perfect controller, with a one hour perspective).

        :param state_vector: current state vector used to determine the heating power in case a setpoint is specified in the actions
        :type state_vector: numpy.array
        :param actions: list of current actions performaed on the system. It might contains in particular here 'heating_power' in case it's directly controlled, and 'temperature_setpoint' in case of an indirect control of the heating power by specifying the temperature setpoint
        :type: dict[str, float]
        :return: the vector U of the state space representation together with the heating power and an array with current output values
        :rtype: tuple[array, float, array]
        """
        U = array([[self.data('Tcorridor')[k]], [self.data('Tout')[k]],[self.data('free_gain_power')[k]],[self.data('corridor_CO2_concentration')[k]], [self.concentrationCO2out.val], [self.data('occupancy')[k]]])

        temperature_setpoint, heating_power = None, 0
        if influencing_variable_values is None:
            influencing_variable_values = tuple([0 for _ in range(len(self.influencing_variable_names))])
        if actions is not None and 'temperature_setpoint' in actions and actions['temperature_setpoint'] is not None:
                temperature_setpoint = actions['temperature_setpoint']
                temperature_without_heating = dot(self.Cd_state_matrix.get(influencing_variable_values)[0, :], state_vector) + dot(self.Dd_state_matrix.get(influencing_variable_values)[0, :], U)
                heating_power = (temperature_setpoint - temperature_without_heating) / self.Dd_state_matrix.get(influencing_variable_values)[0, self.power_gain_index]
                heating_power = min(max(0, heating_power[0]), self.heater_max_power.val)
                actions['heating_power'] = heating_power
                U[self.power_gain_index,0] += actions['heating_power']
        elif actions is not None and 'heating_power' in actions:
                U[self.power_gain_index,0] += actions['heating_power']
        if actions is None:
            actions = {}
        return U, actions

    def matrix_K_state_observer(self) -> numpy.array:
        """Return the gain matrix K for the state observer.

        :return: matrix K
        :rtype: numpy.array
        """
        P = numpy.array([0+i*1e-6 for i in range(len(self.state_variable_names))])
        fsf = place_poles(numpy.transpose(self.Ad_state_matrix.nominal()), numpy.transpose(self.Cd_state_matrix.nominal()), P, method='KNV0')
        return numpy.transpose(fsf.gain_matrix)

    def compute_physical_matrices_order2(self, influencing_variable_values):
        """Return a function that is provided to buildingenergy.model.Model.discrete_state_matrices(). It computes the time continuous state space matrices taking into account the provided values of the influencing variables, respecting the order  specified when creating a buildingenergy.model.Model.

        :param influencing_variable_values: list of the values of the influencing variables for which the continuous state matrices must be computed
        :type influencing_variable_values: list[float]
        :return: state matrices of a state space representation, consistent with the orders of variables specified when creating a buildingenergy.model.Model
        :rtype: tuple[list[list[float]]]
        """
        self.state_variable_names = ('tau1', 'tau2', 'CO2')
        door_opening = influencing_variable_values[0]
        window_opening = influencing_variable_values[1]

        Rcor = self.Rcor_0.val +  (self.Rcor_1.val - self.Rcor_0.val) * door_opening
        Rout = self.Rout_0.val +  (self.Rout_1.val - self.Rout_0.val) * window_opening
        Qcor = self.corridor_infiltration.val + (self.door_open_infiltration.val - self.corridor_infiltration.val) * door_opening
        Qout = self.outdoor_infiltration.val + (self.window_open_infiltration.val - self.outdoor_infiltration.val) * window_opening

        R = 1 / (1/Rcor + 1/self.Ri1.val + 1/self.Ri2.val + 1/Rout)
        A = [[(R-self.Ri1.val)/(self.Ri1.val**2*self.Ci1.val), R/(self.Ri1.val*self.Ri2.val*self.Ci1.val), 0],
                [R/(self.Ri1.val*self.Ri2.val*self.Ci2.val), (R-self.Ri2.val)/(self.Ri2.val**2*self.Ci2.val),0],
                [0,0,-(Qcor+Qout)/self.room_volume.val]]
        B = [[R/(self.Ri1.val*Rcor*self.Ci1.val), R/(self.Ri1.val*Rout*self.Ci1.val), R/(self.Ri1.val*self.Ci1.val), 0, 0, 0],
                [R/(self.Ri2.val*Rcor*self.Ci2.val), R/(self.Ri2.val*Rout*self.Ci2.val), R/(self.Ri2.val*self.Ci2.val),0,0,0],
                [0,0,0,Qcor/self.room_volume.val, Qout/self.room_volume.val,self.co2_breath_production.val/self.room_volume.val]]
        C = [[R/self.Ri1.val, R/self.Ri2.val,0], [0,0,1]]
        D = [[R/Rcor, R/Rout, R, 0, 0, 0],[0, 0, 0, 0, 0, 0]]
        return A, B, C, D


    def compute_physical_matrices_order1_slow(self, influencing_variable_values):
        """Return a function that is provided to buildingenergy.model.Model.discrete_state_matrices(). It computes the time continuous state space matrices taking into account the provided values of the influencing variables, respecting the order  specified when creating a buildingenergy.model.Model.

        :param influencing_variable_values: list of the values of the influencing variables for which the continuous state matrices must be computed
        :type influencing_variable_values: list[float]
        :return: state matrices of a state space representation, consistent with the orders of variables specified when creating a buildingenergy.model.Model
        :rtype: tuple[list[list[float]]]
        """
        self.state_variable_names = ('tau1', 'CO2')
        door_opening = influencing_variable_values[0]
        window_opening = influencing_variable_values[1]

        Rcor = self.Rcor_0.val +  (self.Rcor_1.val - self.Rcor_0.val) * door_opening
        Rout = self.Rout_0.val +  (self.Rout_1.val - self.Rout_0.val) * window_opening
        Qcor = self.corridor_infiltration.val + (self.door_open_infiltration.val - self.corridor_infiltration.val) * door_opening
        Qout = self.outdoor_infiltration.val + (self.window_open_infiltration.val - self.outdoor_infiltration.val) * window_opening

        R = 1 / (1/Rcor + 1/self.Ri1.val + 1/Rout)
        A = [[(R-self.Ri1.val)/(self.Ri1.val**2*self.Ci1.val), 0],
                [0,-(Qcor+Qout)/self.room_volume.val]]
        B = [[R/(self.Ri1.val*Rcor*self.Ci1.val), R/(self.Ri1.val*Rout*self.Ci1.val), R/(self.Ri1.val*self.Ci1.val), 0, 0, 0],
                [0,0,0,Qcor/self.room_volume.val, Qout/self.room_volume.val,self.co2_breath_production.val/self.room_volume.val]]
        C = [[R/self.Ri1.val, 0], [0, 1]]
        D = [[R/Rcor, R/Rout, R, 0, 0, 0], [0, 0, 0, 0, 0, 0]]
        return A, B, C, D

    def compute_physical_matrices_order1_fast(self, influencing_variable_values):
        """Return a function that is provided to buildingenergy.model.Model.discrete_state_matrices(). It computes the time continuous state space matrices taking into account the provided values of the influencing variables, respecting the order  specified when creating a buildingenergy.model.Model.

        :param h358model: the H358 model, containing parameters (values can be obtained thanks to 'parameter name' and ordered lists of input, influencing, state and output variables
        :type h358model: H358model
        :param influencing_variable_values: list of the values of the influencing variables for which the continuous state matrices must be computed
        :type influencing_variable_values: list[float]
        :return: state matrices of a state space representation, consistent with the orders of variables specified when creating a buildingenergy.model.Model
        :rtype: tuple[list[list[float]]]
        """
        self.state_variable_names = ('tau1', 'CO2')
        door_opening = influencing_variable_values[0]
        window_opening = influencing_variable_values[1]

        Rcor = self.Rcor_0.val +  (self.Rcor_1.val - self.Rcor_0.val) * door_opening
        Rout = self.Rout_0.val +  (self.Rout_1.val - self.Rout_0.val) * window_opening
        Qcor = self.corridor_infiltration.val + (self.door_open_infiltration.val - self.corridor_infiltration.val) * door_opening
        Qout = self.outdoor_infiltration.val + (self.window_open_infiltration.val - self.outdoor_infiltration.val) * window_opening

        R = 1 / (1/Rcor + 1/self.Ri2.val + 1/Rout)
        A = [[(R-self.Ri2.val)/(self.Ri2.val**2*self.Ci2.val), 0],
                [0,-(Qcor+Qout)/self.room_volume.val]]
        B = [[R/(self.Ri2.val*Rcor*self.Ci2.val), R/(self.Ri2.val*Rout*self.Ci2.val), R/(self.Ri2.val*self.Ci2.val), 0, 0, 0],
                [0,0,0,Qcor/self.room_volume.val, Qout/self.room_volume.val,self.co2_breath_production.val/self.room_volume.val]]
        C = [[R/self.Ri2.val, 0], [0, 1]]
        D = [[R/Rcor, R/Rout, R, 0, 0, 0], [0, 0, 0, 0, 0, 0]]
        return A, B, C, D


if __name__ == '__main__':
    use_state_observer=True
    h358_model = H358Model(sampling_time_in_secs=3600, input_variable_names = ('Tcorridor', 'Tout', 'free_gain_power', 'corridorCCO2', 'outCCO2', 'occupancy'), influencing_variable_names = ('door_opening', 'window_opening'), possible_action_variable_names = ('door_opening', 'window_opening', 'heating_power', 'temperature_setpoint'), output_variable_names = ('Toffice_reference', 'office_CO2_concentration'), power_gain_variable_name='free_gain_power')
    data_container = buildingenergy.measurements.DataContainer('h358data_winter2015-2016.csv', skiprows=0, nrows=None)

    h358_model.register_data(data_container)
    #h358_model.register_state_space_representation(('tau2', 'Cin'), h358_model.compute_physical_matrices_order1_fast)
    h358_model.register_state_space_representation(('tau1', 'Cin'), h358_model.compute_physical_matrices_order1_slow)
    #h358_model.register_state_space_representation(('tau1', 'tau2', 'Cin'), h358_model.compute_physical_matrices_order2)

    datetime = h358_model.data('datetime')
    Tout = h358_model.data('Tout')
    Tcorridor = h358_model.data('Tcorridor')
    Toffice_reference = h358_model.data('Toffice_reference')
    corridor_CO2_concentration = h358_model.data('corridor_CO2_concentration')
    office_CO2_concentration = h358_model.data('office_CO2_concentration')
    door_opening = h358_model.data('door_opening')
    window_opening = h358_model.data('window_opening')
    occupancy = h358_model.data('occupancy')
    total_electric_power = h358_model.data('total_electric_power')
    dT_heat = h358_model.data('dT_heat')

    office_simulated_temperature = []
    office_simulated_CO2 = []
    X = h358_model.initialize()
    if use_state_observer:
        h358_model.K = h358_model.matrix_K_state_observer()
    Xobs = X.copy()
    for k in range(len(datetime)):
        I = (door_opening[k], window_opening[k])  # influencing variables
        resulting_actions_dict = {'heating_power': h358_model.data('heating_power')[k], 'door_opening': door_opening[k], 'window_opening': window_opening[k]}
        U, resulting_actions_dict = h358_model.computeU(k, X, I, actions=resulting_actions_dict)
        Y = h358_model.computeY(k, X, U, I)
        office_simulated_temperature.append(Y[0,0])
        office_simulated_CO2.append(Y[1,0])
        if use_state_observer:
            X, Xobs = h358_model.stepX(k, X, Xobs, I, U)
            if k % 24 == 0:
                X = Xobs
        else:
            X, observer_state_vector = h358_model.stepX(k, X, None, I, U)  # k: int, state_vector: array, observer_state_vector: array, influencing_variables: list[float], input_variables: array
    print('* parameters:')
    print(*h358_model.parameters)
    print('* adjustable parameters')
    print(*h358_model.adjustables)
    data_container.add_external_variable('office_simulated_temperature', office_simulated_temperature)
    data_container.add_external_variable('office_simulated_CO2', office_simulated_CO2)
    data_container.plot()

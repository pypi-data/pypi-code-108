import time as ti
from matplotlib import pyplot as plt
from scipy.integrate import solve_ivp
from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.config.simulation.system import StorageSystemConfig
from simses.commons.state.system import SystemState
from simses.system.auxiliary.auxiliary import Auxiliary
from simses.system.auxiliary.heating_ventilation_air_conditioning.hvac import HeatingVentilationAirConditioning
from simses.system.housing.abstract_housing import Housing
from simses.system.power_electronics.acdc_converter.abstract_acdc_converter import AcDcConverter
from simses.system.power_electronics.dcdc_converter.abstract_dcdc_converter import DcDcConverter
from simses.system.storage_system_dc import StorageSystemDC
from simses.system.thermal.ambient.ambient_thermal_model import AmbientThermalModel
from simses.system.thermal.model.system_thermal_model import SystemThermalModel
from simses.technology.storage import StorageTechnology


class ZeroDDynamicSystemThermalModel(SystemThermalModel):
    """This is going to be Stefan's model."""

    def __init__(self, ambient_thermal_model: AmbientThermalModel, housing: Housing,
                 hvac: HeatingVentilationAirConditioning, general_config: GeneralSimulationConfig,
                 storage_system_config: StorageSystemConfig, dc_systems: [StorageSystemDC],
                 acdc_converter: AcDcConverter):
        # ---------- General parameters and config ----------
        super().__init__()
        self.__system_config: StorageSystemConfig = storage_system_config
        self.__acdc_converter = acdc_converter
        self.__dc_systems = dc_systems[0]
        self.__storage_technology: StorageTechnology = self.__dc_systems.get_storage_technology()
        self.__dc_dc_converter: DcDcConverter = self.__dc_systems.get_dc_dc_converter()
        self.__start_time: float = general_config.start
        self.__end_time: float = general_config.end
        self.__sample_time: float = general_config.timestep
        self.__loop: int = general_config.loop

        # Ambient temperature model
        self.__ambient_thermal_model: AmbientThermalModel = ambient_thermal_model
        # Housing Model
        self.__housing: Housing = housing  # Link housing object
        # HVAC model
        self.__heating_cooling: HeatingVentilationAirConditioning = hvac
        # Solar irradiation model
        # TODO create and couple solar irradiation model (AP)

        # ---------- Settings ----------
        # It is possible to set developer_mode and/or developer_mode_plotting active in the config.
        # plotting mode: a plot is generated after the simulation has finished
        # developer mode: thermal resistances, thermal capacities, times for code segments, mean/max control difference,
        # coefficients of the pid controller, losses of the batteries and converters and the capacity of the battery get
        # printed out
        try:
            self.__developer_mode: int = int(self.__system_config.hvac['constant_hvac'][7])
        except IndexError:
            self.__developer_mode = 0
        else:
            if self.__developer_mode != 1 and self.__developer_mode != 0:
                raise Exception('Developer mode, in the config, must be set to 0 (not wished) or 1 (wished) or '
                                'should not be set at all.')
        try:
            self.__developer_mode_plotting: int = int(self.__system_config.hvac['constant_hvac'][8])
        except IndexError:
            self.__developer_mode_plotting = 0
        else:
            if self.__developer_mode_plotting != 1 and self.__developer_mode_plotting != 0:
                raise Exception(
                    'Plotting, in the config, must be set to 0 (not wished) or 1 (wished) or should not be set at all.')

        # ---------- time values for the simulation ----------
        # It is possible to set the calculation and the evaluation time in the config.
        # -- Calculation Time --
        # self.__calculation_time_step is the time step after which the thermal power gets recalculated
        try:
            self.__calculation_time_step: int = int(self.__system_config.hvac['constant_hvac'][6])
        except IndexError:
            # if the simulated time span is larger then 1 day, the calculation time step increases to lower the runtime
            if self.__end_time - self.__start_time >= 86400:
                self.__calculation_time_step = 300
            else:
                self.__calculation_time_step = 60
        # securing that the sample time is an integer multiple of the calculation time step
        if self.__sample_time % self.__calculation_time_step != 0:
            raise Exception(
                'calculate_temperature failed because calculation_time_step is not an integer multiple of '
                'sample time, please change calculation_time_step or the sample time')

        # -- Evaluation Time --
        # self.__t_eval_step is the time step after which the equation gets evaluated, it has impact on the I-controller
        # and the plotting (it results in the graphs getting more detailed).
        # Set t_eval-step to self.__calculation_time_step if plots are not needed because the impact on the I-Controller
        # is negligible.
        self.__t_eval_step: int = self.__calculation_time_step
        # securing that calculation_time is an integer multiple of t_eval_step
        if self.__calculation_time_step % self.__t_eval_step != 0:
            raise Exception('calculate_temperature failed because sample_time is not an integer multiple of '
                            't_eval_step, please change t_eval_step')

        # ---------- Initializing temperatures of components ----------
        # The temperature target for the battery can be set in the config. If no value has been given, 25°C is taken as
        # target.
        try:
            self.__battery_temperature_target = float(self.__system_config.hvac['constant_hvac'][2]) + 273.15
        except IndexError:
            self.__battery_temperature_target = 298.15

        # The temperatures of the components in the housing get initialized with the target temperature.
        self.__ia_temperature: float = self.__battery_temperature_target  # K internal air temperature
        self.__battery_temperature = self.__battery_temperature_target  # K battery temperature
        self.__converter_temperature_ac_dc = self.__battery_temperature_target  # K converter temperature

        # The wall of the housing is simulated with 3 layers. Layer 1 is the inner an layer 3 the outer layer.
        self.__l1_temperature = self.__housing.inner_layer.temperature  # K
        self.__l2_temperature = self.__housing.mid_layer.temperature  # K
        self.__l3_temperature = self.__housing.outer_layer.temperature  # K

        # ---------- Initializing Parameters ----------
        # -- Inner Air --
        # Model with p & V constant, i.e. if T rises, mass must decrease.
        # Quantities with reference to ideal gas equation
        self.__air_specific_heat = 1006  # J/kgK, cp (at constant pressure)
        self.__individual_gas_constant = self.universal_gas_constant / self.molecular_weight_air  # J/kgK
        self.__air_density = self.air_pressure / (
                self.__individual_gas_constant *298.15)  # kg/m3
        self.update_air_parameters()

        # -- Battery --
        self.__surface_area_battery = self.__storage_technology.surface_area  # in m2
        self.__mass_battery = self.__storage_technology.mass  # in kg
        self.__specific_heat_capacity_battery = self.__storage_technology.specific_heat  # in J/kgK
        self.__convection_coefficient_cell_air = self.__storage_technology.convection_coefficient  # in W/m2K

        # -- DC-DC Converter --
        # Note: in this model the DC-DC Converter is treated as an part of the battery. That means battery and DC-DC
        # converter are seen as one thermal component with the same specific heat capacity and convection coefficient.
        # For the simulation/calculation the mass, surface area and thermal losses of the DC-DC converter are getting
        # added to the according battery values.
        self.__surface_area_converter_dc_dc = self.__dc_dc_converter.surface_area  # in m2
        self.__mass_converter_dc_dc = self.__dc_dc_converter.mass  # in kg

        # -- AC-DC Converter --
        self.__surface_area_converter_ac_dc = self.__acdc_converter.surface_area  # in m2
        self.__mass_converter_ac_dc = self.__acdc_converter.mass  # in kg
        self.__specific_heat_capacity_converter_ac_dc = self.__specific_heat_capacity_battery  # in J/kgK
        self.__convection_coefficient_converter_ac_dc = self.__convection_coefficient_cell_air  # in W/m2K

        # -- calculation of thermal resistances an capacities --
        self.calculate_thermal_resistances()
        self.calculate_thermal_capacities()

        # ---------- Initializing variables and arrays for calculation ----------
        self.__ac_dc__converter_losses = 0
        self.__battery_and_dc_dc_converter_losses = 0
        self.__hvac_losses = 0
        self.__temperature_series = []
        # sum passed time keeps track of the time already simulated; also used for x_axis if plotting is wished
        self.__sum_passed_time = 0

        # ---------- Initializing variables and arrays for plotting ----------
        # arrays to store the temperatures and thermal power for multiple sample times
        if self.__developer_mode_plotting == 1:
            self.__inner_air_temperature_storage = [self.__ia_temperature]
            self.__battery_temperature_storage = [self.__battery_temperature]
            self.__converter_temperature_storage = [self.__converter_temperature_ac_dc]
            self.__l1_temperature_storage = [self.__l1_temperature]
            self.__l2_temperature_storage = [self.__l2_temperature]
            self.__l3_temperature_storage = [self.__l3_temperature]
            self.__battery_and_dc_dc_converter_loss_storage = [0]
            self.__converter_loss = [0]
            self.__zero_line_for_losses_plot = [0]

        # ---------- variables for developer mode ----------
        # times for the different sections of the code
        self.__time_for_calculate_temperature = 0
        # time_for_differential_equation is part of time_for_calculate_temperature
        self.__time_for_differential_equation = 0
        self.__time_for_calculate_thermal_power = 0

    def calculate_thermal_resistances(self):
        # all units in K/W
        # calculates thermal convection resistance between the surrounding air (sa) and  the margin of Layer 3 (l3)
        self.__sa_l3_thermal_resistance = 1 / (self.__housing.inner_layer.convection_coefficient_air *
                                               self.__housing.outer_layer.surface_area_total)
        # calculates thermal conduction resistance between the margin of Layer 3 (l3) and the mid of Layer 2 (l2)
        self.__l3_l2_thermal_resistance = self.__housing.outer_layer.thickness / \
                                          (self.__housing.outer_layer.thermal_conductivity * self.__housing.inner_layer.surface_area_total) \
                                          + 0.5 * self.__housing.mid_layer.thickness / \
                                          (self.__housing.mid_layer.thermal_conductivity * self.__housing.mid_layer.surface_area_total)
        # calculates thermal conduction resistance  between the mid of Layer 2 (l2) and the margin of Layer 1 (l1)
        self.__l2_l1_thermal_resistance = 0.5 * self.__housing.mid_layer.thickness / \
                                          (self.__housing.mid_layer.thermal_conductivity * self.__housing.mid_layer.surface_area_total) \
                                          + self.__housing.inner_layer.thickness / \
                                          (self.__housing.inner_layer.thermal_conductivity * self.__housing.inner_layer.surface_area_total)
        # calculates thermal convection resistance  between Layer 1 (l1) of the wall and the inner air (ia)
        self.__l1_ia_thermal_resistance = 1 / (self.__housing.outer_layer.convection_coefficient_air *
                                               self.__housing.inner_layer.surface_area_total)
        # calculates thermal convection resistance  between the battery (bat) and the inner air (ia)
        self.__bat_ia_thermal_resistance = 1 / (self.__convection_coefficient_cell_air *
                                                (self.__surface_area_battery + self.__surface_area_converter_dc_dc))
        # calculates thermal convection resistance  between the converter (conv) and the inner air (ia)
        self.__conv_ia_thermal_resistance = 1 / (self.__convection_coefficient_converter_ac_dc *
                                                 self.__surface_area_converter_ac_dc)

        if self.__developer_mode == 1:
            print('')
            print('-----Resistances-----')
            print('Battery-IA Resistance :', self.__bat_ia_thermal_resistance, 'K/W')
            print('Converter-IA Resistance :', self.__conv_ia_thermal_resistance, 'K/W')
            print('Wall TOTAL Thermal Resistance :', self.__l3_l2_thermal_resistance + self.__l2_l1_thermal_resistance +
                  self.__sa_l3_thermal_resistance + self.__l1_ia_thermal_resistance, 'K/W')
            print('     SA-l3 Resistance :', self.__sa_l3_thermal_resistance, 'K/W')
            print('     l3-l2 Resistance :', self.__l3_l2_thermal_resistance, 'K/W')
            print('     l2-l1 Resistance :', self.__l2_l1_thermal_resistance, 'K/W')
            print('     l1-IA Resistance :', self.__l1_ia_thermal_resistance, 'K/W')

    def calculate_thermal_capacities(self):
        # all units in J/K
        self.__battery_thermal_capacity = (self.__mass_battery + self.__mass_converter_dc_dc) * \
                                          self.__specific_heat_capacity_battery
        self.__converter_thermal_capacity = self.__mass_converter_ac_dc * self.__specific_heat_capacity_converter_ac_dc
        self.__inner_air_thermal_capacity = self.__air_mass * self.__air_specific_heat
        self.__l3_thermal_capacity = self.__housing.outer_layer.mass * self.__housing.outer_layer.specific_heat
        self.__l2_thermal_capacity = self.__housing.mid_layer.mass * self.__housing.mid_layer.specific_heat
        self.__l1_thermal_capacity = self.__housing.inner_layer.mass * self.__housing.inner_layer.specific_heat

        if self.__developer_mode == 1:
            print('')
            print('-----Capacities-----')
            print('IA Thermal Capacity :', self.__inner_air_thermal_capacity, 'J/K')
            print('Battery Capacity :', self.__battery_thermal_capacity, 'J/K')
            print('Converter Capacity :', self.__converter_thermal_capacity, 'J/K')
            print('Wall Thermal Capacity: ',
                  self.__l3_thermal_capacity + self.__l2_thermal_capacity + self.__l1_thermal_capacity, 'J/K')

    def update_air_parameters(self):
        self.__air_volume = self.__housing.internal_air_volume  # in m3
        self.__air_mass = self.__air_volume * self.__air_density  # kg

    def calculate_temperature(self, time, state: SystemState, dc_states) -> None:
        if self.__developer_mode == 1:
            start_time_calculate_temperature = ti.time()
        ambient_air_temperature = self.__ambient_thermal_model.get_temperature(time)
        self.__air_density = self.air_pressure / (self.__individual_gas_constant * state.temperature)
        self.update_air_parameters()
        calculated_time = 0
        # TODO solar radiation model
        radiation_power = 0
        hvac_losses_sample_time = []

        while calculated_time < self.__sample_time:
            calculated_time += self.__calculation_time_step
            self.__sum_passed_time += self.__calculation_time_step

            thermal_power = self.__heating_cooling.get_thermal_power()
            if self.__developer_mode == 1:
                start_time_differential_equation = ti.time()

            def equation_rhs(t, variable_array):
                # variable_array = [inner_air_temperature, battery_temperature, converter_temperature,
                # l3_temperature, l2_temperature, l1_temperature]
                # Temperature variables: inner_air_temperature, battery_temperature, converter_temperature,
                # l3_temperature, l2_temperature, l1_temperature
                # independent variable: time

                # Differential equation for change in inner air temperature
                d_by_dt_inner_air_temperature = (((variable_array[5] - variable_array[0]) / self.__l1_ia_thermal_resistance) +
                                                 ((variable_array[1] - variable_array[0]) / self.__bat_ia_thermal_resistance) +
                                                 ((variable_array[2] - variable_array[0]) / self.__conv_ia_thermal_resistance) -
                                                 thermal_power) / \
                                                self.__inner_air_thermal_capacity
                # Differential equation for change in battery temperature
                d_by_dt_battery_temperature = ((state.storage_power_loss + state.dc_power_loss) -
                                               (variable_array[1] - variable_array[0]) / self.__bat_ia_thermal_resistance) / \
                                              self.__battery_thermal_capacity
                # Differential equation for change in converter temperature
                d_by_dt_converter_temperature_ac_dc = (state.pe_losses - ((variable_array[2] - variable_array[0])
                                                                          / self.__conv_ia_thermal_resistance)) / \
                                                      self.__converter_thermal_capacity
                # Differential equation for change in L3 temperature
                d_by_dt_l3_temperature = (radiation_power +
                                          ((ambient_air_temperature - variable_array[3]) / self.__sa_l3_thermal_resistance)
                                          - ((variable_array[3] - variable_array[4]) / self.__l3_l2_thermal_resistance)) / \
                                         self.__l3_thermal_capacity
                # Differential equation for change in l2 temperature
                d_by_dt_l2_temperature = (((variable_array[3] - variable_array[4]) / self.__l3_l2_thermal_resistance) -
                                          ((variable_array[4] - variable_array[5]) / self.__l2_l1_thermal_resistance)) / \
                                         self.__l2_thermal_capacity
                # Differential equation for change in L1 temperature
                d_by_dt_l1_temperature = (((variable_array[4] - variable_array[5]) / self.__l2_l1_thermal_resistance) -
                                          ((variable_array[5] - variable_array[0]) / self.__l1_ia_thermal_resistance)) / \
                                         self.__l1_thermal_capacity

                equation_rhs_array = [d_by_dt_inner_air_temperature, d_by_dt_battery_temperature,
                                      d_by_dt_converter_temperature_ac_dc, d_by_dt_l3_temperature,
                                      d_by_dt_l2_temperature,
                                      d_by_dt_l1_temperature]
                return equation_rhs_array

            # time_interval is an array of times at which the equation get evaluated
            time_interval = [i for i in range(self.__t_eval_step, self.__calculation_time_step + self.__t_eval_step,
                                              self.__t_eval_step)]

            sol = solve_ivp(equation_rhs, (0, self.__calculation_time_step),
                            [self.__ia_temperature, self.__battery_temperature, self.__converter_temperature_ac_dc,
                             self.__l3_temperature, self.__l2_temperature, self.__l1_temperature],
                            method='BDF', t_eval=time_interval)

            if self.__developer_mode == 1:
                end_time_differential_equation = ti.time()
                self.__time_for_differential_equation += end_time_differential_equation - start_time_differential_equation

            self.__temperature_series = sol.y
            # setting current temperatures
            self.__ia_temperature = self.__temperature_series[0, -1]
            self.__battery_temperature = self.__temperature_series[1, -1]
            self.__converter_temperature_ac_dc = self.__temperature_series[2, -1]
            self.__l3_temperature = self.__temperature_series[3, -1]
            self.__l2_temperature = self.__temperature_series[4, -1]
            self.__l1_temperature = self.__temperature_series[5, -1]

            # store temperatures for plotting
            if self.__developer_mode_plotting == 1:
                self.__inner_air_temperature_storage.extend(self.__temperature_series[0])
                self.__battery_temperature_storage.extend(self.__temperature_series[1])
                self.__converter_temperature_storage.extend(self.__temperature_series[2])
                self.__l3_temperature_storage.extend(self.__temperature_series[3])
                self.__l2_temperature_storage.extend(self.__temperature_series[4])
                self.__l1_temperature_storage.extend(self.__temperature_series[5])

            # calculate thermal power
            self.calculate_thermal_power(self.__temperature_series[1])
            hvac_losses_sample_time.append(self.__heating_cooling.get_electric_power())

        #   end while   #######################################################################
        # the energy losses of the converter and hvac get calculated in kWh
        self.__ac_dc__converter_losses += state.pe_losses * ((self.__sample_time / 3600) / 1000)
        self.__battery_and_dc_dc_converter_losses += (state.storage_power_loss + state.dc_power_loss) \
                                                    * ((self.__sample_time / 3600) / 1000)
        for x in hvac_losses_sample_time:
            self.__hvac_losses += x * (1/len(hvac_losses_sample_time)) * ((self.__sample_time / 3600) / 1000)

        # setting temperature for SIMSES simulation and plotting
        self.__storage_technology.state.temperature = self.__battery_temperature

        if self.__developer_mode_plotting == 1:
            self.__battery_and_dc_dc_converter_loss_storage.append(int(state.storage_power_loss + state.dc_power_loss))
            self.__converter_loss.append(int(state.pe_losses))
            self.__zero_line_for_losses_plot.append(0)

        if self.__developer_mode == 1:
            end_time_calculate_temperature = ti.time()
            self.__time_for_calculate_temperature += end_time_calculate_temperature - start_time_calculate_temperature

        # ---------- Plotting the temperatures at the end of the simulated time ----------
        # plotting after the last complete sample time
        if (self.__developer_mode_plotting == 1 or self.__developer_mode == 1) \
                and (self.__sum_passed_time > self.__loop * (self.__end_time - self.__start_time) - self.__sample_time):
            self.plot_temperatures(state)

    def calculate_thermal_power(self, temperature_series):
        # running the HVAC and logging the time needed (if developer mode is active)
        if self.__developer_mode == 1:
            start_time_calculate_thermal_power = ti.time()

        self.__heating_cooling.run_air_conditioning(temperature_series, self.__t_eval_step)

        if self.__developer_mode == 1:
            end_time_calculate_thermal_power = ti.time()
            self.__time_for_calculate_thermal_power += end_time_calculate_thermal_power - \
                                                       start_time_calculate_thermal_power

    def plot_temperatures(self, state: SystemState):
        # testing if a suitable HVAC model is selected in the config
        try:
            test = self.__heating_cooling.get_coefficients()[0] - 5
        except TypeError:
            raise Exception('If developer mode or plotting mode is wished, this thermal model must be used with an '
                            'suitable hvac_model which has the get_coefficients() and get_plotting_arrays() methods'
                            ' implemented.')

        if abs(max(self.__heating_cooling.get_plotting_arrays()[0])) > abs(
                min(self.__heating_cooling.get_plotting_arrays()[0])):
            control_difference_max = abs(max(self.__heating_cooling.get_plotting_arrays()[0]))
        else:
            control_difference_max = abs(min(self.__heating_cooling.get_plotting_arrays()[0]))

        control_difference_mean_calculation_help = 0
        for x in self.__heating_cooling.get_plotting_arrays()[0]:
            control_difference_mean_calculation_help += x
        control_difference_mean = abs(control_difference_mean_calculation_help / len(
            self.__heating_cooling.get_plotting_arrays()[0]))

        if self.__developer_mode == 1:
            start_time_for_plot = ti.time()

        if self.__developer_mode_plotting == 1:

            # generating the time array which contains the x-coordinates for the temperatures
            t_axis_for_temperature_plot = [0] + [i for i in range(self.__t_eval_step, self.__sum_passed_time +
                                                                  self.__t_eval_step, self.__t_eval_step)]
            plt.figure(1)
            plt.subplot(411)
            print_coefficients = ('[Kp coefficient : ' + str(self.__heating_cooling.get_coefficients()[0]) +
                                  '  ;  Ki coefficient : ' + str(self.__heating_cooling.get_coefficients()[1]) +
                                  '  ;  Kd coefficient : ' + str(self.__heating_cooling.get_coefficients()[2]) +
                                  '  ;  Sample time : ' + str(self.__sample_time) + '  ;  Calculation time : ' +
                                  str(self.__calculation_time_step) + '  ;  Evaluation time : ' +
                                  str(self.__t_eval_step) + '  ;  Max Thermal Power : ' +
                                  str(self.__heating_cooling.get_max_thermal_power()) + ']')
            axes = plt.gca()
            axes.text(0, 1.5, print_coefficients,
                      transform=axes.transAxes, fontsize=12, verticalalignment='top')
            plt.plot(t_axis_for_temperature_plot, self.__inner_air_temperature_storage, label='inner_air_temperature')
            plt.plot(t_axis_for_temperature_plot, self.__battery_temperature_storage, label='battery_temperature')
            plt.plot(t_axis_for_temperature_plot, self.__converter_temperature_storage,
                     label='converter_temperature_ac_dc')
            plt.plot(t_axis_for_temperature_plot, self.__l3_temperature_storage, label='L3_temperature')
            plt.plot(t_axis_for_temperature_plot, self.__l2_temperature_storage, label='L2_temperature')
            plt.plot(t_axis_for_temperature_plot, self.__l1_temperature_storage, label='L1_temperature')
            plt.plot(t_axis_for_temperature_plot, self.__heating_cooling.get_plotting_arrays()[1],
                     'black', label='target')
            axes = plt.gca()
            axes.set_xlim([0, self.__end_time - self.__start_time])
            plt.title('Temperatures over Time')
            plt.ylabel('Temperature')
            plt.legend(loc=1)

            plt.subplot(412)
            plt.plot(t_axis_for_temperature_plot, self.__heating_cooling.get_plotting_arrays()[0],
                     label='temperature difference')
            plt.plot(t_axis_for_temperature_plot, self.__heating_cooling.get_plotting_arrays()[2]
                     , 'black',label='zero')
            axes = plt.gca()
            axes.set_xlim([0, self.__end_time - self.__start_time])
            # axes.set_ylim([-15, 15])
            plt.ylabel('Temperature Difference')
            plt.legend(loc=1)

            plt.subplot(413)
            # thermal power needs its own x_axis scale, because it gets calculated after self.__calculation_time_step
            # and not after self.__t_eval_step like the temperatures
            t_axis_for_thermal_power_plot = [0]
            j = 0
            while j * self.__calculation_time_step < self.__sum_passed_time:
                t_axis_for_thermal_power_plot.append((j + 1) * self.__calculation_time_step)
                j += 1
            plt.plot(t_axis_for_thermal_power_plot, self.__heating_cooling.get_plotting_arrays()[3],
                     label='thermal power')
            plt.plot(t_axis_for_thermal_power_plot, self.__heating_cooling.get_plotting_arrays()[4],
                     'black', label='zero')
            axes = plt.gca()
            axes.set_xlim([0, self.__end_time - self.__start_time])
            axes.set_ylim([-self.__heating_cooling.get_max_thermal_power() - 1000,
                           self.__heating_cooling.get_max_thermal_power() + 1000])
            plt.ylabel('Power')
            plt.legend(loc=1)

            plt.subplot(414)
            # battery_loss and converter_loss need their own x_axis scale, because they get calculated after each
            # sample time and not after self.__t_eval_step or self.__calculation_time_step like the temperatures
            t_axis_for_losses_plot = [0]
            n = 0
            while n * self.__sample_time < self.__sum_passed_time:
                t_axis_for_losses_plot.append((n + 1) * self.__sample_time)
                n += 1
            plt.plot(t_axis_for_losses_plot, self.__battery_and_dc_dc_converter_loss_storage, 'orange',
                     label='DC-DC converter and battery loss')
            plt.plot(t_axis_for_losses_plot, self.__converter_loss, 'g', label='AC-DC converter loss')
            plt.plot(t_axis_for_losses_plot, self.__zero_line_for_losses_plot, 'black', label='zero')
            axes = plt.gca()
            axes.set_xlim([0, self.__end_time - self.__start_time])
            if self.__developer_mode == 1:
                print_control_difference = ('[Max control difference : ' + str(control_difference_max) +
                                            '  ;  Mean control difference : ' + str(control_difference_mean) + ']')
                axes.text(0, -0.4, print_control_difference,
                          transform=axes.transAxes, fontsize=12, verticalalignment='top')
            plt.xlabel('Time')
            plt.ylabel('Losses')
            plt.legend(loc=1)

            plt.show()
        if self.__developer_mode == 1:
            end_time_for_plot = ti.time()
        if self.__developer_mode == 1:
            print()
            print('----- config settings -----')
            print('Battery Temperature target :', self.__battery_temperature_target - 273.15, '°C')
            print('Max Thermal Power :', self.__heating_cooling.get_max_thermal_power(), 'W')
            print('Kp coefficient :', self.__heating_cooling.get_coefficients()[0])
            print('Ki coefficient :', self.__heating_cooling.get_coefficients()[1])
            print('Kd coefficient :', self.__heating_cooling.get_coefficients()[2])
            print()
            print('Sample time :', int(self.__sample_time), 's')
            print('Calculation time :', self.__calculation_time_step, 's')
            print('Evaluation time :', self.__t_eval_step, 's')
            print()
            print('-----Results-----')
            print('capacity remaining (nominal) :', state.capacity, 'Wh')
            print('capacity remaining (in percent) :', state.capacity /
                  int(self.__system_config.storage_technologies['storage_1'][0]), '%')
            print('sum losses :', self.__ac_dc__converter_losses + self.__hvac_losses +
                  self.__battery_and_dc_dc_converter_losses , 'kWh')
            print('hvac losses  :', self.__hvac_losses , 'kWh')
            print('battery and dc_dc losses :', self.__battery_and_dc_dc_converter_losses , 'kWh')
            print('ac_dc losses :', self.__ac_dc__converter_losses , 'kWh')
            print()
            print('Max control difference:', control_difference_max, '°C')
            print('Mean control difference:', control_difference_mean, '°C')
            print()
            print('Time needed for plotting', end_time_for_plot - start_time_for_plot, 's')
            print('Time needed for calculate_temperature total', self.__time_for_calculate_temperature, 's')
            print('Time needed for differential equations ', self.__time_for_differential_equation, 's')
            print('Time needed for calculate_thermal power', self.__time_for_calculate_thermal_power, 's')
            print()

    def get_auxiliaries(self) -> [Auxiliary]:
        return [self.__heating_cooling]

    def get_temperature(self) -> float:
        return self.__ia_temperature

    def get_ambient_temperature(self) -> float:
        return 0.0

    def get_solar_irradiation_thermal_load(self) -> float:
        return 0.0

    def get_hvac_thermal_power(self) -> float:
        """
        returns the HVAC thermal power in W
        :return: __hvac_thermal_power as float
        """
        return 0.0

    def reset_profiles(self, ts_adapted: float) -> None:
        """
        Enables looping of the simulation beyond the original length of the time series for the AmbientThermalModel and
        SolarIrradiationModel
        """
        pass

    # def get_air_mass(self) -> float:
    #     return self.__air_mass
    #
    # def get_air_specific_heat(self) -> float:
    #     return self.__air_specific_heat

    def close(self):
        self.__housing.close()
from __future__ import annotations
import buildingenergy.thermics
import buildingenergy.solarbuilding
import buildingenergy.openweather
import buildingenergy.measurements

room_volume = 56
co2_breath_production = 7
body_metabolism = 100
laptop_power_threshold_for_occupancy = 17
concentrationCO2out = 395
heater_power_per_degree = 50
heater_max_power = 1500
outdoor_infiltration = 0.0035
window_open_infiltration = 0.01
corridor_infiltration = 0.0035
door_open_infiltration = 0.007
solar_factor = 0.85
window_direction = -13
solar_mask = buildingenergy.solarbuilding.WindowMask((-73+window_direction, 73+window_direction), (20, 60))

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
corridor_wall.add_infiltration(corridor_infiltration)
corridor_wall.add_max_opening_air_flow(door_open_infiltration)
Rcor_0 = corridor_wall.R(0)
Rcor_1 = corridor_wall.R(1)
print(corridor_wall)

# outdoor wall
west_glass_surface = 2 * 130e-2 * 52e-2 + 27e-2 * 52e-2 + 72e-2 * 52e-2
east_glass_surface = 36e-2 * 56e-2
windows_surface = west_glass_surface + east_glass_surface
glass_surface = windows_surface
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
external_wall.add_infiltration(outdoor_infiltration)
external_wall.add_max_opening_air_flow(window_open_infiltration)
Rout_0 = external_wall.R(0)
Rout_1 = external_wall.R(1)
print(external_wall)

# slab
slab_effective_thickness = 11.9e-2
slab_surface = (309e-2 + 20e-3 + 34e-2) * (406e-2 + internal_wall_thickness) + 408e-2 * (273e-2 - 60e-2) - 315e-2 * (34e-2 + 20e-3) - (185e-3 + internal_wall_thickness) * 50e-2
slab = buildingenergy.thermics.Composition(first_layer_indoor=True, last_layer_indoor=None, position='horizontal')
slab.add_layer('concrete', slab_effective_thickness/2)
floor_inertia1 = buildingenergy.thermics.Wall('slab')
floor_inertia1.add_composition(slab, slab_surface)
print(floor_inertia1)
Ci1 = buildingenergy.thermics.Composition.volumic_masses['concrete'] * buildingenergy.thermics.Composition.specific_heats['concrete'] * slab_surface * slab_effective_thickness
Ri1 = floor_inertia1.R()

slab_effective_thickness = 2.43e-2
slab.add_layer('concrete', slab_effective_thickness/2)
floor_inertia2 = buildingenergy.thermics.Wall('slab')
floor_inertia2.add_composition(slab, slab_surface)
print(floor_inertia1)
Ci2 = buildingenergy.thermics.Composition.volumic_masses['concrete'] * buildingenergy.thermics.Composition.specific_heats['concrete'] * slab_surface * slab_effective_thickness
Ri2 = floor_inertia2.R()
        

# load values for variables
data_container = buildingenergy.measurements.DataContainer('h358data_winter2015-2016.csv', skiprows=0, nrows=60*24)
site_weather_data = buildingenergy.openweather.OpenWeatherMapJsonReader('grenoble_weather2015-2019.json', from_stringdate=data_container.starting_stringdatetime, to_stringdate=data_container.ending_stringdatetime, sea_level_in_meter=330, albedo=.1).site_weather_data
solar_mask = buildingenergy.solarbuilding.WindowMask((-86, 60), (20, 68))
office_solar_gain = buildingenergy.solarbuilding.Building(site_weather_data)
office_solar_gain.add_window('main', surface=2, exposure_in_deg=-13, slope_in_deg=90, solar_factor=0.85, window_mask=solar_mask)
phi_sun, _ = office_solar_gain.solar_gain
Tout = office_solar_gain.site_weather_data.get('temperature')
stringdate_days, average_temperature_days, min_temperature_days, max_temperature_days, dju_days = site_weather_data.day_degrees(18)
office_solar_gain.generate_xls('officeH358')

datetime = data_container.get_variable('datetime')
office_CO2_concentration = data_container.get_variable('office_CO2_concentration')
corridorCCO2 = data_container.get_variable('corridor_CO2_concentration')
Toffice_reference = data_container.get_variable('Toffice_reference')
Tcorridor = data_container.get_variable('Tcorridor')
power_stephane = data_container.get_variable('power_stephane')
power_khadija = data_container.get_variable('power_khadija')
power_audrey = data_container.get_variable('power_audrey')
power_stagiaire = data_container.get_variable('power_stagiaire')
power_block_east = data_container.get_variable('power_block_east')
power_block_west = data_container.get_variable('power_block_west')
total_electric_power = []
for i in range(len(datetime)):
    total_electric_power.append(power_block_east[i] + power_block_west[i])
window_opening = data_container.get_variable('window_opening')
door_opening = data_container.get_variable('door_opening')
dT_heat = data_container.get_variable('dT_heat')

occupancy = []
for k in range(len(datetime)):
    occupancy.append((power_stephane[k] > laptop_power_threshold_for_occupancy) + (power_khadija[k] > laptop_power_threshold_for_occupancy) + (power_audrey[k] > laptop_power_threshold_for_occupancy) + (power_stagiaire[k] > laptop_power_threshold_for_occupancy))

gain_sun =  [phi_sun[k] * solar_factor * glass_surface for k in range(len(datetime))]
gain_met =  [occupancy[k] * body_metabolism for k in range(len(datetime))]
Pin =  [phi_sun[k] * solar_factor * glass_surface + total_electric_power[k] + occupancy[k] * body_metabolism + heater_power_per_degree * dT_heat[k] for k in range(len(datetime))]

office_simulated_temperature = []
office_simulated_CO2 = []
for k in range(len(datetime)):
    QW = external_wall._infiltration_air_flow + (external_wall._max_opening_air_flow - external_wall._infiltration_air_flow) * window_opening[k]
    QD = corridor_wall._infiltration_air_flow + (corridor_wall._max_opening_air_flow - corridor_wall._infiltration_air_flow) * door_opening[k]
    R = 1 / (1 / external_wall.R(window_opening[k]) + 1 / corridor_wall.R(door_opening[k]))
    office_simulated_temperature.append((Tcorridor[k] / corridor_wall.R(door_opening[k]) + (Tout[k]) / external_wall.R(window_opening[k]) + Pin[k]) * R)
    office_simulated_CO2.append((QW*concentrationCO2out + QD*corridorCCO2[k] + co2_breath_production*occupancy[k]) / (QW+QD))


data_container.add_external_variable('gain_sun', gain_sun)
data_container.add_external_variable('gain_met', gain_met)
data_container.add_external_variable('Pin', Pin)
data_container.add_external_variable('office_simulated_temperature', office_simulated_temperature)
data_container.add_external_variable('office_simulated_CO2', office_simulated_CO2)
data_container.plot()

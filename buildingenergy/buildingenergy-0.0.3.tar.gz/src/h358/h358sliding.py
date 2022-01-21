from __future__ import annotations

import buildingenergy.linreg as linreg
import h358measurements
import buildingenergy.measurements
import os, sys, shutil

if os.path.isdir('log'):
    shutil.rmtree('log')
os.mkdir('log')
sys.stdout = open("log/h358sliding.md", 'w')

data_container = h358measurements.DataContainer('h358data_winter2015-2016.csv', skiprows=0, nrows=None)


print("# sliding window")

sample_time_seconds = 3600
offset = True
minimum_input_delay = 0
inputs_maximum_delays = (2, 0, 0, 1, 2, 1, 1)
ouput_maximum_delay = 4
slice_size = 24  # size of the time slice (default: 24) usually corresponding to one day
minimum_slices = 12  # the initial number of time slices used to learn parameters. If too small, it will generate a singular matrix error
slice_memory = 24 * 7  # None for no slice memory limit

print('* sample_time_seconds:', sample_time_seconds)
print('* offset:', offset)
print('* minimum_input_delay:', minimum_input_delay)
print('* inputs_maximum_delays:', inputs_maximum_delays)
print('* ouput_maximum_delay:', ouput_maximum_delay)
print('* slice_size:', slice_size)
print('* minimum_slices:', minimum_slices)
print('* slice_memory:', slice_memory)

input_labels = ('Tout', 'window_opening', 'door_opening', 'total_electric_power', 'phi_sun', 'dT_heat', 'occupancy')  # 'Tcorridor',
output_label = 'Toffice_reference'
#input_labels = ('corridor_CO2_concentration', 'window_opening', 'door_opening', 'occupancy')
#output_label = 'office_CO2_concentration'


linear_regression = linreg.LinearRegression(input_labels=input_labels, output_label=output_label, minimum_input_delay=minimum_input_delay, inputs_maximum_delays=inputs_maximum_delays, output_maximum_delay=ouput_maximum_delay, offset=offset)

sliding_inputs = [data_container.data[data_label] for data_label in input_labels]
sliding_output = data_container.data[output_label]
output_estimated_sliding = linear_regression.sliding(sliding_inputs, sliding_output, time_slice_size=slice_size, minimum_time_slices=minimum_slices, time_slice_memory=slice_memory)
data_container.add_external_variable('%s_estimated' % output_label, output_estimated_sliding)

plot_saver_sliding = buildingenergy.measurements.PlotSaver(data_container)
plot_saver_sliding.time_plot(['%s' % output_label, '%s_estimated' % output_label], 'log/output_sliding')
print('* Estimated output at sliding')
print('![Sliding output](output_sliding.png)')
linear_regression.error_analysis(sliding_inputs, sliding_output, output_estimated_sliding)

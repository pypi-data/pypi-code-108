"""ARX model for H358 office.

Author: stephane.ploix@grenoble-inp.fr
"""
import os
import shutil
import sys
import buildingenergy.linreg as linreg
import h358measurements
import buildingenergy.measurements


if os.path.isdir('log'):
    shutil.rmtree('log')
os.mkdir('log')
sys.stdout = open("log/linreg.md", 'w')

training_data_container = h358measurements.DataContainer('h358data_winter2015-2016.csv', skiprows=0, nrows=24*60)

print("# Linear Regression")

######## tuning parameter zone #######
sample_time_seconds = 3600
offset = True
minimum_input_delay = 0
inputs_maximum_delays = (2, 0, 0, 0, 2, 1, 1)
ouput_maximum_delay = 4
ratio_learning = 2 / 3
######################################

print('* sample_time_seconds:', sample_time_seconds)
print('* offset:', offset)
print('* minimum_input_delay:', minimum_input_delay)
print('* inputs_maximum_delays:', inputs_maximum_delays)
print('* ouput_maximum_delay:', ouput_maximum_delay)
print('* ratio_learning:', ratio_learning)

input_labels = ('Tout', 'window_opening', 'door_opening', 'total_electric_power', 'phi_sun', 'dT_heat', 'occupancy')  # 'Tcorridor',
output_label = 'Toffice_reference'
# input_labels = ('corridor_CO2_concentration', 'window_opening', 'door_opening', 'occupancy')
# output_label = 'office_CO2_concentration'

print('## Training')

linear_regression = linreg.LinearRegression(input_labels=input_labels, output_label=output_label, minimum_input_delay=minimum_input_delay, inputs_maximum_delays=inputs_maximum_delays, output_maximum_delay=ouput_maximum_delay, offset=offset)

training_inputs = [training_data_container.data[data_label] for data_label in input_labels]
training_output = training_data_container.data[output_label]
linear_regression.learn(training_inputs, training_output)

print('## model')
print(linear_regression)
linear_regression.plot_zeros_poles()

output_training = linear_regression.simulate(training_inputs, training_output)

print('## impacts')
print(linear_regression)

linear_regression.error_analysis(training_inputs, training_output, output_training)


print('## Testing')
testing_data_container = h358measurements.DataContainer('h358data_winter2015-2016.csv', skiprows=0, nrows=None)
testing_inputs = [testing_data_container.data[data_label] for data_label in input_labels]
testing_output = testing_data_container.data[output_label]
output_estimated = linear_regression.simulate(testing_inputs, testing_output)
testing_data_container.add_external_variable(output_label + '_estimated', output_estimated)


opening_closed = [0 for _ in testing_data_container.data['window_opening']]
opening_opened = [1 for _ in testing_data_container.data['window_opening']]
testing_data_container.add_external_variable('window_opening_closed', [0 for _ in testing_data_container.data['window_opening']])
testing_data_container.add_external_variable('window_opening_opened', [1 for _ in testing_data_container.data['window_opening']])
testing_data_container.add_external_variable('door_opening_closed', [0 for _ in testing_data_container.data['door_opening']])
testing_data_container.add_external_variable('door_opening_opened', [1 for _ in testing_data_container.data['door_opening']])


plot_saver_testing = buildingenergy.measurements.PlotSaver(testing_data_container)
plot_saver_testing.time_plot(['%s'%output_label,'%s_estimated'%output_label], 'log/output_testing')

print('* Estimated %s at testing' % output_label)
print('![Testing %s](output_testing.png)' % output_label)
linear_regression.error_analysis(testing_inputs, testing_output, output_estimated)

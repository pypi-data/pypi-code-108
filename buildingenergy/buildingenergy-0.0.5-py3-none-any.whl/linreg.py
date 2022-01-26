"""ARX design helper.

Author: stephane.ploix@g-scop.grenoble-inp.fr
"""

import copy
import math
import matplotlib
import matplotlib.pyplot
import numpy
import numpy.linalg


class LinearRegression:
    """General class to design ARX model matching measurement data."""

    def __init__(self, input_labels, output_label, minimum_input_delay, inputs_maximum_delays, output_maximum_delay, offset=False):
        """Estimate linear regression coefficients for a dataset.

        The meta-parameters for tuning the ARX model structre are:
            offset = True
            minimum_input_delay = 1
            inputs_maximum_delays = [2 3] (if a single int value, 4 for instance, is used, it would be equal to [4 4])
            ouput_maximum_delay = 3
        we can get the following linear regression:
            y{k} = c1 y{k-1} + c2 y{k-2} + c3 y{k-3} (ouput_maximum_delay)
                ...+ c4 u1{k-1} (minimum_input_delay) + c5 u1{k-2} (inputs_maximum_delays[0])
                ...+ c6 u2{k-1} (minimum_input_delay) + c7 u2{k-2} + c8 u2{k-3} (inputs_maximum_delays[1])
                ...+ c9

        :param input_label: input variable names
        :type input_label: list[str]
        :param output_label: output variable name
        :type output_label: list[str]
        :param minimum_input_delay: int standing for the delay_order variable represents the time delay to the system
        :type minimum_input_delay: int
        :param inputs_maximum_delays: int or list standing for the num_orders variable represents the order for the different inputs
        :type inputs_maximum_delays: int or list[int]
        :param output_maximum_delay: int standing for the den_order variable represents the order for the output
        :type outputs_maximum_delays: int or list[int]
        :param offset: will search for an offset constant value if True
        :type offset: bool
        """
        self.__input_labels = input_labels
        self.__number_of_inputs = len(input_labels)
        self.__output_label = output_label
        self.__offset = offset
        if type(inputs_maximum_delays) == int:
            inputs_maximum_delays = [inputs_maximum_delays for i in range(len(input_labels))]
        self.__inputs_maximum_delays = [max(minimum_input_delay, num_order) for num_order in inputs_maximum_delays]
        self.__output_maximum_delay = output_maximum_delay
        self.__input_minimum_delay = minimum_input_delay
        self.__output_delay_parameters: dict[int, float] = dict()
        self.__inputs_delay_parameters: dict[int, float] = [dict() for _ in range(self.__number_of_inputs)]
        self.__offset_value: float = 0
        self.__output_delay_impacts = {delay: 0 for delay in self.__output_delay_parameters}
        self.__inputs_delay_impacts = [{delay: 0 for delay in self.__inputs_delay_parameters[i]} for i in range(self.__number_of_inputs)]
        self.__offset_impact = 0
        self.__total_impact = 0

    def learn(self, list_of_input_values, output_values):
        """Estimate the parameters of the linear regression according to the structure specified in the initializer.

        :param list_of_input_values: list of variable data to be used for input variables where size = number of input variables x number of data
        :type list_of_input_values: list[list[float]]
        :param output_values: list of variable data to be used for output variables where size = number of data
        :type output_values: list[float]
        """
        __number_of_values = len(output_values)
        __Y_matrix, __X_matrix = list(), list()
        for k in range(max(self.__output_maximum_delay, max(self.__inputs_maximum_delays)), __number_of_values):
            __X_matrix_row = list()
            __Y_matrix.append(output_values[k])
            for i in range(0, self.__output_maximum_delay):
                __X_matrix_row.append(-output_values[k-i-1])
            for j in range(self.__number_of_inputs):
                for i in range(self.__inputs_maximum_delays[j] - self.__input_minimum_delay + 1):
                    __X_matrix_row.append(list_of_input_values[j][k - i - self.__input_minimum_delay])
            if self.__offset:
                __X_matrix_row.append(1)
            __X_matrix.append(__X_matrix_row)

        __X_matrix = numpy.matrix(__X_matrix)
        __Y_matrix = numpy.matrix(__Y_matrix).transpose()

        parameters = (numpy.linalg.inv(__X_matrix.transpose() * __X_matrix) * __X_matrix.transpose() * __Y_matrix).squeeze().tolist()[0]
        self.__output_delay_parameters: dict[int, float] = dict()
        for i in range(self.__output_maximum_delay):
            self.__output_delay_parameters[i + 1] = -parameters[i]

        self.__inputs_delay_parameters: list[dict[int, float]] = [dict() for _ in range(self.__number_of_inputs)]
        parameters_index = self.__output_maximum_delay
        for i in range(self.__number_of_inputs):
            for j in range(0, self.__inputs_maximum_delays[i] - self.__input_minimum_delay + 1):
                self.__inputs_delay_parameters[i][j + self.__input_minimum_delay] = parameters[parameters_index]
                parameters_index += 1
        if self.__offset:
            self.__offset_value = parameters[-1]
        else:
            self.__offset_value = 0

    @property
    def input_delay_parameters(self):
        """Estimate parameter values multiplying to input variables.

        :return: list of dictionaries corresponding to each input with delay as key and parameter as value
        :rtype: list[dict[int, float]]
        """
        return self.__inputs_delay_parameters

    @input_delay_parameters.setter
    def input_delay_parameters(self, input_delay_parameters):
        """Set the parameter values multiplying to input variables.

        :param input_delay_parameters: list of dictionaries corresponding to each input with delay as key and parameter as value
        :type input_delay_parameters: list[dict[int, float]]
        """
        self.__input_delay_parameters = input_delay_parameters

    @property
    def output_delay_parameters(self):
        """Estimate parameter values multiplying to output variables.

        :return: dictionary corresponding  with delay as key and parameter as value.
        :rtype: dict[int, float]
        """
        return self.__output_delay_parameters

    @output_delay_parameters.setter
    def output_delay_parameters(self, output_delay_parameters):
        """Set the parameter values multiplying to output variables.

        :param output_delay_parameters: dictionary corresponding  with delay as key and parameter as value
        :type output_delay_parameters: list[float]
        """
        self.__output_delay_parameters = output_delay_parameters

    @property
    def offset_value(self) -> float:
        """Get the resulting offset value.

        :return: offset value. If offset has been set to false in the initializer, it will return 0.
        :rtype: float
        """
        return self.__offset_value

    @offset_value.setter
    def offset_value(self, offset_value):
        """Set an offset value.

        :param offset_value: offset value
        :type offset_value: float
        """
        self.__offset_value = offset_value

    @property
    def maximum_delay(self) -> int:
        """Estimate the the maximum delay considering delays in output but also in all inputs.

        :return: the maximum delay considering delays in output but also in all inputs
        :rtype: int
        """
        __maximum_delay = max(self.__output_delay_parameters)
        for input_delay_parameters in self.__inputs_delay_parameters:
            __maximum_delay = max(__maximum_delay, max(input_delay_parameters))
        return __maximum_delay

    def simulate(self, list_of_inputs_values, list_of_initial_output_values=None):
        """Simulate the ouput response using input values and estimated (with learn) linear regression.

        :param list_of_inputs_values: list of variable data to be used for input variables where size = number of input variables x number of data
        :type list_of_inputs_values: list[list[float]]
        :param list_of_initial_output_values: list of variable data to be used for output variables to initialize the linear regression, where size >= maximum delay (values corresponding to index > maximum delay are ignored). If an int is provided, the values will be iniatized with it and None, 0 will be used. Default to None
        :type list_of_initial_output_values: list[float]
        :return: simulated output with learnt linear regression
        :rtype: list[float]
        """
        number_of_values = len(list_of_inputs_values[0])
        if list_of_initial_output_values is None:
            estimated_output_values = [0 for i in range(self.maximum_delay+1)]
        elif type(list_of_initial_output_values) == float or type(list_of_initial_output_values) == int:
            estimated_output_values = [list_of_initial_output_values for i in range(self.maximum_delay + 1)]
        else:
            estimated_output_values = [list_of_initial_output_values[i] for i in range(self.maximum_delay+1)]
        self.__output_delay_impacts = {delay:0 for delay in self.__output_delay_parameters}
        self.__inputs_delay_impacts = [{delay:0 for delay in self.__inputs_delay_parameters[i]} for i in range(self.__number_of_inputs)]
        self.__offset_impact = 0
        self.__total_impact = 0
        for k in range(self.maximum_delay+1, number_of_values):
            estimated_output_value = 0
            for output_delay in self.__output_delay_parameters:
                term = self.__output_delay_parameters[output_delay] * estimated_output_values[k-output_delay]
                estimated_output_value += term
                self.__output_delay_impacts[output_delay] += abs(term)
                self.__total_impact += abs(term)
            for i in range(self.__number_of_inputs):
                for input_delay in self.__inputs_delay_parameters[i]:
                    term = self.__inputs_delay_parameters[i][input_delay] * list_of_inputs_values[i][k - input_delay]
                    estimated_output_value += term
                    self.__inputs_delay_impacts[i][input_delay] += abs(term)
                    self.__total_impact += abs(term)
            estimated_output_values.append(estimated_output_value + self.__offset_value)
            self.__offset_impact += abs(self.__offset_value)
            self.__total_impact += abs(self.__offset_value)
        return estimated_output_values

    def sliding(self, list_of_inputs_values, list_of_output_values, time_slice_size=24, minimum_time_slices=15, time_slice_memory: int = None, log: bool = True):
        """Simulate with sliding window jumping from time slice to time slice to learn new parameters of linear regression and predict output.

        :param list_of_inputs_values: list of variable data to be used for input variables where size = number of input variables x number of data
        :type list_of_inputs_values: list[list[float]]
        :param list_of_output_values: list of variable data to be used for output variables to initialize the linear regression, where size >= maximum delay (values corresponding to index > maximum delay are ignored). If an int is provided, the values will be iniatized with it and None, 0 will be used
        :type list_of_output_values: list[float]
        :param time_slice_size: size of the time slice (default: 24) usually corresponding to one day
        :type time_slice_size: int
        :param minimum_time_slices: the initial number of time slices used to learn parameters. If too small, it will generate a singular matrix error. Default to 15
        :type minimum_time_slices: int
        :param time_slice_memory: maximum number of time slices kept for learning parameters. If smaller then minimum_time_slices, time_slice_memory will be set to minimum_time_slices. Default is None, which means no memory limitation. Default to None
        :type time_slice_memory: int
        :param log: log results if True. Default is True
        :type log: bool
        :return: estimated output simulated per time slice
        :rtype: list[float]
        """
        if time_slice_memory is not None:
            time_slice_memory = max(time_slice_memory, minimum_time_slices)
        inputs_slices = [LinearRegression.__extract_inputs(k, (k + 1) * time_slice_size, list_of_inputs_values) for k in range(0, minimum_time_slices * time_slice_size, time_slice_size)]
        outputs_slices = [LinearRegression.__extract_outputs(k, (k + 1) * time_slice_size, list_of_output_values) for k in range(0, minimum_time_slices * time_slice_size, time_slice_size)]
        estimated_outputs = list_of_output_values[0:minimum_time_slices * time_slice_size].copy()
        for k in range(minimum_time_slices * time_slice_size, len(list_of_output_values), time_slice_size):
            merged_inputs = LinearRegression.__merge_inputs(inputs_slices)
            merged_outputs = LinearRegression.__merge_outputs(outputs_slices)
            self.learn(merged_inputs, merged_outputs)
            if log:
                print(self)
            inputs_slices.append(LinearRegression.__extract_inputs(k, k + time_slice_size, list_of_inputs_values))
            all_estimated_outputs = self.simulate(LinearRegression.__merge_inputs(inputs_slices), estimated_outputs)
            estimated_outputs.extend(all_estimated_outputs[-time_slice_size:])
            outputs_slices.append(LinearRegression.__extract_outputs(k, k + time_slice_size, list_of_output_values))
            if time_slice_memory is not None and len(outputs_slices) > time_slice_memory:
                inputs_slices = inputs_slices[-time_slice_memory:]
                outputs_slices = outputs_slices[-time_slice_memory:]
        return estimated_outputs[0:len(list_of_output_values)]

    @staticmethod
    def __extract_inputs(from_k, to_k, list_of_input_values):
        """Extract a slice of time for the input data.

        :param from_k: beginning of the time slice
        :type from_k: int
        :param to_k: end of the time slice
        :type to_k: int
        :param list_of_input_values: input data
        :type list_of_input_values: list[list[float]]
        :return: time slice of the input data
        :rtype: list[float]
        """
        extracted_inputs = list()
        for i in range(len(list_of_input_values)):
            extracted_inputs.append(list_of_input_values[i][from_k:to_k])
        return extracted_inputs

    @staticmethod
    def __extract_outputs(from_k: int, to_k: int, list_of_output_values):
        """Extract a slice of time for the outout data.

        :param from_k: beginning of the time slice
        :type from_k: int
        :param to_k: end of the time slice
        :type to_k: int
        :param list_of_input_values: output data
        :type list_of_output_values: list[float]
        :return: time slice of the output data
        :rtype: list[float]
        """
        return list_of_output_values[from_k:to_k]

    @staticmethod
    def __merge_inputs(list_of_inputs_slices):
        """Merge several input time slices into a single one.

        :param list_of_inputs_slices: time slices
        :type list_of_inputs_slices: list[list[list[float]]]
        :return: an unique time slice, which is the concatenation of the slices, respected to order with which they have been provided
        :rtype: list[list[float]]
        """
        merged_inputs = copy.deepcopy(list_of_inputs_slices[0])
        for j in range(1, len(list_of_inputs_slices)):
            for i in range(len(list_of_inputs_slices[0])):
                merged_inputs[i].extend(list_of_inputs_slices[j][i])
        return merged_inputs

    @staticmethod
    def __merge_outputs(list_of_output_slices):
        """Merge several output time slices into a single one.

        :param list_of_ioutput_slices: time slices
        :return: an unique time slice, which is the concatenation of the slices, respected to order with which they have been provided
        :rtype: list[float]
        """
        merged_outputs = copy.deepcopy(list_of_output_slices[0])
        for j in range(1, len(list_of_output_slices)):
            merged_outputs.extend(list_of_output_slices[j])
        return merged_outputs

    def __str__(self):
        """Return a descriptive string of the linear regression.

        :return: text representation
        """
        string = '%s{k} = ' % (self.__output_label)
        for delay in self.__output_delay_parameters:
            if self.__output_delay_parameters[delay] > 0:
                string += '+%f %s{k-%i} ' % (self.__output_delay_parameters[delay], self.__output_label, delay)
            else:
                string += '%f %s{k-%i} ' % (self.__output_delay_parameters[delay], self.__output_label, delay)
            if self.__total_impact != 0:
                string += '(%.2f%%)' % (100 * self.__output_delay_impacts[delay] / self.__total_impact)
        for i in range(self.__number_of_inputs):
            string += '\n\t\t\t...'
            for delay in self.__inputs_delay_parameters[i]:
                if self.__inputs_delay_parameters[i][delay] > 0:
                    if delay != 0:
                        string += '+%f %s{k-%i} ' % (self.__inputs_delay_parameters[i][delay], self.__input_labels[i], delay)
                    else:
                        string += '+%f %s{k} ' % (self.__inputs_delay_parameters[i][delay], self.__input_labels[i])
                else:
                    if delay != 0:
                        string += '%f %s{k-%i} ' % (self.__inputs_delay_parameters[i][delay], self.__input_labels[i], delay)
                    else:
                        string += '%f %s{k} ' % (self.__inputs_delay_parameters[i][delay], self.__input_labels[i])
                if self.__total_impact != 0:
                    string += '(%.2f%%)' % (100 * self.__inputs_delay_impacts[i][delay] / self.__total_impact)
        if self.__offset:
            if self.__offset_value > 0:
                string += '\n\t\t\t +%f' % self.__offset_value
            elif self.__offset_value < 0:
                string += '\n\t\t\t %f' % self.__offset_value
            if self.__offset_value != 0 and self.__total_impact != 0:
                string += '(%.2f%%)' % (100 * self.__offset_impact / self.__total_impact)
        return string

    def error_analysis(self, list_of_inputs_values, list_of_actual_output_values, list_of_estimated_output_values, maxlags=10, folder_name='log'):
        """Analyse the error of estimation by characterizing error, and analyzing correlations with input and auto-correlation of the output.

        :param list_of_inputs_values: input data values
        :type list_of_inputs_values: list[list[float]]
        :param list_of_actual_output_values: actual recorded output values
        :type list_of_actual_output_values: list[float]
        :param list_of_estimated_output_values: estimated values with the learnt linear regression
        :type list_of_estimated_output_values: list[float]
        :param maxlags: optional parameter used for cross correlation, default is 10.
        :type maxlags: int
        """
        number_of_parameters = len(self.__output_delay_parameters)
        for i in range(self.__number_of_inputs):
            number_of_parameters += len(self.__inputs_delay_parameters[i])
        if self.__offset:
            number_of_parameters += 1
        number_of_data = len(list_of_actual_output_values)
        output_errors = [list_of_actual_output_values[_] - list_of_estimated_output_values[_] for _ in range(number_of_data)]
        loss_function = (sum([error ** 2 for error in output_errors]) / len(output_errors)) / 2
        akaike_value = (1 + number_of_parameters / len(output_errors)) / (1 - number_of_parameters / len(output_errors)) * loss_function
        print('* Average output error = %f' % (sum(output_errors) / len(output_errors)))
        print('* Average absolute output error = %f' % (sum([abs(error) for error in output_errors]) / len(output_errors)))
        print('* LOSS function = %f' % loss_function)
        print('* AKAIKE value = %f' % akaike_value)
        print('* Max output error = %f' % max(output_errors))
        print('* Min output error = %f' % min(output_errors))
        print('* Standard deviation for output error = %f' % numpy.std(output_errors))
        sorted_output_errors = output_errors.copy()
        sorted_output_errors.sort()
        output_errors10 = sorted_output_errors[0: int(number_of_data / 10)]
        output_errors90 = sorted_output_errors[number_of_data - int(number_of_data/10): number_of_data]
        print('* 10%% lowest error average = %f' % (sum(output_errors10)/len(output_errors10)))
        print('* 90%% highest error average = %f' % (sum(output_errors90)/len(output_errors10)))

        fig = matplotlib.pyplot.figure()
        fig.suptitle('Output error Histogram')
        axes = fig.add_subplot(1, 1, 1)
        axes.hist(output_errors, bins=50)
        axes.set_ylabel('Frequency')
        fig.tight_layout()
        matplotlib.pyplot.savefig(folder_name+'/histogram.png')
        print('* Histogram')
        print('![histogram](histogram.png)')
        number_of_rows = math.ceil(math.sqrt(self.__number_of_inputs))
        number_of_columns = math.ceil(math.sqrt(self.__number_of_inputs))
        fig = matplotlib.pyplot.figure()
        fig.suptitle('trend analysis')
        for i in range(self.__number_of_inputs):
            axes1 = fig.add_subplot(number_of_rows, number_of_columns, i + 1)
            axes1.set_xlabel('input' + str(i))
            axes1.set_xlabel('time')
            axes1.set_ylabel('output errors', color='tab:red')
            axes1.plot([i for i in range(number_of_data)], output_errors, color='tab:red')
            axes1.tick_params(axis='y', labelcolor='tab:red')
            axes1.grid()
            axes2 = axes1.twinx()
            axes2.set_ylabel(self.__input_labels[i], color='tab:blue')
            axes2.plot([i for i in range(number_of_data)], list_of_inputs_values[i], color='tab:blue')
            axes2.tick_params(axis='y', labelcolor='tab:blue')
        fig.tight_layout()
        matplotlib.pyplot.savefig(folder_name+'/trends.png')
        print('* Trends')
        print('![trends](trends.png)')

        fig, axes = matplotlib.pyplot.subplots()  # auto-correlation
        fig.suptitle("Auto-correlation error")
        axes.acorr(output_errors, normed=True, usevlines=True, maxlags=maxlags)
        axes.set_xlim([-maxlags - 0.5, maxlags + 0.5])
        axes.grid()
        fig.tight_layout()
        matplotlib.pyplot.savefig(folder_name+'/autocorrelations.png')
        print('* Auto-correlations error')
        print('![correlations](autocorrelations.png)')

        fig, axes = matplotlib.pyplot.subplots()
        fig.suptitle('Cross correlation inputs-error analysis')
        for i in range(self.__number_of_inputs):
            axes = fig.add_subplot(number_of_rows, number_of_columns, i + 1)
            axes.set_xlabel(self.__input_labels[i])
            axes.xcorr(output_errors, list_of_inputs_values[i], normed=True, usevlines=True, maxlags=maxlags)
            axes.set_xlim([-maxlags - 0.5, 0.5])
            axes.grid()
        fig.tight_layout()
        matplotlib.pyplot.savefig(folder_name+'/cross-correlations.png')
        print('* Cross correlations inputs-errors')
        print('![correlations](cross-correlations.png)')

    def plot_zeros_poles(self, folder_name='log'):
        """Plot the zeros (roots of the numerator) and the poles (roots of the denominator) in a single figure with zeros as 'o' and poles as 'x'.

        The resulting figure is saved as 'log/zeros-poles.png' and a markdown string is returned on the standard output stream (with print).
        """
        print('## zeros-poles analysis')
        print('### poles')
        denominator = [0 for _ in range(self.maximum_delay + 1)]
        denominator[0] = 1
        for delay in self.__output_delay_parameters:
            denominator[delay] = - self.__output_delay_parameters[delay]
        poles = numpy.roots(denominator)
        zeros = list()
        for i in range(len(self.__input_labels)):
            print('### zeros for input %s' % self.__input_labels[i])
            numerator = [0 for j in range(self.maximum_delay + 1)]
            for delay in self.__inputs_delay_parameters[i]:
                numerator[delay] = self.__inputs_delay_parameters[i][delay]
            zeros.append(numpy.roots(numerator))
            print('* ', zeros[-1])

        number_of_plots = len(self.__input_labels)
        number_of_rows = math.floor(math.sqrt(number_of_plots))
        number_of_columns = math.ceil(number_of_plots / number_of_rows)
        fig = matplotlib.pyplot.figure()
        fig.suptitle('zeros-poles analysis')
        for i in range(0, len(self.__input_labels)):
            axes = fig.add_subplot(number_of_rows, number_of_columns, i + 1)
            axes.set_xlabel(self.__input_labels[i])
            # create the unit circle
            create_unit_circle = matplotlib.patches.Circle((0, 0), radius=1, fill=False, color='black', ls='dashed')
            axes.add_patch(create_unit_circle)
            # Plot the zeros and set marker properties
            plot_zeros = axes.plot(zeros[i].real, zeros[i].imag, 'go', ms=10)
            matplotlib.pyplot.setp(plot_zeros, markersize=10.0, markeredgewidth=1.0, markeredgecolor='k', markerfacecolor='g')
            # Plot the poles and set marker properties
            plot_poles = axes.plot(poles.real, poles.imag, 'rx', ms=10)
            matplotlib.pyplot.setp(plot_poles, markersize=12.0, markeredgewidth=3.0, markeredgecolor='r', markerfacecolor='r')
            axes.spines['left'].set_position('center')
            axes.spines['bottom'].set_position('center')
            axes.spines['right'].set_visible(False)
            axes.spines['top'].set_visible(False)
            # set the ticks
            radius = 1.5
            axes.axis('scaled')
            axes.axis([-radius, radius, -radius, radius])
            ticks = [-1, -.5, .5, 1]
            matplotlib.pyplot.xticks(ticks)
            matplotlib.pyplot.yticks(ticks)
            axes.grid()
        fig.tight_layout()
        matplotlib.pyplot.savefig(folder_name+'/zeros-poles.png')
        print('### Graphical representation')
        print('![zeros-poles](zeros-poles.png)')

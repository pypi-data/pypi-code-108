"""A module that contains a data container of on-site measurements.

Author:  stephane.ploix@g-scop.grenoble-inp.fr
"""
import pandas
import tkinter as tk
from buildingenergy import timemg
import matplotlib
import matplotlib.pyplot
import matplotlib.dates
matplotlib.use('TkAgg')


class DataContainer:
    """It gathers measurement data corresponding to dates with a regular sample time. A DataContainer gives an easy access to them and make it possible to plot them."""

    def __init__(self, csv_filename, skiprows=0, nrows=None, initial_string_date=None, final_string_date=None):
        """Create a data container by collecting data from a csv file.

        Selection of a time period can be achieved in 2 ways: with a row basis using skiprows and nrows, or with a date basis: the intersection of both periods is returned.

        :param csv_filename: name of the csv file containing
        :type csv_filename: str
        :param skiprows: number of rows to ignore at the begining of the csv file, defaults to 0
        :type skiprows: int, optional
        :param nrows: number of rows to read (from skiprows), defaults to None
        :type nrows: int, optional
        :param initial_string_date: initial date in format 'dd/mm/YYYY HH:MM:SS', default to None, optional
        :type initial_string_date: str
        :param final_string_date: final date in format 'dd/mm/YYYY HH:MM:SS', default to None, optional
        :type final_string_date: str
        """
        self.sample_time = None
        self.starting_stringdatetime = None
        self.ending_stringdatetime = None
        self.registered_databases = dict()
        self.data = dict()
        self.extracted_variables = list()
        self.data['stringtime'] = None
        self.extracted_variables.append('stringtime')
        self.data['epochtime'] = None
        self.extracted_variables.append('epochtime')
        self.data['datetime'] = None
        self.extracted_variables.append('datetime')

        self.SPECIAL_VARIABLES = ('stringtime', 'epochtime', 'datetime')
        self.variable_full_name_id_dict = dict()  # context$variable: variable_id
        self.variable_full_name_database_dict = dict()  # context$variable: database_name
        self.variable_full_name_csv_dict = dict()  # context$variable: csv_file_name
        self.variable_type = dict()
        self.contexts = list()

        self.data = dict()
        self._extracted_variable_full_names = list()  # context_variable names
        self.data['stringtime'] = None
        self._extracted_variable_full_names.append('stringtime')
        self.data['epochtime'] = None
        self._extracted_variable_full_names.append('epochtime')
        self.data['datetime'] = None
        self._extracted_variable_full_names.append('datetime')

        dataframe = pandas.read_csv(csv_filename, dialect='excel')

        variable_names = dataframe.columns
        for variable_name in variable_names:
            if variable_name == 'stringtime':
                dataframe['stringtime'].astype({'stringtime': 'str'})
                self.data[variable_name] = dataframe[variable_name].values.tolist()[skiprows:nrows+skiprows] if nrows is not None else dataframe[variable_name].values.tolist()[skiprows:]
            elif variable_name == 'datetime':
                if nrows is not None:
                    self.data[variable_name] = [timemg.stringdate_to_datetime(stringdatetime, date_format='%Y-%m-%d %H:%M:%S') for stringdatetime in dataframe['datetime'].values.tolist()[skiprows:nrows+skiprows]]
                else:
                    self.data[variable_name] = [timemg.stringdate_to_datetime(stringdatetime, date_format='%Y-%m-%d %H:%M:%S') for stringdatetime in dataframe['datetime'].values.tolist()[skiprows:]]
            elif variable_name == 'epochtime':
                dataframe[variable_name].astype({'epochtime': 'int'})
                self.data[variable_name] = dataframe[variable_name].values.tolist()[skiprows:nrows+skiprows] if nrows is not None else dataframe[variable_name].values.tolist()[skiprows:]
            else:
                self.add_external_variable(variable_name, dataframe[variable_name].values.tolist()[skiprows:nrows+skiprows] if nrows is not None else dataframe[variable_name].values.tolist()[skiprows:])

        in_period=False
        k_inf, k_sup = 0, len(self.data['datetime'])
        initial_datetime = timemg.stringdate_to_datetime(initial_string_date, date_format='%d/%m/%Y %H:%M:%S') if initial_string_date is not None else None
        final_datetime = timemg.stringdate_to_datetime(final_string_date, date_format='%d/%m/%Y %H:%M:%S') if final_string_date is not None else None
        for k in range(len(self.data['datetime'])):
            current_datetime = self.data['datetime'][k]
            if not in_period and initial_datetime is not None and current_datetime >= initial_datetime:
                k_inf = k
                in_period = True
            if in_period and final_datetime is not None and current_datetime >= final_datetime:
                k_sup = k
                break
        for variable_name in variable_names:
            self.data[variable_name] = self.data[variable_name][k_inf:k_sup]

        self.starting_stringdatetime = self.data['stringtime'][0]
        self.ending_stringdatetime = self.data['stringtime'][-1]
        self.sample_time_in_secs = int((self.data['epochtime'][1]-self.data['epochtime'][0]) / 1000)

    def add_external_variable(self, label: str, values):
        """Use to add a series of values to the container. It will appears as any other measurements.

        :param label: file_name of the series
        :type label: str
        :param values: series of values but it must be compatible with the times which are common to all series
        :type values: list[float]
        """
        if label in self.extracted_variables:
            print('variable %s replaced because it was already extracted' % label)
            del self.data[label]
        self.data[label] = values
        self.extracted_variables.append(label)

    def get_variable(self, label):
        """Use to get a series of values. Special series of dates are available: 'stringtime' as string, 'epochtime' as number of seconds from January 1st 1970 at Greenwich (EPOCH time),  'datetime' as Python date format.

        :param label: file_name of the series coming from CSV file or among 'stringtime', 'epochtime' or 'datetime'
        :type label: str
        :return: a list of floating numbers
        :rtype: list[float]
        """
        return self.data[label]

    def get_number_of_variables(self):
        """Get the number of series including 3 times series named 'stringtime', 'epochtime' or 'datetime'.

        :return: number of series plus 3 different time series
        :rtype: int
        """
        return len(self.extracted_variables)

    def get_number_of_samples(self):
        """Return the number of data common to all the series.

        :return: the number of data common to all the series
        :rtype: int
        """
        if self.data['epochtime'] is None:
            return 0
        else:
            return len(self.data['epochtime'])

    def _plot_selection(self, int_vars: list):
        """Use to plot curve.

        :param int_vars: reference to the variable to be plotted
        :type: list[int]
        """
        styles = ('-', '--', '-.', ':')
        linewidths = (3.0, 2.5, 2.5, 1.5, 1.0, 0.5, 0.25)
        figure, axes = matplotlib.pyplot.subplots()
        axes.set_title('from %s to %s' % (self.starting_stringdatetime, self.ending_stringdatetime))
        text_legends = list()
        for i in range(len(int_vars)):
            if int_vars[i].get():
                style = styles[i % len(styles)]
                linewidth = linewidths[i // len(styles) % len(linewidths)]
                time_data = list(self.data['datetime'])
                value_data = list(self.data[self.extracted_variables[i + 3]])
                if len(time_data) > 1:
                    time_data.append(time_data[-1] + (time_data[-1] - time_data[-2]))
                    value_data.append(value_data[-1])
                axes.step(time_data, value_data, linewidth=linewidth, linestyle=style, where='post')
                axes.set_xlim([time_data[0], time_data[-1]])
                text_legends.append(self.extracted_variables[i + 3])
                int_vars[i].set(0)
        axes.legend(text_legends, loc=0)
        figure.set_tight_layout(True)
        axes.xaxis.set_major_locator(matplotlib.dates.WeekdayLocator(byweekday=matplotlib.dates.MO))
        axes.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%d/%m %H:%M'))
        axes.xaxis.set_minor_locator(matplotlib.dates.DayLocator())
        axes.grid(True)
        matplotlib.pyplot.show()

    def plot(self):
        """Display a series selector to plot the different time series."""
        tk_variables = list()
        tk_window = tk.Tk()
        tk_window.wm_title('variable plotter')
        tk.Button(tk_window, text='plot', command=lambda: self._plot_selection(tk_variables)).grid(row=0, column=0, sticky=tk.W + tk.E)
        frame = tk.Frame(tk_window).grid(row=1, column=0, sticky=tk.N + tk.S)
        vertical_scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
        vertical_scrollbar.grid(row=1, column=1, sticky=tk.N + tk.S)
        canvas = tk.Canvas(frame, width=400, yscrollcommand=vertical_scrollbar.set)
        tk_window.grid_rowconfigure(1, weight=1)
        canvas.grid(row=1, column=0, sticky='news')
        vertical_scrollbar.config(command=canvas.yview)
        checkboxes_frame = tk.Frame(canvas)
        checkboxes_frame.rowconfigure(1, weight=1)
        for i in range(3, len(self.extracted_variables)):
            tk_variable = tk.IntVar()
            tk_variables.append(tk_variable)
            tk.Checkbutton(checkboxes_frame, text=self.extracted_variables[i], variable=tk_variable, offvalue=0).grid(row=(i - 3), sticky=tk.W)
        canvas.create_window(0, 0, window=checkboxes_frame)
        checkboxes_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox('all'))
        tk_window.geometry(str(tk_window.winfo_width()) + "x" + str(tk_window.winfo_screenheight()))
        tk_window.mainloop()

    def size(self):
        """Return the recorded date size.

        :return: the data size
        :rtype: int
        """
        return len(self.data['stringtime'])

    def __str__(self):
        """Make it possible to print a datacontainer.

        :return: description of the datacontainer
        :rtype: str
        """
        string = 'Data cover period from %s to %s with time period: %d seconds\nRegistered database:\n' % (self.starting_stringdatetime, self.ending_stringdatetime, self.sample_time)
        for database in self.registered_databases:
            string += '- %s \n' % database
        string += 'Available variables:\n'
        for variable_name in self.extracted_variables:
            string += '- %s \n' % variable_name
        return string


class PlotSaver:
    """Class to save plots into file."""

    def __init__(self, data_container: DataContainer):
        """Initialize the plot saver.

        :param data_container: datacontainer from which time series can be plotted
        :type data_container: DataContainer
        """
        self.data_container = data_container

    def time_plot(self, selected_variable_full_names, filename: str):
        """Generate time plot.

        :param selected_variable_full_names: full names (ie context$name) of the variables to be plot
        :type selected_variable_full_names: list[str]
        :param filename: name of the image file that will contain the plot
        :type filename: str
        """
        styles = ('-', '--', '-.', ':')
        linewidths = (1.0, 1.0, 0.75, 0.75, 0.5, 0.5, 0.25, 0.25)
        _, axes = matplotlib.pyplot.subplots()
        text_legends = list()
        for i in range(len(selected_variable_full_names)):
            style = styles[i % len(styles)]
            linewidth = linewidths[i // len(styles) % len(linewidths)]
            time_data = list(self.data_container.data['datetime'])
            variable_data = list(self.data_container.get_variable(selected_variable_full_names[i]))
            if len(time_data) > 1:
                time_data.append(time_data[-1] + (time_data[-1] - time_data[-2]))
                variable_data.append(variable_data[-1])
            axes.step(time_data, variable_data, linewidth=linewidth, linestyle=style, where='post')
            axes.set_xlim([time_data[0], time_data[-1]])
            text_legends.append(selected_variable_full_names[i])

        # axes.xaxis.set_major_locator(matplotlib.dates.WeekdayLocator(byweekday=matplotlib.dates.MO))
        # axes.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%d/%m %H:%M'))
        axes.legend(text_legends, loc=0)
        axes.xaxis.set_minor_locator(matplotlib.dates.DayLocator())
        axes.fmt_xdata = matplotlib.dates.DateFormatter('%d/%m/%Y %H:%M')
        matplotlib.pyplot.gcf().autofmt_xdate()
        axes.grid(True)
        matplotlib.pyplot.savefig(filename+'.png', dpi=1500)

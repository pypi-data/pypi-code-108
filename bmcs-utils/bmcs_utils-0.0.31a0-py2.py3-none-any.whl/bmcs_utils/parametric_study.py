import numpy as np
import matplotlib.pyplot as plt
from .model import Model
import os

class ParametricStudy(Model):
    name = 'Parametric Study'
    tree = []
    plot_title = ''

    def run(self, params_config, exp_data=None, log=True, savefig=False):
        np.set_printoptions(precision=3)
        fig, axes = self._get_axes(params_config)
        if exp_data is not None:
            for i, ax in enumerate(axes):
                w_val = exp_data[0]
                f_val = exp_data[1]
                ax.plot(w_val, f_val, c='black', label='Experiment', linestyle='--')

        if log:
            print('Parametric study is running...')

        current_ax_idx = 0
        for param_config in params_config:
            if log:
                # print param name
                params_str = ''
                if self._are_multiple_params(param_config):
                    for param in param_config:
                        params_str += param[0] + ', '
                    print(params_str[0:-2] + ': ', end='')
                else:
                    print(param_config[0] + ': ', end='')

            self._plot_for_param_values(param_config, axes[current_ax_idx], log)
            current_ax_idx += 1

            if log:
                print('')
        if log:
            print('Parametric study finished.')
        plt.show()
        self.fig = fig
        if savefig:
            self.savefig()
        return fig

    def _get_axes(self, params_config):
        params_num = len(params_config)
        nrows = int(params_num / 3)
        if params_num % 3 != 0:
            nrows += 1
        ncols = min(params_num, 3)

        fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(7 * ncols, 5 * nrows))

        if params_num > 1:  # axes is numpy array of AxesSubplot objects
            axes = axes.flatten()
        else:  # axes is a single AxesSubplot object
            axes = np.array([axes])
        return fig, axes

    def _plot_for_param_values(self, param_config, axes, log):
        if self._are_multiple_params(param_config):
            # The user provided list of lists that means multiple params to be changed together
            self._plot_for_param_conf_list(param_config, axes, log)
        else:
            self._plot_for_param_conf_list([param_config], axes, log)

    def _plot_for_param_conf_list(self, param_configs, axes, log):
        param_values_1 = param_configs[0][2]
        parallel_param_names = [param_config[0] for param_config in param_configs]
        self.plot_title = '_'.join(parallel_param_names)

        for i_value in range(len(param_values_1)):
            values_str = ''
            parallel_param_values = []
            default_values = []
            # Assign param values for first value series
            for param_config in param_configs:
                param_name = param_config[0]
                param_object = param_config[1]
                param_values = param_config[2]
                value = param_values[i_value]
                parallel_param_values.append(value)
                values_str += str(value) + ', '
                default_values.append(getattr(param_object, param_name))
                try:
                    setattr(param_object, param_name, value)
                except:
                    print('Param assignment failed!')
            values_str = '(' + values_str[0:-2] + '), '
            if log:
                print(values_str, end='')
            self.plot(axes, *self._get_plot_title_and_label(parallel_param_names, parallel_param_values))

            # set default values again
            for i, param_config in enumerate(param_configs):
                param_name = param_config[0]
                param_object = param_config[1]
                setattr(param_object, param_name, default_values[i])

    def savefig(self):
        self.fig.savefig(os.path.join(self.get_output_dir(), self.plot_title + '.pdf'))

    def plot(self, ax, title, curve_label):
        raise NotImplementedError()

    def _are_multiple_params(self, param_config):
        return isinstance(param_config[0], list)

    def _get_plot_title_and_label(self, param_names, values):
        label = ''
        title = ''
        for param_name, value in zip(param_names, values):
            label += param_name + '=' + str(value) + ', '
            title += param_name + ', '
        return title[0:-2], label[0:-2]

    def get_output_dir(self):
        cwd = os.getcwd()
        out_dir = os.path.join(cwd, '_param_studies_data')
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        return out_dir

# Usage example
if __name__ == '__main__':
    from bmcs_beam.bending.deflection_profile import DeflectionProfile

    # Create such class in your package that describes what should be plotted in the params study
    class ParamsStudy(ParametricStudy):

        def __init__(self, dp):
            self.dp = dp

        def plot(self, ax, param_name, value):
            ax.set_xlabel(r'$w_\mathrm{max}$ [mm]')
            ax.set_ylabel(r'$F$ [kN]')
            F, w = self.dp.get_Fw()
            ax.plot(w, self.dp.F_scale * F, label=param_name + '=' + str(value), lw=2)
            ax.set_title(param_name)
            ax.legend()

    dp = DeflectionProfile()
    ps = ParamsStudy(dp)

    # Define the params_config such that:
    # {param_name : (object_which_have_the_param, list of param values), second_param_name... }
    params_config = [
        ['L', dp.beam_design, [4000, 5000]],
        ['L', dp.beam_design, [4000, 5000]],
        ['E_ct', dp.mc, [30000, 35000]],
        # One can study the effect of changing two parameters together like follows
        [['B', dp.mc.cross_section_shape_, [1000, 200, 300]],
         ['H', dp.mc.cross_section_shape_, [300, 400, 700]]],
    ]
    ps.run(params_config)

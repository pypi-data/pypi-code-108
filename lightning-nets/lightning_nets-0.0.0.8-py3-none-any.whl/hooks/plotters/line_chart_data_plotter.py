import os
import matplotlib
import matplotlib.pyplot as plt

import numpy as np

from .data_plotter import DataPlotter

class LineChartDataPlotter(DataPlotter):
    def __init__(self, output_dir:str = os.getcwd()):
        self.output_dir = self._make_path(os.path.join(output_dir, "plots"))
    
    def _make_path(self, output_path):
        if not os.path.isdir(output_path):
            os.makedirs(output_path)
        return output_path

    def plot_data(self, x, y, y_pred, current_epoch, global_step):
        """
        Save output samples.
        """
        matplotlib.use('Agg')

        if len(x.shape) == 2 and len(y.shape) == 2 and len(y_pred.shape) == 2:
            x = x.reshape(x.shape[0], 1, x.shape[1])
            y = y.reshape(y.shape[0], 1, y.shape[1])
            y_pred = y_pred.reshape(y_pred.shape[0], 1, y_pred.shape[1])

        assert y_pred.shape == y.shape
        assert len(x.shape) == 3 and len(y.shape) == 3 and len(y_pred.shape) == 3

        plt.close()
        current_output_dir = self._make_path(os.path.join(self.output_dir, f"epoch={current_epoch}-step-{global_step}"))

        for idx, sample in enumerate(y_pred):
            sample = sample[0]
            x_output = np.arange(len(sample))
            nrows = x.shape[1] + y.shape[1]
            plt.figure(figsize=(20, 10))
            for ti in range(x.shape[1]):
                train_input = x[idx][ti]
                x_input = np.arange(len(train_input))
                ax = plt.subplot(nrows, 1, ti + 1)
                ax.set_ylim([-1, 1])

                plt.plot(x_input, train_input, label='Input_{}'.format(ti), color='indigo')
                plt.ylabel('Input {}'.format(ti))

                plt.ylim(-1.1, 1.1)
                plt.legend(loc=4)
                plt.grid(axis='x')

            train_set_sample = y[idx][0]
            # share x and y
            ax3 = plt.subplot(nrows, 1, nrows)
            ax3.set_ylim([-1, 1])

            plt.plot(x_output, sample, label='G_output', color='dodgerblue')
            plt.plot(x_output, train_set_sample, label='Validation_Output', color='mediumvioletred')

            plt.xlabel('Sample Index')
            plt.ylabel('G Output')

            plt.legend(loc=4)
            plt.tight_layout()

            plt.savefig(os.path.join(current_output_dir, f"{idx + 1}_sample_prediciton.png"))
            plt.clf()
            plt.close()
        
        matplotlib.use('TkAgg')

import os
import matplotlib
import matplotlib.pyplot as plt

import torch

import numpy as np

from .data_plotter import DataPlotter

class MnistCganImageDataPlotter(DataPlotter):
    def __init__(self, output_dir:str = os.getcwd()):
        self.output_dir = self._make_path(os.path.join(output_dir, "plots"))
    
    def _make_path(self, output_path):
        if not os.path.isdir(output_path):
            os.makedirs(output_path)
        return output_path

    def plot_data(self, x, y, y_pred, current_epoch: int, global_step: int):
        matplotlib.use('Agg')

        plt.close()
        current_output_dir = self._make_path(os.path.join(self.output_dir, f"epoch={current_epoch}-step-{global_step}"))

        for idx, sample in enumerate(y_pred):
            sample = sample[0]

            ax1 = plt.subplot(212)
            if len(x.shape) > 1:
                x_t = x[idx,0]
            else:
                x_t = x[idx]
            y_input = torch.nn.functional.one_hot(torch.tensor(x_t).long(), num_classes=10).numpy()
            x_input = np.arange(len(y_input))
            ax1.set_xticks(x_input)

            plt.bar(x_input, y_input, label=f'Input_{0}', color='indigo')
            plt.ylabel(f'Input {0}')
            plt.ylim(0, 1.1)
            plt.legend(loc=4)
            plt.grid(axis='x')

            ax2 = plt.subplot(221)
            plt.imshow(y.squeeze()[idx,:,:])
            plt.colorbar()

            ax3 = plt.subplot(222)
            plt.imshow(y_pred.squeeze()[idx,:,:])
            plt.colorbar()
            
            plt.savefig(os.path.join(current_output_dir, f"{idx + 1}_sample_prediciton.png"))
            plt.clf()
            plt.cla()
            plt.close()

        matplotlib.use('TkAgg')
        return

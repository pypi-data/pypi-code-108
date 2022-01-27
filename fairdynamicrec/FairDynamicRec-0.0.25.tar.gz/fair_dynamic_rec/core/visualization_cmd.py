import os
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

class VisualizationCmd:
    def __init__(self, config, dataObj, rankers):
        self.viz_dir = 'visualizations'
        self.viz_path = self.make_viz_dir(config)

    def draw(self, metric, data, labels, plot_type):
        if plot_type == 'line':
            self.line_plot(metric, data, labels)
        elif plot_type == 'scatter':
            self.scatter_plot(metric, data, labels)
        elif plot_type == 'scatter_colorbar':
            self.scatter_colorbar_plot(metric, data, labels)
        return

    def line_plot(self, metric, data, labels):
        for key, value in data.items():
            plt.plot(value['x'], value['y'], label=labels['legend'][key])
        plt.xlabel(labels['x'])
        plt.ylabel(labels['y'])
        if len(data.keys()) > 1:
            plt.legend()
        plt.savefig(self.viz_path / Path(metric['name'] + '.eps'), format='eps')
        plt.close()

    def scatter_plot(self, metric, data, labels):
        for key, value in data.items():
            plt.scatter(value['x'], value['y'], label=labels['legend'][key], s=1)
        plt.xlabel(labels['x'])
        plt.ylabel(labels['y'])
        if len(data.keys()) > 1:
            plt.legend()
            # plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.savefig(self.viz_path / Path(metric['name'] + '.eps'), format='eps')
        plt.close()

    def scatter_colorbar_plot(self, metric, data, labels):
        for key, value in data.items():
            heatmap = plt.pcolor(value['data'], cmap=plt.cm.Greys, vmin=1, vmax=10)

            # if 'positive_feedback' in value:
            #     for i in range(value['positive_feedback'].shape[1]):
            #         positive_items = value['positive_feedback'][:, i].nonzero()[0]
            #         plt.scatter(np.full(len(positive_items), i), positive_items, color=metric['TP-color'], s=0.1)
                    # negative_items = value['negative_feedback'][:, i].nonzero()[0]
                    # plt.scatter(np.full(len(negative_items), i), negative_items, color=metric['FP-color'], s=0.1)

            plt.yticks(np.arange(0, value['data'].shape[0], 100))
            plt.xticks(np.arange(0, value['data'].shape[1], value['data'].shape[1]/10))

            plt.colorbar(heatmap)

            plt.xlabel(labels['x'])
            plt.ylabel(labels['y'])

            plt.savefig(self.viz_path / Path(key + '-' + metric['name'] + '.jpg'), format='jpg')
            plt.close()

    def make_viz_dir(self, config):
        if not os.path.exists(config._target / Path(self.viz_dir)):
            os.makedirs(config._target / Path(self.viz_dir))
        return config._target / Path(self.viz_dir)
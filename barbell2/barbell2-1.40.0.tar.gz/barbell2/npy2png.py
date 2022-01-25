import os
import logging
import numpy as np
import matplotlib.pyplot as plt

from .utils import apply_window, apply_color_map, get_alberta_color_map

logger = logging.getLogger(__name__)


class Numpy2Png:

    def __init__(self, npy_array_or_file_path):
        self.npy_array_or_file_path = npy_array_or_file_path
        self.png_file_name = 'npy_array.png'
        self.png_file_path = None
        self.png_figure_size = (10, 10)
        self.color_map = None
        self.output_dir = '.'
        self.window = [400, 50]

    def set_png_file_name(self, png_file_name):
        self.png_file_name = png_file_name

    def set_png_figure_size(self, png_figure_size):
        self.png_figure_size = png_figure_size

    def set_output_dir(self, output_dir):
        self.output_dir = output_dir

    def set_color_map(self, color_map):
        if isinstance(color_map, str) and color_map == 'alberta':
            self.color_map = get_alberta_color_map()
        else:
            self.color_map = color_map

    def set_window(self, window):
        self.window = window

    def execute(self):
        if isinstance(self.npy_array_or_file_path, str):
            npy_array = np.load(self.npy_array_or_file_path)
        else:
            npy_array = self.npy_array_or_file_path
        npy_array = apply_window(npy_array, self.window)
        if self.color_map is not None:
            logger.info(f'>>> npy_array: {type(npy_array)}')
            npy_array = apply_color_map(npy_array, self.color_map, dtype=float)
        fig = plt.figure(figsize=self.png_figure_size)
        ax = fig.add_subplot(1, 1, 1)
        if self.color_map is not None:
            plt.imshow(npy_array)
        else:
            plt.imshow(npy_array, cmap='gray')
        ax.axis('off')
        self.png_file_path = os.path.join(self.output_dir, self.png_file_name)
        plt.savefig(self.png_file_path, bbox_inches='tight')
        plt.close('all')

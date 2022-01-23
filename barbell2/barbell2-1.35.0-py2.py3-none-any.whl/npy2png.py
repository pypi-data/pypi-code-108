import os
import numpy as np
import matplotlib.pyplot as plt

from .utils import apply_window


class Numpy2Png:

    def __init__(self, npy_array_or_file_path):
        self.npy_array_or_file_path = npy_array_or_file_path
        self.png_file_name = 'npy_array.png'
        self.png_file_path = None
        self.png_figure_size = (10, 10)
        self.output_dir = '.'
        self.window = [400, 50]

    def set_png_file_name(self, png_file_name):
        self.png_file_name = png_file_name

    def set_png_figure_size(self, png_figure_size):
        self.png_figure_size = png_figure_size

    def set_output_dir(self, output_dir):
        self.output_dir = output_dir

    def set_window(self, window):
        self.window = window

    def execute(self):
        if isinstance(self.npy_array_or_file_path, str):
            npy_array = np.load(self.npy_array_or_file_path)
        else:
            npy_array = self.npy_array_or_file_path
        npy_array = apply_window(npy_array, self.window)
        fig = plt.figure(figsize=self.png_figure_size)
        ax = fig.add_subplot(1, 1, 1)
        plt.imshow(npy_array, cmap='gray')
        ax.axis('off')
        self.png_file_path = os.path.join(self.output_dir, self.png_file_name)
        plt.savefig(self.png_file_path, bbox_inches='tight')
        plt.close('all')

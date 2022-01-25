import os
import numpy as np
import matplotlib.pyplot as plt

from barbell2.utils import apply_color_map, get_alberta_color_map


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
        if self.color_map is not None:
            npy_array = apply_color_map(npy_array, self.color_map)
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


if __name__ == '__main__':
    # pixels = np.load('/Users/Ralph/Desktop/output-segmentl3/1_pred.npy')
    n2p = Numpy2Png('/Users/Ralph/Desktop/output-segmentl3/1_pred.npy')
    n2p.set_color_map('alberta')
    n2p.set_output_dir('/Users/Ralph/Desktop')
    n2p.execute()

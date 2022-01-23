import os
import pydicom
import matplotlib.pyplot as plt


class Dcm2Png:

    def __init__(self, dcm_file):
        self.dcm_file = dcm_file
        self.dcm_file_name = os.path.split(dcm_file)[1]
        self.output_png_file = None
        self.png_figure_size = (10, 10)
        self.output_dir = os.path.abspath(os.path.curdir)
        self.verbose = False

    def set_png_figure_size(self, png_figure_size):
        self.png_figure_size = png_figure_size

    def get_png_figure_size(self):
        return self.png_figure_size

    def set_output_dir(self, output_dir):
        if not os.path.isdir(output_dir):
            if self.verbose:
                print(f'Output directory {output_dir} does not exist, creating it...')
            os.makedirs(output_dir, exist_ok=False)
        self.output_dir = output_dir

    def get_output_dir(self):
        return self.output_dir

    @staticmethod
    def apply_ct_window(pix, window):
        result = (pix - window[1] + 0.5 * window[0])/window[0]
        result[result < 0] = 0
        result[result > 1] = 1
        return result

    def execute(self):
        p = pydicom.dcmread(self.dcm_file)
        if p.file_meta.TransferSyntaxUID.is_compressed:
            p.decompress()
        pixels = p.pixel_array
        pixels = pixels * p.RescaleSlope + p.RescaleIntercept
        pixels = self.apply_ct_window(pixels, [400, 50])
        pixels = pixels.astype(float)
        fig = plt.figure(figsize=self.png_figure_size)
        ax = fig.add_subplot(1, 1, 1)
        plt.imshow(pixels, cmap='gray')
        ax.axis('off')
        self.output_png_file = os.path.join(self.output_dir, self.dcm_file_name + '.png')
        plt.savefig(self.output_png_file, bbox_inches='tight')
        plt.close('all')

    def get_output_png_file(self):
        return self.output_png_file

"""
A library for taking heightmap images and adding contours lines to them. Good
for topographic maps.
"""

from dataclasses import dataclass
from pathlib import Path
import typing
import sys

from matplotlib.image import imread
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


__version__ = "1.0.1"


def rgb2gray(rgb):
    """ Convert RGB to grayscale """
    return np.dot(rgb[..., :3], [0.2989, 0.5870, 0.1140])


@dataclass
class ContourHeightmap:
    """
    Base class for contouring height maps
    """
    width: int = 0
    height: int = 0
    data: any = None

    def load_heightmap(self, filename: typing.Union[str, Path]):
        """ Loads an image file """
        im = imread(filename)  # returns an ndarray
        self.data = im
        self.width, self.height = im.shape[:2]

    def prepare_heightmap(self):
        """
        Get the image data into grayscale and into a meshgrid and contour
        """
        if self.data.shape[2] != 1:  # flatten to grayscale
            self.data = rgb2gray(self.data)
        xs, ys = np.meshgrid(
            np.arange(0, self.height, 1),
            np.arange(0, self.width, 1)
        )

        # add the heightmap to the figure, grayscale
        plt.imshow(self.data, cmap=plt.cm.gray, aspect=1)

        # add the contour lines to the figure
        # cs = plt.contour(xs, ys, self.data)
        plt.contour(xs, ys, self.data)

        # add labels to the main contour lines
        # plt.clabel(cs, inline=1, fontsize=4)

    def render(self, filename="output.png"):
        """ Output the figure to various files """
        plt.axis('off')
        # plt.title(
        #   "Image plot of heightmap as a meshgrid for a grid of values"
        # )
        filename = Path(filename)

        # try and get the image a bit larger than the original
        dpi = 100
        fig = plt.gcf()  # get current figure
        fig.set_dpi(dpi)
        fig.set_size_inches(self.height / dpi, self.width / dpi)

        for output in [filename, filename.with_suffix(".svg")]:
            fig.savefig(output, dpi=dpi*2, bbox_inches='tight', pad_inches=0)
            if output.suffix in [".png"]:  # resize to same as input image
                im = Image.open(output)
                im.thumbnail((self.height, self.width), Image.ANTIALIAS)
                im.save(output)

    def contour(self, inputname, outputname="output.png"):
        """ do all the steps to add and export contours """
        self.load_heightmap(inputname)
        self.prepare_heightmap()
        self.render(outputname)


if __name__ == "__main__":
    c = ContourHeightmap()
    image_name = sys.argv[1]
    out_name = sys.argv[2] if len(sys.argv) > 2 else "output.png"
    c.contour(image_name, out_name)

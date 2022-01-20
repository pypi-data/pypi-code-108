"""
Library of SPAM functions for measuring a porosity field
Copyright (C) 2020 SPAM Contributors

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option)
any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
more details.

You should have received a copy of the GNU General Public License along with
this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import tifffile
import numpy
from . import measurementsToolkit as mtk
import spam.DIC.grid as grid
import spam.plotting.greyLevelHistogram as glh
import matplotlib.pyplot as plt


def porosityField(image, poreValue=None, solidValue=None, maskValue=None, nodeSpacing="auto", hws=10, showGraph=False):
    """
    This function calculates a porosity field on a greyscale image, outputting a field in % porosity.
    A list of half-window sizes can be given, allowing for porosity measurement stability to to evaluate easily.

    Parameters
    ----------
        image : 3D numpy array

        poreValue : float
            The grey value corresponding to the peak of the pores.
            Grey values of this value as considered 100% pore.
            In the case of 2 peaks in the pores (having water and air), should put the principal one.

        solidValue : float
            The grey value corresponding to the peak of the solids.
            Grey values of this value as considered 100% solid.

        maskValue : float, optional
            Indicate whether there is a special value in the input image
            that corrseponds to a mask which indicates voxels that are not taken
            into account in the porosity calculation.
            Default = None

        hws : int or list, optional
            half-window size for cubic measurement window
            Default = 10

        nodeSpacing : int, optional
            spacing of nodes in pixels
            Default = 10 pixels

        showGraph : bool, optional
            If a list of hws is input, show a graph of the porosity evolution
            Default = False

    Returns
    -------
        3D (or 4D) numpy array for constant half-window size (list of half-window sizes)

    """

    # The C function for porosity needs an 8-bit image with greyvalues
    if poreValue is None or solidValue is None:
        print("spam.measurements.porosityField(): Need to give me the greyvalue of the pores and solids")
        return

    if poreValue == solidValue:
        print("spam.measurements.porosityField(): Need to give me the correct greyvalue of the pores and solids, where greyvalue of pores always smaller than that of solids")
        return

    imPorosity = numpy.zeros_like(image, dtype='<u1')
    # Rescale image to imPorosity between poreValue and solidValue, !
    if poreValue < solidValue:
        imPorosity[image > poreValue] = (numpy.true_divide(100, solidValue - poreValue)) * (solidValue - image[image > poreValue])
        imPorosity[image <= poreValue] = 100
        imPorosity[image >= solidValue] = 0

    if poreValue > solidValue:
        imPorosity[image > solidValue] = (numpy.true_divide(100, poreValue - solidValue)) * (poreValue - image[image > solidValue])
        imPorosity[image <= solidValue] = 100
        imPorosity[image >= poreValue] = 0

    # If a mask value is given, apply it
    if maskValue is not None:
        imPorosity[image == maskValue] = 255

    if nodeSpacing == "auto":
        nodeSpacing = min(image.shape) / 2

    # if hws == "auto":           10
    if type(hws) == int:
        hws = [hws]

    points, layout = grid.makeGrid(imPorosity.shape, nodeSpacing)

    pointsArray = []
    hwsArray = []

    for p in points:
        for i in hws:
            pointsArray.append(p)
            hwsArray.append(i)

    pointsArray = numpy.array(pointsArray).astype('<i4')
    hwsArray = numpy.array(hwsArray).astype('<i4')
    porosities = numpy.zeros_like(hwsArray, dtype='<f4')

    # call C function on scaled 8 bit image
    mtk.porosityFieldBinary(imPorosity,
                            pointsArray,
                            hwsArray,
                            porosities)

    if len(hws) == 1:
        porosities = porosities.reshape((layout[0], layout[1], layout[2]))

    else:
        porosities = porosities.reshape((layout[0], layout[1], layout[2], len(hws)))

        if showGraph == True:
            for z in range(porosities.shape[0]):
                for y in range(porosities.shape[1]):
                    for x in range(porosities.shape[2]):
                        plt.plot(hws, porosities[z, y, x, :])
            plt.xlabel('Half-window size')
            plt.ylabel('Porosity (%)')
            plt.show()

    return porosities

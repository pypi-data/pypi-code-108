"""
Library of SPAM functions for plotting greyscale histogram
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


import matplotlib.pyplot as plt
import numpy

def plotGreyLevelHistogram(im, greyRange=None, bins=256, density=False, series=False, showGraph=False):
    """
    Computes a histogram and optionally shows it with matplotlib

    Parameters
    -----------
        im : an n-d numpy array.
            If series = True, the first dimension is interpreted as the different times

        greyRange : 2-component list, optional
            Value of bottom and top of histogram,
            Default is guessed from data type, min and max for float

        bins : int, optional
            Number of bins to split the range into

        density : bool, optional
            Return a PDF or counts?
            Default = False

        series : bool, optional
            Is the input a series of images?
            Default = False

        showGraph : bool, optional
            Show graph?
            Default = False

    Returns
    --------
        midBins : 1D numpy.array
            The middle value of the bins

        counts : 1D numpy.array
            Number of counts for each bin (possibly normalised, if requested)
    """
    if greyRange is None:
        if im.dtype == 'u1':
            greyRange = [0,256]
        elif im.dtype == 'u2':
            greyRange = [0,65536]
        else:
            # Probably a float...
            greyRange = [ im.min(), im.max() ]


    if series == True:
        steps = im.shape[0]
    else:
        steps = 1
        im = [ im.ravel() ]

    for step in range( steps ):
        # Define smoothly-varying colour from blue to red in series
        if series:  d = step/float(steps-1)
        else:       d = 0
        colour = [ 1.0 - d, 0, d ]

        counts,binLimits = numpy.histogram( im[step].ravel(), range=greyRange, bins=bins, density=density)

        binWidth = ( greyRange[1]-greyRange[0] ) / float( bins )

        midBins = [0.5*(a+b) for (a, b) in zip(binLimits[:-1], binLimits[1:])]
        if showGraph == True:
            if series:
                plt.plot( midBins, counts, color=colour, label="Step = {}".format(step+1) )
            else:
                plt.plot( midBins, counts, color=colour )
    if showGraph == True:
        #plt.bar( midBins, counts, binWidth, align='center' )
        plt.xlabel( "Greylevel" )
        plt.ylabel( "Frequency" )
        #plt.ylim( [0, sorted( counts )[int(bins*99.5/100)]] )
        if series:
            plt.legend()
        plt.show()

    return midBins, counts

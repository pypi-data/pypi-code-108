"""
Library of wrapper functions for Simple ITK
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

import SimpleITK
import spam.label

def watershed(binary, markers=None, watershedLevel=1):
    """
    This function runs an ITK watershed on a binary image and returns a labelled image.
    This function uses an interpixel watershed.

    Parameters
    -----------
        binary : 3D numpy array
            This image which is non-zero in the areas which should be split by the watershed algorithm

        markers : 3D numpy array (optional, default = None)
            Not implemented yet, but try!

        watershedLevel : int, optional
            Watershed level for merging maxima

    Returns
    --------
        labelled : 3D numpy array of ints
            3D array where each object is numbered
    """
    import matplotlib.pyplot as plt
    def plotme(im):
        im = SimpleITK.GetArrayFromImage(im)
        plt.imshow(im[im.shape[0]//2])
        plt.show()

    binary = binary > 0

    # Let's convert it 8-bit
    binary = binary.astype('<u1') * 255

    bdata = SimpleITK.GetImageFromArray(binary)

    if markers is not None:
        markers = markers.astype('<u4') if markers.max() > 65535 else markers.astype('<u2')
        markers = SimpleITK.GetImageFromArray(markers)

    watershedLevel=1
    watershedLineOn=False
    fullyConnected=True

    #thresholdFilt = SimpleITK.OtsuThresholdImageFilter()
    #bdata = thresholdFilt.Execute(data)

    #rescaleFilt = SimpleITK.RescaleIntensityImageFilter()
    #rescaleFilt.SetOutputMinimum(0)
    #rescaleFilt.SetOutputMaximum(65535)
    #bdata = rescaleFilt.Execute(data)

    #threshold = thresholdFilt.GetThreshold()

    #fillFilt = SimpleITK.BinaryFillholeImageFilter()
    #bdata = fillFilt.Execute(bdata)

    invertFilt = SimpleITK.InvertIntensityImageFilter()
    bdata = invertFilt.Execute(bdata)

    distanceMapFilt = SimpleITK.DanielssonDistanceMapImageFilter()
    distance = distanceMapFilt.Execute(bdata)

    distance = invertFilt.Execute(distance)

    if markers is None:
        watershedFilt = SimpleITK.MorphologicalWatershedImageFilter()
    else:
        watershedFilt = SimpleITK.MorphologicalWatershedFromMarkersImageFilter()
    watershedFilt.SetFullyConnected(fullyConnected)
    watershedFilt.SetMarkWatershedLine(watershedLineOn)

    if markers is None:
        watershedFilt.SetLevel(watershedLevel)
        labelImage = watershedFilt.Execute(distance)
    else:
        labelImage = watershedFilt.Execute(distance, markers)

    bdata = invertFilt.Execute(bdata)

    maskFilt = SimpleITK.MaskImageFilter()
    mask = maskFilt.Execute(labelImage, bdata)

    #overlayFilt = SimpleITK.LabelOverlayImageFilter()
    #overlay = overlayFilt.Execute(bdata, mask)

    lab = SimpleITK.GetArrayFromImage(mask).astype(spam.label.labelType)

    return lab

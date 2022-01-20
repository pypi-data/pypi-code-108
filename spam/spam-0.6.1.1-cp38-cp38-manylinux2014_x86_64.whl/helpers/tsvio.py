"""
Library of SPAM functions for reading and writing TSV files.
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

import numpy
import os


def writeRegistrationTSV(fileName, regCentre, regReturns):
    '''
    This function writes a correctly formatted TSV file from the result of a single `register()` call, allowing it to be used as an initial registration.

    Parameters
    ----------
        fileName : string
            The file name for output, suggestion: it should probably end with ".tsv"

        regCentre : 3-component list
            A list containing the point at which `Phi` has been measured.
            This is typically the middle of the image, and can be obtained as follows:
            (numpy.array( im.shape )-1)/2.0
            The conversion to a numpy array is necessary, since tuples cannot be divided by a number directly.

        regReturns : dictionary
            This should be the return dictionary from `register`.
            From this dictionary will be extracted: 'Phi', 'error', 'iterations', 'returnStatus', 'deltaPhiNorm'

    '''
    try:
        regPhi = regReturns['Phi']
    except:
        print("spam.helpers.tsvio.writeRegistrationTSV(): Attempting to read old format")
        regPhi = regReturns['PhiCentre']

    # catch 2D images
    if len(regCentre) == 2:
        regCentre = [0, regCentre[0], regCentre[1]]

    # Make one big array for writing:
    header = "NodeNumber\tZpos\tYpos\tXpos\tFzz\tFzy\tFzx\tZdisp\tFyz\tFyy\tFyx\tYdisp\tFxz\tFxy\tFxx\tXdisp\terror\titerations\treturnStatus\tdeltaPhiNorm"
    try:
        outMatrix = numpy.array([[1],
                                [regCentre[0]],
                                [regCentre[1]],
                                [regCentre[2]],
                                [regPhi[0, 0]],
                                [regPhi[0, 1]],
                                [regPhi[0, 2]],
                                [regPhi[0, 3]],
                                [regPhi[1, 0]],
                                [regPhi[1, 1]],
                                [regPhi[1, 2]],
                                [regPhi[1, 3]],
                                [regPhi[2, 0]],
                                [regPhi[2, 1]],
                                [regPhi[2, 2]],
                                [regPhi[2, 3]],
                                [regReturns['error']],
                                [regReturns['iterations']],
                                [regReturns['returnStatus']],
                                [regReturns['deltaPhiNorm']]])
    except:
        print("spam.helpers.tsvio.writeRegistrationTSV(): Attempting to read old format")
        outMatrix = numpy.array([[1],
                            [regCentre[0]],
                            [regCentre[1]],
                            [regCentre[2]],
                            [regPhi[0, 0]],
                            [regPhi[0, 1]],
                            [regPhi[0, 2]],
                            [regPhi[0, 3]],
                            [regPhi[1, 0]],
                            [regPhi[1, 1]],
                            [regPhi[1, 2]],
                            [regPhi[1, 3]],
                            [regPhi[2, 0]],
                            [regPhi[2, 1]],
                            [regPhi[2, 2]],
                            [regPhi[2, 3]],
                            [regReturns['error']],
                            [regReturns['iterationNumber']],
                            [regReturns['returnStatus']],
                            [regReturns['deltaPhiNorm']]])

    numpy.savetxt(fileName,
                  outMatrix.T,
                  fmt='%.7f',
                  delimiter='\t',
                  newline='\n',
                  comments='',
                  header=header)


def writeStrainTSV(fileName, points, decomposedFfield, firstColumn="StrainPointNumber", startRow=0):
    """
    This function writes strains to a TSV file, hiding the complexity of counting and naming columns

    Parameters
    ----------
        fileName : string
            fileName including full path and .tsv at the end to write

        points : Nx3 numpy array
            Points at which the strain is defined

        decomposedFfield : dictionary
            Dictionary containing strain components as per output from spam.deformation.FfieldRegularQ8, FfieldRegularGeers or FfieldBagi

        firstColumn : string, optional
            How to name the first column (series number) of the TSV
            Default = "StrainPointNumber"

        startRow : int, optional
            Are your points and strains offset from zero? Offset TSV by adding blank lines, don't use this if you don't know what you're doing
            Default = 0

    Returns
    -------
        None
    """
    # This is the minimum header for everyone
    header = "{}\tZpos\tYpos\tXpos".format(firstColumn)

    # Allocate minimum output array
    outMatrix = numpy.array([numpy.arange(points.shape[0]),
                                          points[:, 0],
                                          points[:, 1],
                                          points[:, 2]]).T

    nCols = 4

    for component in decomposedFfield.keys():
        if component == 'vol' or component == 'dev' or component == 'volss' or component == 'devss':
                        header = header + "\t{}".format(component)
                        outMatrix = numpy.hstack([outMatrix, numpy.array([decomposedFfield[component].ravel()]).T])
                        nCols += 1

        if component == 'r' or component == 'z':
            for n, di in enumerate(['z', 'y', 'x']):
                        header = header + "\t{}{}".format(component, di)
                        outMatrix = numpy.hstack([outMatrix, numpy.array([decomposedFfield[component].reshape(-1,3)[:,n].ravel()]).T])
                        nCols += 1

        if component == 'e' or component == 'U':
            for n, di in enumerate(['z', 'y', 'x']):
                for m, dj in enumerate(['z', 'y', 'x']):
                    if m>=n:
                        header = header + "\t{}{}{}".format(component, di, dj)
                        outMatrix = numpy.hstack([outMatrix, numpy.array([decomposedFfield[component].reshape(-1,3,3)[:,n,m].ravel()]).T])
                        nCols += 1

    # This is mostly for discrete Strains, where we can avoid or not the zero-numbered grain
    if startRow > 0:
        for i in range(startRow):
            header = header+'\n0.0'
            for j in range(1,nCols):
                header = header+'\t0.0'

    numpy.savetxt(fileName,
                  outMatrix,
                  delimiter='\t',
                  fmt='%.7f',
                  newline='\n',
                  comments='',
                  header=header)


def readCorrelationTSV(fileName, fieldBinRatio=1.0, readOnlyDisplacements=False, readConvergence=True, readPixelSearchCC=False, readError=False, readLabelDilate=False):
    """
    This function reads a TSV file containing a field of deformation functions **Phi** at one or a number of points.
    This is typically the output of the spam-ldic and spam-ddic scripts,
    or anything written by `writeRegistrationTSV`.

    Parameters
    ----------
        fileName : string
            Name of the file

        fieldBinRatio : int, optional
            if the input field is refer to a binned version of the image
            `e.g.`, if ``fieldBinRatio = 2`` the field_name values have been calculated
            for an image half the size of what the returned PhiField is referring to
            Default = 1.0

        readOnlyDisplacements : bool, optional
            Read "zDisp", "yDisp", "xDisp", displacements from the TSV file, and not the rest of the Phi matrix?
            Default = False

        readConvergence : bool, optional
            Read "returnStatus", "deltaPhiNorm", "iterations", from file
            Default = True

        readPixelSearchCC : bool, optional
            Read "pixelSearchCC" from file
            Default = False

        readError : bool, optional
            Read '"error"from file
            Default = False

        readLabelDilate : bool, optional
            Read "LabelDilate" from file
            Default = False

    Returns
    -------
        Dictionary containing:
            fieldDims: 1x3 array of the field dimensions (ZYX) (for a regular grid DIC result)

            numberOfLabels: number of labels (for a discrete DIC result)

            fieldCoords: nx3 array of n points coordinates (ZYX)

            PhiField: nx4x4 array of n points transformation operators

            returnStatus: nx1 array of n points returnStatus from the correlation

            deltaPhiNorm: nx1 array of n points deltaPhiNorm from the correlation

            iterations: nx1 array of n points iterations from the correlation

            pixelSearchCC: nx1 array of n points pixelSearchCC from the correlation

            error: nx1 array of n points error from the correlation

            labelDilate: nx1 array of n points labelDilate from the correlation

    """
    if not os.path.isfile(fileName):
        print("\n\tspam.tsvio.readCorrelationTSV(): {} is not a file. Exiting.".format(fileName))
        return

    f = numpy.genfromtxt(fileName, delimiter="\t", names=True)
    # RS = []
    # deltaPhiNorm = []
    # pixelSearchCC = []

    # If this is a one-line TSV file (an initial registration for example)
    if f.size == 1:
        #print("\tspam.tsvio.readCorrelationTSV(): {} seems only to have one line.".format(fileName))
        nPoints = 1
        numberOfLabels = 1
        fieldDims = [1, 1, 1]

        # Sort out the field coordinates
        fieldCoords = numpy.zeros((nPoints, 3))
        fieldCoords[:, 0] = f['Zpos'] * fieldBinRatio
        fieldCoords[:, 1] = f['Ypos'] * fieldBinRatio
        fieldCoords[:, 2] = f['Xpos'] * fieldBinRatio

        # Sort out the components of Phi
        PhiField = numpy.zeros((nPoints, 4, 4))
        PhiField[0] = numpy.eye(4)

        # Fill in displacements
        try:
            PhiField[0, 0, 3] = f['Zdisp'] * fieldBinRatio
            PhiField[0, 1, 3] = f['Ydisp'] * fieldBinRatio
            PhiField[0, 2, 3] = f['Xdisp'] * fieldBinRatio
        except ValueError:
            PhiField[0, 0, 3] = f['F14'] * fieldBinRatio
            PhiField[0, 1, 3] = f['F24'] * fieldBinRatio
            PhiField[0, 2, 3] = f['F34'] * fieldBinRatio

        if not readOnlyDisplacements:
            try:
                # Get non-displacement components
                PhiField[0, 0, 0] = f['Fzz']
                PhiField[0, 0, 1] = f['Fzy']
                PhiField[0, 0, 2] = f['Fzx']
                PhiField[0, 1, 0] = f['Fyz']
                PhiField[0, 1, 1] = f['Fyy']
                PhiField[0, 1, 2] = f['Fyx']
                PhiField[0, 2, 0] = f['Fxz']
                PhiField[0, 2, 1] = f['Fxy']
                PhiField[0, 2, 2] = f['Fxx']
            except:
                print("spam.helpers.tsvio.readCorrelationTSV(): Attempting to read old format, please update your TSV file (F11 should be Fzz and so on)")
                # Get non-displacement components
                PhiField[0, 0, 0] = f['F11']
                PhiField[0, 0, 1] = f['F12']
                PhiField[0, 0, 2] = f['F13']
                PhiField[0, 1, 0] = f['F21']
                PhiField[0, 1, 1] = f['F22']
                PhiField[0, 1, 2] = f['F23']
                PhiField[0, 2, 0] = f['F31']
                PhiField[0, 2, 1] = f['F32']
                PhiField[0, 2, 2] = f['F33']

        if readConvergence:
            try:
                # Return ReturnStatus, SubPixelDeltaFnorm, SubPixelIterations
                RS = f['returnStatus']
                deltaPhiNorm = f['deltaPhiNorm']
                iterations = f['iterations']
            except:
                print("spam.helpers.tsvio.readCorrelationTSV(): Attempting to read old format, please update your TSV file (SubPix should be )")
                # Return ReturnStatus, SubPixelDeltaFnorm, SubPixelIterations
                RS = f['SubPixReturnStat']
                deltaPhiNorm = f['SubPixDeltaPhiNorm']
                iterations = f['SubPixIterations']
        if readError:
            try:
                error = f['error']
            except ValueError:
                pass
        # Return pixelSearchCC
        if readPixelSearchCC:
            pixelSearchCC = numpy.zeros(nPoints)
            try:
                pixelSearchCC = f['pixelSearchCC']
            except ValueError:
                pass

         # Return error
        if readError:
            error = numpy.zeros(nPoints)
            try:
                error = f['error']
            except ValueError:
                pass
        # Return labelDilate
        if readLabelDilate:
            labelDilate = numpy.zeros(nPoints)
            try:
                labelDilate = f['LabelDilate']
            except ValueError:
                pass


        pixelSearchCC = 0

    # there is more than one line in the TSV file -- a field -- typical case
    else:
        nPoints = f.size

        # check if it is a ddic or ldic result
        try:
            f["NodeNumber"]
            # it's a local DIC result with grid points regularly spaced
            DICgrid = True
            DICdiscrete = False
        except ValueError:
            # it's a discrete DIC result with values in each label's centre of mass
            DICdiscrete = True
            DICgrid = False

        # Sort out the field coordinates
        fieldCoords = numpy.zeros((nPoints, 3))
        fieldCoords[:, 0] = f['Zpos'] * fieldBinRatio
        fieldCoords[:, 1] = f['Ypos'] * fieldBinRatio
        fieldCoords[:, 2] = f['Xpos'] * fieldBinRatio

        if DICgrid:
            fieldDims = numpy.array([len(numpy.unique(f['Zpos'])), len(numpy.unique(f['Ypos'])), len(numpy.unique(f['Xpos']))])
            numberOfLabels = 0
            print("\tspam.tsvio.readCorrelationTSV(): Field dimensions: {}".format(fieldDims))
        elif DICdiscrete:
            numberOfLabels = len(f["Label"])
            fieldDims = [0, 0, 0]
            print("\tspam.tsvio.readCorrelationTSV(): Number of labels: {}".format(numberOfLabels))

        # create ReturnStatus and deltaPhiNorm matrices if asked
        if readConvergence:
            try:
                RS = numpy.zeros(nPoints)
                RS[:] = f[:]['returnStatus']
                deltaPhiNorm = numpy.zeros(nPoints)
                deltaPhiNorm = f[:]['deltaPhiNorm']
                iterations = numpy.zeros(nPoints)
                iterations = f[:]['iterations']
            except:
                print("spam.helpers.tsvio.readCorrelationTSV(): Attempting to read old format, please update your TSV file")
                RS = numpy.zeros(nPoints)
                RS[:] = f[:]['SubPixReturnStat']
                deltaPhiNorm = numpy.zeros(nPoints)
                deltaPhiNorm = f[:]['SubPixDeltaPhiNorm']
                iterations = numpy.zeros(nPoints)
                iterations = f[:]['SubPixIterations']

        # Return pixelSearchCC
        if readPixelSearchCC:
            pixelSearchCC = numpy.zeros(nPoints)
            try:
                pixelSearchCC = f[:]['pixelSearchCC']
            except ValueError:
                pass

         # Return error
        if readError:
            error = numpy.zeros(nPoints)
            try:
                error = f[:]['error']
            except ValueError:
                pass
        # Return labelDilate
        if readLabelDilate:
            labelDilate = numpy.zeros(nPoints)
            try:
                labelDilate = f[:]['LabelDilate']
            except ValueError:
                pass

        # Sort out the components of Phi
        PhiField = numpy.zeros((nPoints, 4, 4))
        for n in range(nPoints):
            # Initialise with Identity matrix
            PhiField[n] = numpy.eye(4)

            # Fill in displacements
            try:
                PhiField[n, 0, 3] = f[n]['Zdisp'] * fieldBinRatio
                PhiField[n, 1, 3] = f[n]['Ydisp'] * fieldBinRatio
                PhiField[n, 2, 3] = f[n]['Xdisp'] * fieldBinRatio
            except ValueError:
                PhiField[n, 0, 3] = f[n]['F14'] * fieldBinRatio
                PhiField[n, 1, 3] = f[n]['F24'] * fieldBinRatio
                PhiField[n, 2, 3] = f[n]['F34'] * fieldBinRatio

            if not readOnlyDisplacements:
                try:
                    # Get non-displacement components
                    PhiField[n, 0, 0] = f[n]['Fzz']
                    PhiField[n, 0, 1] = f[n]['Fzy']
                    PhiField[n, 0, 2] = f[n]['Fzx']
                    PhiField[n, 1, 0] = f[n]['Fyz']
                    PhiField[n, 1, 1] = f[n]['Fyy']
                    PhiField[n, 1, 2] = f[n]['Fyx']
                    PhiField[n, 2, 0] = f[n]['Fxz']
                    PhiField[n, 2, 1] = f[n]['Fxy']
                    PhiField[n, 2, 2] = f[n]['Fxx']
                except:
                    print("spam.helpers.tsvio.readCorrelationTSV(): Attempting to read old format, please update your TSV file (F11 should be Fzz and so on)")
                    # Get non-displacement components
                    PhiField[n, 0, 0] = f[n]['F11']
                    PhiField[n, 0, 1] = f[n]['F12']
                    PhiField[n, 0, 2] = f[n]['F13']
                    PhiField[n, 1, 0] = f[n]['F21']
                    PhiField[n, 1, 1] = f[n]['F22']
                    PhiField[n, 1, 2] = f[n]['F23']
                    PhiField[n, 2, 0] = f[n]['F31']
                    PhiField[n, 2, 1] = f[n]['F32']
                    PhiField[n, 2, 2] = f[n]['F33']

    output = {"fieldDims": fieldDims,
              "numberOfLabels": numberOfLabels,
              "fieldCoords": fieldCoords}
    if readConvergence:
        output.update({"returnStatus": RS,
                        "deltaPhiNorm": deltaPhiNorm,
                        "iterations": iterations})
    if readError:
        output.update({"error": error})
    if readPixelSearchCC:
        output.update({"pixelSearchCC": pixelSearchCC})
    if readLabelDilate:
        output.update({"LabelDilate": labelDilate})

    if readOnlyDisplacements:
        output.update({"displacements": PhiField[:, 0:3, -1]})
    else:
        output.update({"PhiField": PhiField})

    return output


def readStrainTSV(fileName):
    """
    This function reads a strain TSV file written by `spam-discreteStrain` or `spam-regularStrain`

    Parameters
    ----------
        fileName : string
            Name of the file

    Returns
    -------
        Dictionary containing:

            fieldDims: 1x3 array of the field dimensions (ZYX)

            fieldCoords : nx3 array of the field coordinates (ZYX)

            numberOfLabels: number of labels (for a discrete strain result)

            vol: nx1 array of n points with volumetric strain computed under the hypotesis of large strains (if computed)

            dev: nx1 array of n points with deviatoric strain computed under the hypotesis of large strains (if computed)

            volss: nx1 array of n points with volumetric strain computed under the hypotesis of small strains (if computed)

            devss: nx1 array of n points with deviatoric strain computed under the hypotesis of small strains (if computed)

            r : nx3 array of n points with the components of the rotation vector (if computed)

            z : nx3 array of n points with the components of the zoom vector (if computed)

            U : nx3x3 array of n points with the components of the right-hand stretch tensor (if computed)

            e : nx3x3 array of n points with the components of the strain tensor in small strains (if computed)

    """

    if not os.path.isfile(fileName):
        print("\n\tspam.tsvio.readStrainTSV(): {} is not a file. Exiting.".format(fileName))
        return
    #Read the TSV
    f = numpy.genfromtxt(fileName, delimiter="\t", names=True)

    #Number of points
    nPoints = f.size

    #Get keys from file
    keys = f.dtype.names

    #Create empyt dictionary to be filled
    output = {}

    #Read and add the label coordinates
    fieldCoords = numpy.zeros((nPoints, 3))
    fieldCoords[:, 0] = f['Zpos']
    fieldCoords[:, 1] = f['Ypos']
    fieldCoords[:, 2] = f['Xpos']
    output['fieldCoords'] = fieldCoords

    #Check if we are working with a regular grid or discrete
    grid = False
    discrete = False
    if numpy.abs(fieldCoords[2,0] - fieldCoords[3,0]) == 0:
        grid = True
    else:
        discrete = True

    if grid:
        fieldDims = numpy.array([len(numpy.unique(f['Zpos'])), len(numpy.unique(f['Ypos'])), len(numpy.unique(f['Xpos']))])
        output['fieldDims'] = fieldDims
        output['numberOfLabels'] = 0
    else:
        output['fieldDims'] = [0, 0, 0]
        output['numberOfLabels'] = nPoints

    #Check for all the possible keys
    if 'vol' in keys:
        volStrain = numpy.zeros((nPoints, 1))
        volStrain[:, 0] = f['vol']
        output['vol'] = volStrain

    if 'dev' in keys:
        devStrain = numpy.zeros((nPoints, 1))
        devStrain[:, 0] = f['dev']
        output['dev'] = devStrain

    if 'volss' in keys:
        volss = numpy.zeros((nPoints, 1))
        volss[:, 0] = f['volss']
        output['volss'] = volss

    if 'devss' in keys:
        devss = numpy.zeros((nPoints, 1))
        devss[:, 0] = f['devss']
        output['devss'] = devss

    if 'rz' in keys:
        r = numpy.zeros((nPoints, 3))
        r[:, 0] = f['rz']
        r[:, 1] = f['ry']
        r[:, 2] = f['rx']
        output['r'] = r

    if 'zz' in keys:
        # Zooms, these are very badly named like this
        z = numpy.zeros((nPoints, 3))
        z[:, 0] = f['zz']
        z[:, 1] = f['zy']
        z[:, 2] = f['zx']
        output['z'] = z

    if 'Uzz' in keys:
        # Symmetric, so fill in both sides
        U = numpy.zeros((nPoints, 3, 3))
        U[:, 0, 0] = f['Uzz']
        U[:, 1, 1] = f['Uyy']
        U[:, 2, 2] = f['Uxx']
        U[:, 0, 1] = f['Uzy']
        U[:, 1, 0] = f['Uzy']
        U[:, 0, 2] = f['Uzx']
        U[:, 2, 0] = f['Uzx']
        U[:, 1, 2] = f['Uyx']
        U[:, 2, 1] = f['Uyx']
        output['U'] = U

    if 'ezz' in keys:
        # Symmetric, so fill in both sides
        e = numpy.zeros((nPoints, 3, 3))
        e[:, 0, 0] = f['ezz']
        e[:, 1, 1] = f['eyy']
        e[:, 2, 2] = f['exx']
        e[:, 0, 1] = f['ezy']
        e[:, 1, 0] = f['ezy']
        e[:, 0, 2] = f['ezx']
        e[:, 2, 0] = f['ezx']
        e[:, 1, 2] = f['eyx']
        e[:, 2, 1] = f['eyx']
        output['e'] = e

    return output


def TSVtoTIFF(fileName, fieldBinRatio=1.0, lab=None, returnRS=False, outDir=None, prefix=None):
    '''
    This function converts a TSV file (typically the output of spam-ldic and spam-ddic scripts)
    to a tiff file for visualising the deformation field.

    Parameters
    ----------
        fileName : string
            Name of the file

        fieldBinRatio : int, optional
            if the input field is refer to a binned version of the image
            `e.g.`, if ``fieldBinRatio = 2`` the field_name values have been calculated
            for an image half the size of what the returned PhiField is referring to
            Default = 1.0

        lab : 3D numpy array, optional
            The labelled image of the reference state. Highly recommended argument in case of a discrete correlation result.
            Default = None

        returnRS : bool, optional
            if True: will return the returnStatus of the correlation as a tiff file
            Default = False

        outDir : string, optional
            Output directory
            Default is directory of the input field file

        prefix : string, optional
            Prefix for output files
            Default is the basename of the input field file (without extension)
    '''

    import tifffile
    # use the helper function to read the TSV file
    fi = readCorrelationTSV(fileName, fieldBinRatio=fieldBinRatio, readOnlyDisplacements=True, readConvergence=returnRS)
    displacements = fi["displacements"]
    PhiComponents = [['Zdisp', 0],
                     ['Ydisp', 1],
                     ['Xdisp', 2]]

    # set output directory if none
    if outDir is None:
        if os.path.dirname(fileName) == "":
            outDir = "./"
        else:
            outDir = os.path.dirname(fileName)
    else:
        os.makedirs(outDir)

    # output file name prefix
    if prefix is None:
        prefix = os.path.splitext(os.path.basename(fileName))[0]

    # check if it is a ddic result
    if fi["numberOfLabels"] != 0:
        if lab:
            labelled = tifffile.imread(lab)
            import spam.label

            for component in PhiComponents:
                tifffile.imsave("{}/{}-{}.tif".format(outDir, prefix, component[0]),
                                spam.label.convertLabelToFloat(labelled, displacements[:, component[1]]).astype('<f4'))
            if returnRS:
                tifffile.imsave("{}/{}-RS.tif".format(outDir, prefix),
                                spam.label.convertLabelToFloat(labelled, fi["returnStatus"]).astype('<f4'))
        else:
            print("\tspam.tsvio.TSVtoTIFF(): The labelled image of the reference state is needed as input. Exiting.")
            return

    # if not, is a ldic result
    else:
        dims = fi["fieldDims"]

        for component in PhiComponents:
            tifffile.imsave("{}/{}-{}.tif".format(outDir, prefix, component[0]),
                            displacements[:, component[1]].reshape(dims).astype('<f4'))

        if returnRS:
            tifffile.imsave("{}/{}-RS.tif".format(outDir, prefix),
                            fi["returnStatus"].reshape(dims).astype('<f4'))


def TSVtoVTK(fileName, fieldBinRatio=1.0, pixelSize=1.0, returnRS=False, outDir=None, prefix=None):
    '''
    This function converts a TSV file (typically the output of the ldic and ddic scripts)
    to a VTK file for visualising the deformation field.

    Parameters
    ----------
        fileName : string
            Name of the file

        fieldBinRatio : int, optional
            if the input field is refer to a binned version of the image
            `e.g.`, if ``fieldBinRatio = 2`` the field values have been calculated
            for an image half the size of what the returned PhiField is referring to
            Default = 1.0

        pixelSize: float
            physical size of a pixel (i.e. 1mm/px)
            Default = 1.0

        returnRS : bool, optional
            if True: will return the SubPixelReturnStatus of the correlation
            Default = False

        outDir : string
            Output directory
            Default is directory of the input field file

        prefix : string
            Prefix for output files
            Default is the basename of the input field file (without extension)
    '''
    import spam.helpers
    # use the helper function to read the TSV file
    fi = readCorrelationTSV(fileName, fieldBinRatio=fieldBinRatio)
    PhiField = fi["PhiField"]

    # set output directory if none
    if outDir is None:
        if os.path.dirname(fileName) == "":
            outDir = "./"
        else:
            outDir = os.path.dirname(fileName)
    else:
        os.makedirs(outDir)

    # output file name prefix
    if prefix is None:
        prefix = os.path.splitext(os.path.basename(fileName))[0]

    # check if it is a ddic result
    if fi["numberOfLabels"] != 0:
        coords = fi["fieldCoords"][1:] * pixelSize
        if not returnRS:
            pointData = {"displacements": PhiField[1:, :-1, 3] * pixelSize}

        else:
            pointData = {"displacements": PhiField[1:, :-1, 3] * pixelSize,
                         "returnStatus": fi["returnStatus"][1:]}

        spam.helpers.writeGlyphsVTK(coords, pointData, fileName="{}/{}.vtk".format(outDir, prefix))

    # if not, is a ldic result
    else:
        dims = fi["fieldDims"]
        coords = fi["fieldCoords"] * pixelSize
        aspectRatio = numpy.array([numpy.unique(coords[:, i])[1] - numpy.unique(coords[:, i])[0] if len(numpy.unique(coords[:, i])) > 1 else numpy.unique(coords[:, i])[0] for i in range(3)])
        origin = coords[0] - aspectRatio/2.0

        if not returnRS:
            cellData = {"displacements": (PhiField[:, :-1, 3] * pixelSize).reshape((dims[0], dims[1], dims[2], 3))}

        else:
            cellData = {"displacements": (PhiField[:, :-1, 3] * pixelSize).reshape((dims[0], dims[1], dims[2], 3)),
                        "returnStatus": fi["returnStatus"].reshape(dims[0], dims[1], dims[2])}

        spam.helpers.writeStructuredVTK(aspectRatio=aspectRatio, origin = origin, cellData=cellData, fileName="{}/{}.vtk".format(outDir, prefix))

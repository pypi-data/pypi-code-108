# -*- coding: utf-8 -*-
### 2017-05-29 ER and EA


""" Library of image correlation functions for registering two images acquired with different modalities
"""

import DICToolkit
import numpy
numpy.set_printoptions(precision=3, suppress=True )

import scipy.ndimage
import spam.DIC

from correlateGM import jointHistogram

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


def go( im1, im2,
        gaussFit,
        im1mask = None,
        PhiInit = None,
        margin = None,
        maxIterations = 50, minFchange = 0.0001,
        interpolationOrder=1,
        verbose = False, save4D = False, imShowProgress = False ):
    """
    Perform subpixel image correlation between im1 and im2 -- images of the same object acquired with different modalities.

    This function will deform im1 until it best matches im2.
    The matching includes sub-pixel displacements, rotation, and linear straining of the whole image.
    The correlation of im1, im2 will give a deformation function F which maps im1 into im2.
    im1(F.x) = im2(x)

    "Discrete correlation" can be performed by masking im1.

    Parameters
    ----------
        im1 : 3D numpy array
            The greyscale image that will be deformed

        im2 : 3D numpy array
            The greyscale image that will not move

        gaussFit : 2D numpy array 6xN
            Key parameter which is the result of a 2D gaussian fit of the first N peaks in the joint histograms of
            im1 and im2.
            The 6 parameters of the fit are: φ, μ(im1), μ(im2), and a, b, c, where {a,b,c} are the parameter that can be found for `two-dimensional elliptical Gaussian function` here: https://en.wikipedia.org/wiki/Gaussian_function, `i.e.`, coupled with im1², im1*im2 and im2² respectively

        im1mask : 3D numpy array, float, optional
            A mask for the zone to correlate in im1 with NaNs in the zone to not correlate. Default = None, `i.e.`, correlate all of im1 minus the margin

        PhiInit : 4x4 numpy array, optional
            Initial transformation to apply. Default = numpy.eye(4), `i.e.`, no transformation

        margin : int, optional
            Margin, in pixels, to take in im1 and im2 to allow space for interpolation and movement.
            Default = None (`i.e.`, enough margin for a worse-case 45degree rotation with no displacement)

        maxIterations : int, optional
            Maximum number of quasi-Newton interations to perform before stopping. Default = 25

        minFchange : float, optional
            Smallest change in the norm of F (the transformation operator) before stopping. Default = 0.001

        interpolationOrder : int, optional
            Order of the greylevel interpolation for applying F to im1 when correlating. Reccommended value is 3, but you can get away with 1 for faster calculations. Default = 3

        verbose : bool, optional
            Get to know what the function is really thinking, recommended for debugging only. Default = False

        save4D : bool, optional
            Save the different corrections to im1 as a 4D stack. Default = False

        imShowProgress : bool, optional
            Pop up a window showing the image differences (im1-im2) as im1 is progressively deformed.


    Note
    ----
    This correlation is what is proposed in Tudisco et al. "An extension of Digital Image Correlation for intermodality image registration", section 4.3.
    """

    if verbose: print( "\nEnter correlation" )


    # Detect default case and calculate maring necessary for a 45deg rotation with no displacement
    if margin is None:
        # sqrt
        margin = int( (3**0.5 - 1.0) * max(im1.shape)*0.5 )
    else:
        # Make sure margin is an int
        margin = int( margin )

    # Exit clause for singular matrices
    singular = False

    crop = [ slice( margin, im1.shape[0]-margin ),
             slice( margin, im1.shape[1]-margin ),
             slice( margin, im1.shape[2]-margin ) ]

    if imShowProgress:
        import matplotlib.pyplot as plt
        plt.subplot(1,2,1)
        plt.axis([0, im1[crop].shape[1], 0, im1[crop].shape[2]])
        plt.subplot(1,2,2)
        plt.axis([0, im1[crop].shape[1], 0, im1[crop].shape[2]])
        plt.ion()

    ### Figure out coordinates on which the correlation should happen, i.e., the non NaN ones
    # NOTE: these coordinates are within the cropped margin for interpolation
    #cropImCoordsFG = numpy.where( numpy.isfinite( im1[crop] ) )
    if im1mask is not None:
        # TODO: This could just be directly = mask and equals inv of mask
        #  i.e., arry a boolean mask and not a series of coord array
        cropImCoordsFG = numpy.where( im1mask[crop] == True )
        cropImCoordsBG = numpy.where( im1mask[crop] == False )
    else:
        # Everything regular, except that we might have NaNs in the CW...
        #cropImCoordsFG = numpy.ones_like(  im1[crop], dtype='bool' )
        #cropImCoordsBG = numpy.zeros_like( im1[crop], dtype='bool' )
        cropImCoordsFG = numpy.isfinite(  im1[crop], dtype='bool' )
        cropImCoordsBG = numpy.isnan(     im1[crop], dtype='bool' )
        
        # HACK
        #print cropImCoordsFG
        #print cropImCoordsBG
        
        
        # HACK: set nans in im2 to zero
        im2[ numpy.isnan(im2) ] = 0.0
        
        #if numpy.isnan( im1[crop] ).sum() > 0 numpy.isnan( im2[crop] ).sum() > 0:

    ### Numerical value for normalising the error
    errorNormalisation = len( cropImCoordsFG[0] )

    ### If there is no initial F, initalise it to zero.
    if PhiInit is None:
        F = numpy.eye( 4 )
        im1def = im1.copy()
    else:
        F = PhiInit
        im1def = spam.DIC.applyPhi( im1, F, interpolationOrder=interpolationOrder )

    # Use gradient of image 2 which does move
    im2gradZ, im2gradY, im2gradX = numpy.gradient( im2 )
    
    # At this stage we've computed gradients which we are not going to update, im2 and it's gradients will be set equal to
    #   their cropped versions:
    im2      = im2[crop]
    im2gradZ = im2gradZ[crop]
    im2gradY = im2gradY[crop]
    im2gradX = im2gradX[crop]

    # TODO: Eddy check discrete NaNs for forwards tracking

    # Mask nans in gradient (but not before or there are jumps when the grey goes to zero
    #   beacuse of this a label dilate of at least 1 is recommended)
    #im2gradZ[ numpy.where( numpy.isnan( im1gradZ ) ) ] = 0
    #im2gradY[ numpy.where( numpy.isnan( im1gradY ) ) ] = 0
    #im2gradX[ numpy.where( numpy.isnan( im1gradX ) ) ] = 0

    iterationNumber = 0
    returnStatus = 0

    if save4D:
        import tifffile as tf
        diff = numpy.subtract( im1def[crop], im2 )
        diffSeries = []
        diffSeries.append( diff )

    # Big value to start with to ensure the first iteration
    deltaFnorm = 100.0
    error      = numpy.inf
    errorPrev  = numpy.inf

    while iterationNumber <= maxIterations and deltaFnorm > minFchange:
        errorPrev = error

        if verbose: print( "\tIteration Number {:02d}".format( iterationNumber ) ),

        # No recomputation of gradient
        M = numpy.zeros( ( 12, 12 ), dtype='<f4' )
        A = numpy.zeros( ( 12 ),     dtype='<f4' )
        
        im1defCroppedMasked = im1def[crop]
        if numpy.sum( cropImCoordsBG ) > 0:
            im1defCroppedMasked[ cropImCoordsBG ] = numpy.nan

        DICToolkit.computeDICoperatorsGM( im2,
                                          im1defCroppedMasked,
                                          #im1def[  crop],
                                          im2gradZ,
                                          im2gradY,
                                          im2gradX,
                                          gaussFit, M, A )

        #tifffile.imsave( "im1def-{}.tif".format( iterationNumber ), im1def )
        try: deltaF = numpy.dot( numpy.linalg.inv( M ), A )
        except numpy.linalg.linalg.LinAlgError:
            singular = True
            # TODO: Calculate error for clean break.
            break

        deltaFnorm = numpy.linalg.norm( deltaF )

        # Add padding zeros
        deltaF = numpy.hstack( [ deltaF, numpy.zeros( 4 ) ] ).reshape( ( 4, 4 ))

        # In Roux X-N paper equation number 11
        F = numpy.dot( ( numpy.eye( 4 ) - deltaF ), F )

        # reset im2def as emtpy matrix for deformed image
        im1def = spam.DIC.applyPhi( im1, F, interpolationOrder=interpolationOrder )

        residualField = numpy.zeros_like( im2, dtype="<f4" )
        phaseField = numpy.zeros_like( im2, dtype="<u1"  )

        DICToolkit.computeGMresidualAndPhase( im1def[crop], im2, gaussFit, residualField, phaseField )
        #for pixPos in xrange( len( im1defR ) ):
            #maxPhi2 = 0
            #maxi = None
            ## Build residual -- lambda minux log(phi)
            #for i in xrange( gaussFit.shape[0] ):
                #phi   = gaussFit[i,0]
                #Muim1 = gaussFit[i,1]
                #Muim2 = gaussFit[i,2]
                #a     = gaussFit[i,3]
                #b     = gaussFit[i,4]
                #c     = gaussFit[i,5]

                #l = 0.5 * a * (im1defR[pixPos]-Muim1)**2 + \
                          #b * (im1defR[pixPos]-Muim1)*(im2R[pixPos]-Muim2) + \
                          #c * (   im2R[pixPos]-Muim2)**2
                #phi2 = l - numpy.log( phi );

                #if phi2 > maxPhi2:
                    #maxPhi2 = phi2
                    #maxi = i

            #residualField.ravel()[pixPos] = maxPhi2
            #phaseField.ravel()[pixPos] = maxi
        
        error = numpy.square( residualField ).sum() / errorNormalisation

        if save4D:
            diffSeries.append( numpy.subtract( im2, im1def[crop] ) )

        if verbose:
            print( "Error = {:0.2f}".format( error ) ), 
            print( "deltaFnorm = {:0.4f}".format( deltaFnorm ) )

        if errorPrev < error*0.6:
            # undo this bad F which has increased the error:
            F = numpy.dot( ( numpy.eye( 4 ) + deltaF ), F )
            returnStatus = -1
            print("Error increasing, divergence condition detected, exiting.")
            #break
            print("...no actually continuing...")

        if imShowProgress:
            plt.title('Iteration Number = {}'.format( iterationNumber ))
            plt.subplot(2,2,1)
            plt.imshow( residualField[  im2.shape[0]/2,:,: ] )
            plt.subplot(2,2,2)
            plt.imshow( phaseField[     im2.shape[0]/2,:,: ] )
            plt.subplot(2,2,3)
            plt.imshow( im1def[crop][   im2.shape[0]/2,:,: ] )
            plt.subplot(2,2,4)
            plt.imshow( im2[            im2.shape[0]/2,:,: ] )
            plt.pause(0.5)
            plt.savefig('residuals.pdf')

        #if verbose: print "F = \n", F, "\n\n"

        iterationNumber += 1

    if save4D: tf.imsave( "./diff4D.tif", numpy.array( diffSeries ) )

    # Positive return status is a healthy end of while loop:
    if iterationNumber >= maxIterations: returnStatus = 1
    if deltaFnorm     <= minFchange:    returnStatus = 2
    if singular:                        returnStatus = -2

    # When finished
    diff = numpy.subtract( im2, im1def[crop] )

    if imShowProgress:
        # Turn interactive plotting back off
        plt.ioff()

    return { 'transformation': spam.DIC.decomposePhi( F ),
             'F': F,
             'returnStatus': returnStatus,
             'iterationNumber': iterationNumber,
             'residualField': residualField,
             'phaseField': phaseField }

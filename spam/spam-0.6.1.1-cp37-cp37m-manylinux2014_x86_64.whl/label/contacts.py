"""
Library of SPAM functions for dealing with contacts between particles
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

from . import labelToolkit
import numpy

from collections import deque
import scipy.ndimage #for the contact detection
import skimage.feature #for the maxima of the EDM
import time
import multiprocessing #for contact detection and orientation of assemblies
import spam.label
import progressbar
contactType = '<u4'
# Global number of processes
nProcessesDefault = multiprocessing.cpu_count()

def contactingLabels(lab, labelsList=None, areas=False, boundingBoxes=None, centresOfMass=None):
    """
    This function returns contacting labels for a given label or list of labels,
    and optionally the number of voxels involved in the contact.
    This is designed for an interpixel watershed where there are no watershed lines,
    and so contact detection is done by dilating the particle in question once and
    seeing what other labels in comes in contact with.

    Parameters
    -----------
        lab : 3D numpy array of ints ( of type spam.label.toolkit.labelType)
            An array of labels with 0 as the background

        labels : int or a list of labels
            Labels for which we should compute neighbours

        areas : bool, optional (default = False)
            Compute contact "areas"? *i.e.*, number of voxels
            Careful, this is not a physically correct quantity, and
            is measured only as the overlap from ``label`` to its
            neightbours. See ``c    ontactPoint`` for something
            more meaningful

        boundingBoxes : lab.max()x6 array of ints, optional
            Bounding boxes in format returned by ``boundingBoxes``.
            If not defined (Default = None), it is recomputed by running ``boundingBoxes``

        centresOfMass : lab.max()x3 array of floats, optional
            Centres of mass in format returned by ``centresOfMass``.
            If not defined (Default = None), it is recomputed by running ``centresOfMass``

    Returns
    --------
        For a single "labels", a list of contacting labels.
        if areas == True, then a list of "areas" is also returned.

        For multiple labels, as above but a lsit of lists in the order of the labels

    Note
    -----
        Because of dilation, this function is not very safe at the edges,
        and will throw an exception
    """
    # Default state for single
    single = False
    
    if boundingBoxes is None:
        boundingBoxes = spam.label.boundingBoxes(lab)
    if centresOfMass is None:
        centresOfMass = spam.label.centresOfMass(lab, boundingBoxes=boundingBoxes)
    
    if labelsList is None:
        labelsList = list(range(0, lab.max()+1))
    
    # I guess there's only one label
    if type(labelsList) != list:
        labelsList = [labelsList]
        single = True

    contactingLabels = []
    contactingAreas  = []

    for label in labelsList:
        # catch zero and return it in order to keep arrays aligned
        if label == 0:
            contactingLabels.append([0])
            if areas:
                contactingAreas.append([0])
        else:
            p1 = spam.label.getLabel(lab, label,
                            boundingBoxes=boundingBoxes,
                            centresOfMass=centresOfMass,
                            margin=2)
            p2 = spam.label.getLabel(lab, label,
                            boundingBoxes=boundingBoxes,
                            centresOfMass=centresOfMass,
                            margin=2,
                            labelDilate=1)

            dilOnly = numpy.logical_xor(p2['subvol'], p1['subvol'])

            labSlice = lab[ p1['slice'][0].start:p1['slice'][0].stop,
                            p1['slice'][1].start:p1['slice'][1].stop,
                            p1['slice'][2].start:p1['slice'][2].stop]

            if (dilOnly.shape == labSlice.shape):
                intersection = dilOnly * labSlice

                counts = numpy.unique(intersection, return_counts=True)

                # Print counts starting from the 1th column since we'll always have a ton of zeros
                # print "\tLabels:\n\t",counts[0][1:]
                # print "\tCounts:\n\t",counts[1][1:]

                contactingLabels.append(counts[0][1:])
                if areas:
                    contactingAreas.append(counts[1][1:])

            else:
                # The particle is near the edge, pad it
                
                padArray = numpy.zeros((3,2)).astype(int)
                sliceArray = numpy.zeros((3,2)).astype(int)
                for i, sl in enumerate(p1['slice']):
                    if sl.start < 0:
                        padArray[i,0] = -1*sl.start
                        sliceArray[i,0] = 0
                    else:
                        sliceArray[i,0] = sl.start
                    if sl.stop > lab.shape[0]:
                        padArray[i,1] = sl.stop - lab.shape[0]
                        sliceArray[i,1] = lab.shape[0]
                    else:
                        sliceArray[i,1] = sl.stop
                labSlice = lab[ sliceArray[0,0]:sliceArray[0,1],
                                sliceArray[1,0]:sliceArray[1,1],
                                sliceArray[2,0]:sliceArray[2,1]]
                labSlicePad = numpy.pad(labSlice, padArray)
                intersection = dilOnly * labSlicePad
                counts = numpy.unique(intersection, return_counts=True)
                contactingLabels.append(counts[0][1:])
                if areas:
                    contactingAreas.append(counts[1][1:])

    # Flatten if it's a list with only one object
    if single:
        contactingLabels = contactingLabels[0]
        if areas:
            contactingAreas = contactingAreas[0]
    # Now return things
    if areas:
        return contactingLabels, contactingAreas
    else:
        return contactingLabels


def contactPoints(lab, contactPairs, returnContactZones=False, boundingBoxes=None, centresOfMass=None):
    """
    Get the point, or area of contact between contacting particles.
    This is done by looking at the overlap of a 1-dilation of particle1 onto particle 2
    and vice versa.

    Parameters
    -----------
        lab : 3D numpy array of ints ( of type spam.label.toolkit.labelType)
            An array of labels with 0 as the background

        contactPairs : list (or list of list) of labels
            Pairs of labels for which we should compute neighbours

        returnContactZones : bool, optional (default = False)
            Output a labelled volume where contact zones are labelled according to the order
            of contact pairs?
            If False, the centres of mass of the contacts are returned

        boundingBoxes : lab.max()x6 array of ints, optional
            Bounding boxes in format returned by ``boundingBoxes``.
            If not defined (Default = None), it is recomputed by running ``boundingBoxes``

        centresOfMass : lab.max()x3 array of floats, optional
            Centres of mass in format returned by ``centresOfMass``.
            If not defined (Default = None), it is recomputed by running ``centresOfMass``

    Returns
    --------
        if returnContactZones:
            lab : 3D numpy array of ints ( of type spam.label.toolkit.labelType)
        else:
            Z Y X Centres of mass of contacts
    """
    # detect list of lists with code from: https://stackoverflow.com/questions/5251663/determine-if-a-list-contains-other-lists
    #if not any(isinstance(el, list) for el in contactPairs ):
        #contactPairs = [ contactPairs ]
    # different approach:
    contactPairs = numpy.array(contactPairs)
    # Pad with extra dim if only one contact pair
    if len(contactPairs.shape) == 1:
        contactPairs = contactPairs[numpy.newaxis, ...]

    if boundingBoxes is None:
        boundingBoxes = spam.label.boundingBoxes(lab)
    if centresOfMass is None:
        centresOfMass = spam.label.centresOfMass(lab, boundingBoxes=boundingBoxes)

    # To this volume will be added each contact "area", labelled
    # with the contact pair number (+1)
    analysisVolume = numpy.zeros_like(lab)

    for n, contactPair in enumerate( contactPairs ):
        # Do both orders in contacts
        if len(contactPair) != 2:
            print("spam.label.contacts.contactPoints(): contact pair does not have 2 elements")
        for label1, label2 in [ contactPair, contactPair[::-1] ]:
            #print( "Label1: {} Label2: {}".format( label1, label2 ) )
            p1 = spam.label.getLabel(lab, label1,
                            boundingBoxes=boundingBoxes,
                            centresOfMass=centresOfMass,
                            margin=2)
            p2 = spam.label.getLabel(lab, label1,
                            boundingBoxes=boundingBoxes,
                            centresOfMass=centresOfMass,
                            margin=2,
                            labelDilate=1)

            dilOnly = numpy.logical_xor(p2['subvol'], p1['subvol'])

            labSlice  = (slice(p1['slice'][0].start,p1['slice'][0].stop),
                         slice(p1['slice'][1].start,p1['slice'][1].stop),
                         slice(p1['slice'][2].start,p1['slice'][2].stop))

            labSubvol = lab[labSlice]

            if (dilOnly.shape == labSubvol.shape):
                intersection = dilOnly * labSubvol

                analysisVolume[labSlice][intersection==label2] = n+1

            else:
                raise Exception(
                    '\tdilOnly and labSlice are not the same size... getLabel probably did some safe cutting around the edges')

    if returnContactZones:
        return analysisVolume
    else:
        return spam.label.centresOfMass(analysisVolume)



def labelledContacts(lab, maximumCoordinationNumber=20):
    """
    Uniquely names contacts based on grains.

    Parameters
    -----------
        lab : 3D numpy array of ints ( of type spam.label.toolkit.labelType)
            An array of labels with 0 as the background

        maximumCoordinationNumber : int (optional, default = 20)
            Maximum number of neighbours to consider per grain

    Returns
    --------
        An array, containing:
            contactVolume : array of ints
                3D array where contact zones are uniquely labelled

            Z : array of ints
                Vector of length lab.max()+1 contaning the coordination number
                (number of touching labels for each label)

            contactTable : array of ints
                2D array of lab.max()+1 by  2*maximumCoordinationNumber
                containing, per grain: touching grain label, contact number

            contactingLabels : array of ints
                2D array of numberOfContacts by 2
                containing, per contact: touching grain label 1, touching grain label 2
    """
    contacts        = numpy.zeros_like( lab, dtype=contactType )
    Z               = numpy.zeros( ( lab.max()+1 ), dtype='<u1' )
    contactTable    = numpy.zeros( ( lab.max()+1,  maximumCoordinationNumber*2 ), dtype=contactType )
    contactingLabels= numpy.zeros( ( (lab.max()+1)*maximumCoordinationNumber, 2 ), dtype=spam.label.labelType )

    labelToolkit.labelContacts( lab, contacts, Z, contactTable, contactingLabels )

    # removed the first row of contactingLabels, as it is 0, 0
    return [ contacts, Z, contactTable, contactingLabels[1:contacts.max()+1,:] ]


def fetchTwoGrains(volLab,labels,volGrey=None,boundingBoxes=None,padding=0,size_exclude=5):
    """
    Fetches the sub-volume of two grains from a labelled image

    Parameters
    ----------
        volLab : 3D array of integers
            Labelled volume, with lab.max() labels

        labels : 1x2 array of integers
            the two labels that should be contained in the subvolume
            
        volGrey : 3D array
            Grey-scale volume

        boundingBoxes : lab.max()x6 array of ints, optional
            Bounding boxes in format returned by ``boundingBoxes``.
            If not defined (Default = None), it is recomputed by running ``boundingBoxes``

        padding : integer
            padding of the subvolume
            for some purpose it might be benefitial to have a subvolume
            with a boundary of zeros

    Returns
    -------
        subVolLab : 3D array of integers
            labelled sub-volume containing the two input labels

        subVolBin : 3D array of integers
            binary subvolume

        subVolGrey : 3D array
            grey-scale subvolume
    """

    # check if bounding boxes are given
    if boundingBoxes is None:
        #print "bounding boxes are not given. calculating ...."
        boundingBoxes = spam.label.boundingBoxes(volLab)
    #else:
        #print "bounding boxes are given"
    lab1, lab2 = labels
    # Define output dictionary since we'll add different things to it
    output = {}
    # get coordinates of the big bounding box
    startZ = min( boundingBoxes[lab1,0], boundingBoxes[lab2,0] ) - padding
    stopZ  = max( boundingBoxes[lab1,1], boundingBoxes[lab2,1] ) + padding
    startY = min( boundingBoxes[lab1,2], boundingBoxes[lab2,2] ) - padding
    stopY  = max( boundingBoxes[lab1,3], boundingBoxes[lab2,3] ) + padding
    startX = min( boundingBoxes[lab1,4], boundingBoxes[lab2,4] ) - padding
    stopX  = max( boundingBoxes[lab1,5], boundingBoxes[lab2,5] ) + padding
    output['slice'] = (slice(startZ, stopZ+1),
                       slice(startY, stopY+1),
                       slice(startX, stopX+1))
    subVolLab = volLab[output['slice'][0].start:output['slice'][0].stop, 
                       output['slice'][1].start:output['slice'][1].stop, 
                       output['slice'][2].start:output['slice'][2].stop]

    subVolLab_A = numpy.where( subVolLab == lab1, lab1, 0 )
    subVolLab_B = numpy.where( subVolLab == lab2, lab2, 0 )
    subVolLab = subVolLab_A + subVolLab_B
    
    struc = numpy.zeros((3,3,3))
    struc[1,1:2,:]=1
    struc[1,:,1:2]=1
    struc[0,1,1]=1
    struc[2,1,1]=1
    subVolLab = spam.label.filterIsolatedCells(subVolLab, struc, size_exclude)
    output['subVolLab'] = subVolLab
    subVolBin = numpy.where( subVolLab != 0, 1, 0 )
    output['subVolBin'] = subVolBin
    if volGrey is not None:
        subVolGrey = volGrey[output['slice'][0].start:output['slice'][0].stop, 
                             output['slice'][1].start:output['slice'][1].stop, 
                             output['slice'][2].start:output['slice'][2].stop]
        subVolGrey = subVolGrey * subVolBin
        output['subVolGrey'] = subVolGrey
    
    return output


def localDetection(subVolGrey,localThreshold,radiusThresh=None):
    """
    local contact refinement
    checks whether two particles are in contact with a local threshold,
    that is higher than the global one used for binarisation

    Parameters
    ----------
        subVolGrey : 3D array
            Grey-scale volume

        localThreshold : integer or float, same type as the 3D array
            threshold for binarisation of the subvolume

        radiusThresh : integer, optional
            radius for excluding patches that might not be relevant,
            e.g. noise can lead to patches that are not connected with the grains in contact
            the patches are calculated with ``equivalentRadii()``
            Default is None and such patches are not excluded from the subvolume

    Returns
    -------
        CONTACT : boolean
            if True, that particles appear in contact for the local threshold

    Note
    ----
        see https://doi.org/10.1088/1361-6501/aa8dbf for further information
    """

    CONTACT = False
    subVolBin = ((subVolGrey > localThreshold)*1).astype('uint8')
    if radiusThresh is not None:
        # clean the image of isolated voxels or pairs of voxels
        # due to higher threshold they could exist
        subVolLab, numObjects = scipy.ndimage.measurements.label(subVolBin)
        if numObjects > 1:
            radii = spam.label.equivalentRadii( subVolLab )
            labelsToRemove = numpy.where( radii < radiusThresh )
            if len(labelsToRemove[0]) > 1:
                subVolLab = spam.label.removeLabels( subVolLab, labelsToRemove)
        subVolBin = ((subVolLab > 0)*1).astype('uint8')

    # fill holes
    subVolBin = scipy.ndimage.morphology.binary_fill_holes(subVolBin).astype('uint8')
    labeledArray, numObjects = scipy.ndimage.measurements.label(subVolBin, structure=None, output=None)
    if numObjects == 1:
        CONTACT = True

    return CONTACT


def contactOrientations(volBin, volLab, watershed="ITK", peakDistance=1, markerShrink=True, verbose=False):
    """
    determines contact normal orientation between two particles
    uses the random walker implementation from skimage

    Parameters
    ----------
        volBin : 3D array
            binary volume containing two particles in contact

        volLab : 3D array of integers
            labelled volume containing two particles in contact

        watershed : string
            sets the basis for the determination of the orientation
            options are "ITK" for the labelled image from the input,
            "RW" for a further segmentation by the random walker
            Default = "ITK"

        peakDistance : int, optional
            Distance in pixels used in skimage.feature.peak_local_max
            Default value is 1

        markerShrink : boolean
            shrinks the markers to contain only one voxel.
            For large markers, the segmentation might yield strange results depending on the shape.
            Default = True
            
        verbose : boolean (optional, default = False)
            True for printing the evolution of the process
            False for not printing the evolution of process
        

    Returns
    -------
        contactNormal : 1x3 array
            contact normal orientation in z,y,x coordinates
            the vector is flipped such that the z coordinate is positive

        len(coordIntervox) : integer
            the number of points for the principal component analysis
            indicates the quality of the fit

        notTreatedContact : boolean
            if False that contact is not determined
            if the contact consisted of too few voxels a fit is not possible or feasible
    """
    notTreatedContact = False
    from skimage.segmentation import random_walker

    if watershed == "ITK":
        # ------------------------------
        # ITK watershed for orientations
        # ------------------------------
        # need to relabel, because the _contactPairs functions looks for 1 and 2
        labels = numpy.unique(volLab)
        volLab[ volLab==labels[1] ] = 1
        volLab[ volLab==labels[2] ] = 2

        contactITK = _contactPairs(volLab)

        if len(contactITK) <=2:
            #print('WARNING: not enough contacting voxels (beucher)... aborting this calculation')
            notTreatedContact = True
            return numpy.zeros((3)), 0, notTreatedContact

        coordIntervox = contactITK[:,0:3]
        # Determining the contact orientation! using PCA
        contactNormal = _contactNormals(coordIntervox)

    if watershed == "RW":
        #Get Labels
        label1,label2 = numpy.unique(volLab)[1:]
        #Create sub-domains
        subVolBinA = numpy.where( volLab == label1, 1, 0 )
        subVolBinB = numpy.where( volLab == label2, 1, 0 )
        volBin = subVolBinA + subVolBinB
        #Calculate distance map
        distanceMapA = scipy.ndimage.morphology.distance_transform_edt(subVolBinA)
        distanceMapB = scipy.ndimage.morphology.distance_transform_edt(subVolBinB)
        #Calculate local Max
        localMaxiA = skimage.feature.peak_local_max(distanceMapA, min_distance=peakDistance, indices=False, exclude_border=False, labels=subVolBinA)
        localMaxiB = skimage.feature.peak_local_max(distanceMapB, min_distance=peakDistance, indices=False, exclude_border=False, labels=subVolBinB)
        #Label de Peaks
        struc = numpy.ones((3,3,3))
        markersA, numMarkersA = scipy.ndimage.measurements.label(localMaxiA, structure=struc)
        markersB, numMarkersB = scipy.ndimage.measurements.label(localMaxiB, structure=struc)
        if numMarkersA == 0 or numMarkersB == 0:
            notTreatedContact = True
            if verbose:
                print("spam.contacts.contactOrientations: No grain markers found for this contact. Setting the contact as non-treated")
            return numpy.zeros((3)), 0, notTreatedContact
        #Shrink the markers 
        #   The index property should be a list with all the labels encountered, exlucing the label for the backgroun (0).
        centerOfMassA =  scipy.ndimage.measurements.center_of_mass(markersA,labels=markersA,index=list(numpy.unique(markersA)[1:]))
        centerOfMassB =  scipy.ndimage.measurements.center_of_mass(markersB,labels=markersB,index=list(numpy.unique(markersB)[1:]))    
        #Calculate the value of the distance map for the markers
        marksValA = []
        marksValB = []
        for x in range(len(centerOfMassA)):
            marksValA.append(distanceMapA[int(centerOfMassA[x][0]),int(centerOfMassA[x][1]),int(centerOfMassA[x][2])])    
        for x in range(len(centerOfMassB)):
            marksValB.append(distanceMapB[int(centerOfMassB[x][0]),int(centerOfMassB[x][1]),int(centerOfMassB[x][2])])    
        #Sort the markers coordinates acoording to their distance map value
        #   First element correspond to the coordinates of the marker with the higest value in the distance map
        centerOfMassA = numpy.flipud([x for _,x in sorted(zip(marksValA,centerOfMassA))])
        centerOfMassB = numpy.flipud([x for _,x in sorted(zip(marksValB,centerOfMassB))])
        marksValA = numpy.flipud(sorted(marksValA))
        marksValB = numpy.flipud(sorted(marksValB))
        #Select markers
        markers = numpy.zeros(volLab.shape)
        markers[int(centerOfMassA[0][0]),int(centerOfMassA[0][1]),int(centerOfMassA[0][2])]=1.
        markers[int(centerOfMassB[0][0]),int(centerOfMassB[0][1]),int(centerOfMassB[0][2])]=2.
        # set the void phase of the binary image to -1, excludes this phase from calculation of the random walker (saves time)
        volRWbin = volBin.astype(float)
        markers[~volRWbin.astype(bool)] = -1
        if numpy.max(numpy.unique(markers)) != 2:
            notTreatedContact = True
            if verbose:
                print("spam.contacts.contactOrientations: The grain markers where wrongly computed. Setting the contact as non-treated")
            return numpy.zeros((3)), 0, notTreatedContact
        probMaps = random_walker(volRWbin, markers, beta=80, mode='cg_mg', return_full_prob=True)
        # reset probability of voxels in the void region to 0! (-1 right now, as they were not taken into account!)
        probMaps[:,~volRWbin.astype(bool)] = 0
        # create a map of the probabilities of belonging to either label 1 oder label 2 (which is just the inverse map)
        labRW1 = probMaps[0].astype(numpy.float32)
        # label the image depending on the probabilty of each voxel belonging to marker = 1, save one power watershed
        labRW = numpy.array(labRW1)
        labRW[labRW > 0.5] = 1
        labRW[(labRW < 0.5) & (labRW > 0)] = 2
        # seed of the second marker has to be labelled by 2 as well
        labRW[markers == 2] = 2

        contactVox = _contactPairs(labRW)
        if len(contactVox) <=2:
            #print 'WARNING: not enough contacting voxels (rw).... aborting this calculation'
            notTreatedContact = True
            if verbose:
                print("spam.contacts.contactOrientations: Not enough contacting voxels, aborting this calculation. Setting the contact as non-treated")
            return numpy.zeros((3)), 0, notTreatedContact

        # get subvoxel precision - using the probability values at the contacting voxels!
        coordIntervox = _contactPositions(contactVox,labRW1)
        # Determining the contact orientation! using PCA
        contactNormal = _contactNormals(coordIntervox)

    return contactNormal[0], len(coordIntervox), notTreatedContact


def _contactPairs(lab):
    """
    finds the voxels involved in the contact
    i.e. the voxels of one label in direct contact with another label

    Parameters
    ----------
        lab : 3D array of integers
            labelled volume containing two particles in contact
            labels of the considered particles are 1 and 2

    Returns
    -------
        contact : (len(contactVoxels))x4 array
            z,y,x positions and the label of the voxel
    """
    dimensions = numpy.shape(lab)
    dimZ, dimY, dimX = dimensions[0], dimensions[1], dimensions[2]

    # position of the voxels labelled by 1 ... row 1 = coord index 1, row 2 = coord 2, ...
    positionLabel = numpy.array(numpy.where(lab==1))
    # initialize the array for the contact positions and labels!
    contact=numpy.array([[],[],[],[]]).transpose()

    # loop over all voxels labeled with 1
    for x in range (0,len(positionLabel.transpose())):
        pix=numpy.array([positionLabel[0][x],positionLabel[1][x],positionLabel[2][x],1])
        # pix ... positions (axis 0,1,2) of the first voxel containing 1
        ## x axis neighbor
        if positionLabel[0][x]<dimZ-1: # if the voxel is still in the image!
        #if neighbor in pos. x-direction is 2 then save the actual voxel and the neighbor!!
            if lab[positionLabel[0][x]+1,positionLabel[1][x],positionLabel[2][x]]==2:
                vx1=numpy.array([positionLabel[0][x]+1,positionLabel[1][x],positionLabel[2][x],2])
                # stacks the data, adds a row to the data, so you get (contact, pix, vx2)
                contact=numpy.vstack((contact,pix))
                contact=numpy.vstack((contact,vx1))
        # this condition prevents from getting stuck at the border of the image, where the x-value cannot be reduced!
        if positionLabel[0][x]!=0:
            #if neighbor in neg. x-direction is 2 then save the actual voxel and the neighbor!!
            if lab[positionLabel[0][x]-1,positionLabel[1][x],positionLabel[2][x]]==2:
                vx2=numpy.array([positionLabel[0][x]-1,positionLabel[1][x],positionLabel[2][x],2])
                contact=numpy.vstack((contact,pix))
                contact=numpy.vstack((contact,vx2))
        ## y axis neighbor
        if positionLabel[1][x]<dimY-1:
            if lab[positionLabel[0][x],positionLabel[1][x]+1,positionLabel[2][x]]==2:
                vy1=numpy.array([positionLabel[0][x],positionLabel[1][x]+1,positionLabel[2][x],2])
                contact=numpy.vstack((contact,pix))
                contact=numpy.vstack((contact,vy1))
        if positionLabel[1][x]!=0:
            if lab[positionLabel[0][x],positionLabel[1][x]-1,positionLabel[2][x]]==2:
                vy2=numpy.array([positionLabel[0][x],positionLabel[1][x]-1,positionLabel[2][x],2])
                contact=numpy.vstack((contact,pix))
                contact=numpy.vstack((contact,vy2))
        ## z axis neighbor
        if positionLabel[2][x]<dimX-1:
            if lab[positionLabel[0][x],positionLabel[1][x],positionLabel[2][x]+1]==2:
                vz1=numpy.array([positionLabel[0][x],positionLabel[1][x],positionLabel[2][x]+1,2])
                contact=numpy.vstack((contact,pix))
                contact=numpy.vstack((contact,vz1))
        if positionLabel[2][x]!=0:
            if lab[positionLabel[0][x],positionLabel[1][x],positionLabel[2][x]-1]==2:
                vz2=numpy.array([positionLabel[0][x],positionLabel[1][x],positionLabel[2][x]-1,2])
                contact=numpy.vstack((contact,pix))
                contact=numpy.vstack((contact,vz2))

    return contact


def _contactPositions(contact,probMap):
    """
    determines the position of the points that define the contact area
    for the random walker probability map
    the 50 percent probability plane is considered as the area of contact
    linear interpolation is used to determine the 50 percent probability area

    Parameters
    ----------
        contact : (len(contactVoxels))x4 array
            z,y,x positions and the label of the voxel
            as returned by the function contactPairs()

        probMap : 3D array of floats
            probability map of one of the labels
            as determined by the random walker

    Returns
    -------
        coordIntervox : (len(coordIntervox))x3 array
            z,y,x positions of the 50 percent probability area
    """
    coordIntervox = numpy.array([[],[],[]]).transpose()
    for x in range (0,len(contact),2): #call only contact pairs (increment 2)
        prob1 = probMap[int(contact[x][0]),int(contact[x][1]),int(contact[x][2])]
        #pick the probability value of the concerning contact voxel!
        prob2 = probMap[int(contact[x+1][0]),int(contact[x+1][1]),int(contact[x+1][2])]
        if prob2-prob1 != 0:
            add = float((0.5-prob1)/(prob2-prob1))
        else:
            add=0.5 #if both voxels have the same probability (0.5), the center is just in between them!
        #  check whether the next contact voxel is x-axis (0) neighbor or not
        ## x axis neighbor
        if contact[x][0]!=contact[x+1][0]:
            ## 2 possibilities: a coordinates > or < b coordinates
            if contact[x][0]<contact[x+1][0]: # find the contact point in subvoxel resolution!
                midX=numpy.array([contact[x][0]+add,contact[x][1],contact[x][2]])
                coordIntervox=numpy.vstack((coordIntervox,midX))
            else:
                midX=numpy.array([contact[x][0]-add,contact[x][1],contact[x][2]])
                coordIntervox=numpy.vstack((coordIntervox,midX))
        ## y axis neighbor
        elif contact[x][1]!=contact[x+1][1]:
            if contact[x][1]<contact[x+1][1]:
                midY=numpy.array([contact[x][0],contact[x][1]+add,contact[x][2]])
                coordIntervox=numpy.vstack((coordIntervox,midY))
            else:
                midY=numpy.array([contact[x][0],contact[x][1]-add,contact[x][2]])
                coordIntervox=numpy.vstack((coordIntervox,midY))
        ## z axis neighbor
        else:
            if contact[x][2]<contact[x+1][2]:
                midZ=numpy.array([contact[x][0],contact[x][1],contact[x][2]+add])
                coordIntervox=numpy.vstack((coordIntervox,midZ))
            else:
                midZ=numpy.array([contact[x][0],contact[x][1],contact[x][2]-add])
                coordIntervox=numpy.vstack((coordIntervox,midZ))

    return coordIntervox


def _contactNormals(dataSet):
    """
    determines the contact normal orientation
    based on the intervoxel positions determined by the function contactPositions()
    uses a principal component analysis
    the smallest eigenvector of the covariance matrix is considered as the contact orientation

    Parameters
    ----------
        dataSet : (len(dataSet))x3 array
            z,y,x positions of the 50 percent probability area of the random walker

    Returns
    -------
        contactNormal : 1x3 array
            z,y,x directions of the normalised contact normal orientation
    """
    covariance = numpy.cov(dataSet,rowvar=0,bias=0)

    # step 3: calculate the eigenvectors and eigenvalues
    # eigenvalues are not necessarily ordered ...
    # colum[:,i] corresponds to eig[i]
    eigVal, eigVec = numpy.linalg.eig(covariance)

    # look for the eigenvector corresponding to the minimal eigenvalue!
    minEV = eigVec[:,numpy.argmin(eigVal)]

    # vector orientation
    contactNormal = numpy.zeros((1,3))
    if minEV[2]<0:
        contactNormal[0,0], contactNormal[0,1], contactNormal[0,2] = -minEV[0], -minEV[1], -minEV[2]
    else:
        contactNormal[0,0], contactNormal[0,1], contactNormal[0,2] = minEV[0], minEV[1], minEV[2]

    return contactNormal


def _markerCorrection(markers, numMarkers, distanceMap, volBin, peakDistance=5, struc=numpy.ones((3,3,3))):
    """
    corrects the number of markers used for the random walker segmentation of two particles
    if too many markers are found, the markers with the largest distance are considered
    if too few markers are found, the minimum distance between parameters is reduced

    Parameters
    ----------
        markers : 3-D array of integers
            volume containing the potential markers for the random walker

        numMarkers : integer
            number of markers found so far

        distanceMap : 3-D array of floats
            euclidean distance map

        volBin : 3-D array of integers
            binary volume

        peakDistance : integer
            peak distance as used in skimage.feature.peak_local_max
            Default value is 15 px

        struc=numpy.ones((3,3,3)) : 3x3x3 array of integers
            structuring element for the labelling of the markers
            Default element is a 3x3x3 array of ones

    Returns
    -------
        markers : 3-D array of integers
            volume containing the markers
    """
    counter = 0
    # If there are too many markers, slowly increse peakDistance until it's the size of the image, if this overshoots the next bit will bring it back down
    goodMarkers = []
    if numpy.amax(markers) > 2:
        while numpy.amax(markers) > 2 and peakDistance < min(volBin.shape):
            peakDistance = int(peakDistance*1.3)
            localMaxi = skimage.feature.peak_local_max(distanceMap, min_distance=peakDistance, indices=False, exclude_border = False, labels=volBin, num_peaks=2)
            markers, numMarkers = scipy.ndimage.measurements.label(localMaxi,structure=struc)

    # If there are no markers, decrease peakDistance
    while (numpy.any(markers)==False or numpy.amax(markers) < 2):
        if (counter > 10 ):
            markers=numpy.zeros(markers.shape)
            return markers
        peakDistance = int(peakDistance/1.3)
        localMaxi = skimage.feature.peak_local_max(distanceMap, min_distance=peakDistance, indices=False, exclude_border = False, labels=volBin, num_peaks=2)
        markers, numMarkers = scipy.ndimage.measurements.label(localMaxi,structure=struc)
        counter = counter + 1

    if (numpy.amax(markers) > 2):
        centerOfMass = scipy.ndimage.measurements.center_of_mass(markers, labels=markers, index=range(1,numMarkers+1))
        distances = numpy.zeros((numMarkers,numMarkers))
        for i in range(0, numMarkers):
            for j in range(i, numMarkers):
                distances[i,j] = numpy.linalg.norm(numpy.array(centerOfMass[i])-numpy.array(centerOfMass[j]) )

        maxDistance = numpy.amax(distances)
        posMaxDistance = numpy.where(distances == maxDistance )

        # let's choose the markers with the maximum distance
        markers1 = numpy.where(markers == posMaxDistance[0][0]+1, 1, 0 )
        markers2 = numpy.where(markers == posMaxDistance[1][0]+1, 2, 0 )

        localMaxi = markers1 + markers2
        markers, numMarkers = scipy.ndimage.measurements.label(localMaxi,structure=struc)

    return markers


def localDetectionAssembly(volLab, volGrey, contactList, localThreshold, boundingBoxes=None, nProcesses=nProcessesDefault, radiusThresh=4):
    """
    Local contact refinement of a set of contacts
    checks whether two particles are in contact with a local threshold using ``localDetection()``

    Parameters
    ----------
        volLab : 3D array
            Labelled volume

        volGrey : 3D array
            Grey-scale volume

        contactList : (ContactNumber)x2 array of integers
            contact list with grain labels of each contact in a seperate row,
            as given by ``spam.label.contacts.labelledContacts`` in the list contactingLabels

        localThreshold : integer or float, same type as the 3D array
            threshold for binarisation of the subvolume

        boundingBoxes : lab.max()x6 array of ints, optional
            Bounding boxes in format returned by ``boundingBoxes``.
            If not defined (Default = None), it is recomputed by running ``boundingBoxes``

        nProcesses : integer (optional, default = nProcessesDefault)
            Number of processes for multiprocessing
            Default = number of CPUs in the system

        radiusThresh : integer, optional
            radius in px for excluding patches that might not be relevant,
            e.g. noise can lead to patches that are not connected with the grains in contact
            the patches are calculated with ``equivalentRadii()``
            Default is 4

    Returns
    -------
        contactListRefined : (ContactNumber)x2 array of integers
            refined contact list, based on the chosen local threshold

    Note
    ----
        see https://doi.org/10.1088/1361-6501/aa8dbf for further information
    """
    import progressbar

    # check if bounding boxes are given
    if boundingBoxes is None:
        #print "bounding boxes are not given. calculating ...."
        boundingBoxes = spam.label.boundingBoxes(volLab)

    contactListRefined = []
    numberOfJobs = len( contactList )
    #print ("\n\tLocal contact refinement")
    #print ("\tApplying a local threshold of ", localThreshold, " to each contact.")
    #print ("\tNumber of contacts for treatment ", numberOfJobs)
    #print ("")

    ##########################################

    # Function for localDetectionAssembly
    global funLocalDetectionAssembly
    def funLocalDetectionAssembly(job):
        grainA, grainB = contactList[job].astype('int')
        labels = [grainA, grainB]
        subset = fetchTwoGrains(volLab,labels,volGrey,boundingBoxes)
        contact = localDetection(subset['subVolGrey'],localThreshold,radiusThresh)
        if contact == True:
            #print ("we are in contact!")
            return job, grainA, grainB
        
    # Create progressbar
    widgets = [progressbar.FormatLabel(''), ' ', progressbar.Bar(), ' ', progressbar.AdaptiveETA()]
    pbar = progressbar.ProgressBar(widgets=widgets, maxval=numberOfJobs)
    pbar.start()
    finishedNodes = 0
    
    # Run multiprocessing
    with multiprocessing.Pool(processes=nProcesses) as pool:
        for returns in pool.imap_unordered(funLocalDetectionAssembly, range(0, numberOfJobs)):
            finishedNodes += 1
            widgets[0] = progressbar.FormatLabel("{}/{} ".format(finishedNodes, numberOfJobs))
            pbar.update(finishedNodes)
            if returns is not None:
                contactListRefined.append( [ returns[1], returns[2] ] )
        pool.close()
        pool.join()
            
    
    # End progressbar
    pbar.finish()
    
    return numpy.asarray(contactListRefined)


def contactOrientationsAssembly(volLab, volGrey, contactList, watershed="ITK", peakDistance=5, boundingBoxes=None, nProcesses=nProcessesDefault, verbose=False):
    """
    Determines contact normal orientation in an assembly of touching particles
    uses either directly the labelled image or the random walker implementation from skimage

    Parameters
    ----------
        volLab : 3D array
            Labelled volume

        volGrey : 3D array
            Grey-scale volume

        contactList : (ContactNumber)x2 array of integers
            contact list with grain labels of each contact in a seperate row,
            as given by ``spam.label.contacts.labelledContacts`` in the list contactingLabels
            or by ``spam.label.contacts.localDetectionAssembly()``

        watershed : string, optional
            sets the basis for the determination of the orientation
            options are "ITK" for the labelled image from the input,
            "RW" for a further segmentation by the random walker
            Default = "ITK"    

        peakDistance : int, optional
            Distance in pixels used in skimage.feature.peak_local_max
            Default value is 5

        boundingBoxes : lab.max()x6 array of ints, optional
            Bounding boxes in format returned by ``boundingBoxes``.
            If not defined (Default = None), it is recomputed by running ``boundingBoxes``

        nProcesses : integer (optional, default = nProcessesDefault)
            Number of processes for multiprocessing
            Default = number of CPUs in the system
            
        verbose : boolean (optional, default = False)
            True for printing the evolution of the process
            False for not printing the evolution of process

    Returns
    -------
        contactOrientations : (numContacts)x6 array
            contact normal orientation for every contact
            [labelGrainA, labelGrainB, orientationZ, orientationY, orientationX, intervoxel positions for PCA]

        notTreatedContact : boolean
            if False that contact is not determined
            if the contact consisted of too few voxels a fit is not possible or feasible
    """


    # check if bounding boxes are given
    if boundingBoxes is None:
        #print ("bounding boxes are not given. calculating ....")
        boundingBoxes = spam.label.boundingBoxes(volLab)

    contactOrientations = []
    numberOfJobs = len( contactList )
    #print ("\n\tDetermining the contact orientations of an assembly of particles")
    #print ("\tNumber of contacts ", numberOfJobs)
    #print ("")

    ##########################################
    
    # Function for ContactOrientationsAssembly
    global funContactOrientationsAssembly
    def funContactOrientationsAssembly(job):
        grainA, grainB = contactList[job,0:2].astype('int')
        labels = [grainA, grainB]
        subset = fetchTwoGrains(volLab, labels, volGrey, boundingBoxes)    
        contactNormal, intervox, NotTreatedContact = spam.label.contactOrientations(subset['subVolBin'], 
                                                                                    subset['subVolLab'], 
                                                                                    watershed, 
                                                                                    peakDistance=peakDistance, 
                                                                                    verbose=verbose)
        #TODO work on not treated contacts -- output them!
        return grainA, grainB, contactNormal[0], contactNormal[1], contactNormal[2], intervox
    
    # Create progressbar
    widgets = [progressbar.FormatLabel(''), ' ', progressbar.Bar(), ' ', progressbar.AdaptiveETA()]
    pbar = progressbar.ProgressBar(widgets=widgets, maxval=numberOfJobs)
    pbar.start()
    finishedNodes = 0
    
    # Run multiprocessing
    with multiprocessing.Pool(processes=nProcesses) as pool:
        for returns in pool.imap_unordered(funContactOrientationsAssembly, range(0, numberOfJobs)):
            finishedNodes += 1
            widgets[0] = progressbar.FormatLabel("{}/{} ".format(finishedNodes, numberOfJobs))
            pbar.update(finishedNodes)
            if returns is not None:
                contactOrientations.append( [ returns[0], returns[1], returns[2], returns[3], returns[4], returns[5] ] )
            #result[2], result[3], result[4], result[5], result[6], result[7]
        pool.close()
        pool.join()
    
    # End progressbar
    pbar.finish()
    
    return numpy.asarray(contactOrientations)


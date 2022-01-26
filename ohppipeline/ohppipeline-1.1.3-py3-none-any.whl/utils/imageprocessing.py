# -*- coding: utf-8 -*-


"""
This module provide many function in order to reduce and preprocess fits images

:author: C. Hottier ; N. Robichon
"""


from ccdproc import Combiner, subtract_bias, ccd_process, CCDData, cosmicray_lacosmic, cosmicray_median
from astropy import units as u
from numpy.ma import median as mamedian
from numpy import unravel_index, argmax, roll, median 
from scipy.signal import fftconvolve
from astroalign import register as aaregister

from tqdm import tqdm

from .utils import getlistccddata, getccddata


def makemasterbias(listofbias, unit=u.adu):
    """function to generate a master bias from a several bias

    :param listofbias: list or array-like of fits file name or CCDData
    :param unit: the unit of the image (astropy.units), default adu
    :raise RuntimeError: if there is not enought bias
    :returns: TODO

    """
    if len(listofbias) < 2 :
        raise RuntimeError("too few image to create a master bias, found %d"%(len(listofbias)))

    toanalyse = getlistccddata(listofbias, unit=unit)

    comb = Combiner(toanalyse,)

    return comb.median_combine()

def makemasterflat(masterbias, listofflat, unit=u.adu):
    """process the masterflat from the list of flat after correction of bias

    :param masterbias: np.array of CCDData containing the corresponding master bias 
    :param listofflat: list or array-like of fits file name or CCDData
    :param unit: the unit of the image  (astropy.unit), default adu
    :returns: the CCDData wich contain the masterflat

    """
    if len(listofflat) < 2 :
        raise RuntimeError("too few image to create a master flat, found %d"%(len(listofflat)))

    flattoanalyze = getlistccddata(listofflat, unit=unit)

    correcflat = [subtract_bias(fits,masterbias) for fits in tqdm(flattoanalyze, unit="image")]

    comb = Combiner(correcflat)
    scaling_func = lambda arr: 1.e0/mamedian(arr)
    comb.scaling = scaling_func

    return comb.median_combine()

def processimages(listofimage, masterbias, masterflat, unit=u.adu, ):
    """Processe image reduction for all images in listofimage 

    :listofimage: TODO
    :masterbias: TODO
    :masterflat: TODO
    :returns: list of reduce image 

    """
    imagestoanalyze = getlistccddata(listofimage, unit=unit)
    mbias = getccddata(masterbias, unit=unit)
    mflat = getccddata(masterflat, unit=unit)

    reducesimage = [ccd_process(fit, master_bias=mbias, master_flat=mflat) for fit in tqdm(imagestoanalyze, unit="image")]

    return reducesimage

def clean_cosmic(stack, **kargs):
    """clean the cosmicray in every image in the stack by using the median algorithm. full documentation of algorithm can be found at https://ccdproc.readthedocs.io/en/latest/api/ccdproc.cosmicray_median.html.
    
    Use kargs to pass otpion to the la_cosmic function
    """    

    res = [None] * len(stack)

    for i in tqdm(range(len(stack)), unit="image"):
        tmp = cosmicray_median(stack[i])
        # tmp.unit = u.adu
        res[i] = tmp
    
    return res
        

def crosscorrelalign(listofimage,returncombiner=True):

    # Collect arrays and crosscorrelate all with the first (except the first).
    images = [fits.data for fits in listofimage]
    nX, nY = images[0].shape
    correlations = [fftconvolve(images[0], image[::-1, ::-1], mode='same')
                    for image in images[1:]]

    # For each image determine the coordinate of maximum cross-correlation.
    shift_indices = [
            unravel_index(
                argmax(corr_array,axis=None),
            corr_array.shape) for corr_array in correlations]
    deltas = [(ind[0] - int(nX / 2), ind[1] - int(nY / 2))
                for ind in shift_indices]

    # Roll the images and return their median.
    realigned_images = [roll(image, deltas[i], axis=(0, 1))
                      for (i, image) in enumerate(images[1:])]

    res = [listofimage[0]] + [CCDData(im,meta=fit.header,unit=u.adu) for im,fit in zip(realigned_images, listofimage[1:])]
    if returncombiner : 
        comb = Combiner(res)
        scaling_func = lambda arr: 1.e0/mamedian(arr)
        comb.scaling = scaling_func
        return comb
    else:
        return res

def alignstack(stack, return_footprint=False):
    """
    align stack of images on the first images

    :param stack: list of ccdData 
    :param return_footprint: if true return the footprint of each align images 
    """
    align = [None] * len(stack)
    footprint = [None] * len(stack)
    align[0] = stack[0]
    for i in tqdm(range(1,len(stack))) : 
        tmp, footprint[i] = aaregister(stack[i], stack[0])
        align[i] = CCDData(data=tmp, header=stack[i].header, unit=stack[i].unit)
    
    if return_footprint :
        return align, footprint
    else :
        return align

def reducestack(stack) :
    """
    Reduce stack into one image by using median
    :param stack: list of CCDData
    """

    

# -*- coding: utf-8 -*-

from numpy import arange, full, exp, percentile, poly1d, polyfit
from numpy import float64, NaN, int32
from numpy.ma import diff, MaskedArray
from pandas import DataFrame, Index, read_csv
from scipy.optimize import curve_fit
from pkg_resources import resource_filename

"""Module in order to realise the wavelength calibration"""

_refcalibpath = resource_filename("ohppipeline.spectral","data/calibration_tables.dat")

_genericheader = Index(["Amplitude", "centroid", "sigma"])


def getraymax(spectrum):
    """Look for the location of the higher ray. To look for other ray, just mask those already found
    
    :param spectrum: Array of mask array of the spectrum
    :return: boolkean array, True at the location of the ray and false elsewhere
    """

    if isinstance(spectrum,MaskedArray):
        toa = spectrum
    else :
        toa = MaskedArray(data=spectrum, mask=False)
    difftoa = diff(toa)
    locmax = toa.argmax()
    locright = (difftoa[locmax:]<0).filled(fill_value=False).argmin()+1
    locleft = ((difftoa[:locmax][::-1])>0).filled(fill_value=False).argmin()
    mask = full(shape=spectrum.shape,fill_value=False)
    mask[locmax-locleft:locmax+locright] = True
    return mask

def _gauss(x, *p):
    A, mu, sigma = p
    return A*exp(-(x-mu)**2/(2.*sigma**2))

class Calibrator(object):

    """Class in order to realise the wavelength calibration"""

    def __init__(self, calibrationspectrum, nrays=None, threshold=0.05):
        """Construtor of the Calibrator object. it only required a reduce calibration spectrum.
        it will fit rays from the highest to the faintest. The number of is rays is nrays or all the rays higher than a threshold

        :param calibrationspectrum: unidimensionnal array with the flux of the calibration spectrum
        :param n: if not None look for n highest ray
        :param threshold: if not None search every ray higher than highest ray times to threshold
        """
        
        self._calib = calibrationspectrum.flatten()
        self._rays = []
        self._pixNum = arange(self._calib.size, dtype=float64)

        self._lookForRays(nrays=nrays, threshold=threshold)
        self._fitCentroidRays()
        self._polycoef1guess = None
        self._polycoef2guess = None
        self._refcalibration = None

    def _mergeMask(self):
        """generate a mask to remove rays already localised
        :returns: boolean array; True at rays location

        """
        res = False
        for r in self._rays:
            res = res | r
        return res

    @property
    def maskedspectrum(self):
        """mask already found rays 
        :returns: masked array of the calibration spectrum

        """
        return MaskedArray(data=self._calib, mask=self._mergeMask())

    @property
    def rayCount(self):
        """ return the number of ray already identify
        :returns: the number of identified ray

        """
        return len(self._rays)

    @property
    def rayTable(self):
        return self._raystable

    @property
    def coeffCalibration(self):
        """return the coefficient of the wavelength calibration
        :returns: numpy array of coeficent 

        """
        if self._polycoef2guess is None :
            raise RuntimeError("The first guess polynomial coefficient is not set")
        return self._polycoef2guess

    @property
    def calibrate(self) :
        """The polynomial function to calibrate pixels in wavelength"""
        return poly1d(self.coeffCalibration)

    @property
    def calibrationTable(self):
        """return the calibration table used to adjust the polynomial law
        :returns: pandas.DataFrame with all 

        """
        if self._refcalibration is None :
            raise RuntimeError("The reference calibration table is not yet set, use self.adjustFromFirstGuess to intitiate it")
        return self._refcalibration

    def _poly1guess(self, pix):
        """use the Poly 1st guess and process the pixel values
        :param pix: pixel values
        :returns: equivalent wavelength

        """
        if self._polycoef1guess is None :
            raise RuntimeError("The first guess polynomial coefficient is not set")

        poly = poly1d(self._polycoef1guess)
        return poly(pix)


    def _poly2guess(self, pix):
        """use the Poly 2nd guess and process the pixel values
        :param pix: pixel values
        :returns: equivalent wavelength

        """
        if self._polycoef2guess is None :
            raise RuntimeError("The first guess polynomial coefficient is not set")

        poly = poly1d(self._polycoef2guess)
        return poly(pix)

    def _lookForRays(self, nrays=None, threshold=None):
        """Look for rays in the calibration spectrum. can look for n highest rays or every higher than a threshold, it stop at the first condition reach.

        :param n: if not None look for n highest ray
        :param threshold: if not None search every ray higher than highest ray times to threshold

        """
        if (nrays is None) and (threshold is None):
            raise RuntimeError("n and threshold can not be None in the same time")

        while "new rays is needed" :
            if ((nrays is not None) and (self.rayCount >= nrays)) : break
            if ((threshold is not None) and (self.maskedspectrum.max() < threshold*self._calib.max())) : break
            self._rays += [getraymax(self.maskedspectrum)]

    def visualizeRays(self, ax):
        """plot the spectrum with each rays in different colors

        :param ax: matplotlib.axes where plot the results

        """
        ax.plot(self._pixNum, self.maskedspectrum, c="black")
        for r in self._rays :
            ax.plot(MaskedArray(data=self._calib, mask=~r))
        for i in range(self.rayCount) :
            ax.text(self.rayTable.loc[i,"centroid"], self.rayTable.loc[i,"Amplitude"], "%d"%(i),
                     horizontalalignment='center',verticalalignment="bottom")

    def _fitCentroidRays(self):
        """method in order to fit the centroid of each know rays
        
        """
        resdata = full(fill_value=NaN, shape=(self.rayCount, 3), dtype=float64)
        for i,r in enumerate(self._rays) :
            flux = self._calib[r]
            wavelength = self._pixNum[r]

            #initiale guess
            p0 = [
                    flux.max(),
                    wavelength.mean(),
                    percentile(wavelength, 84) - percentile(wavelength, 16)
                    ]

            p, _ = curve_fit(_gauss, wavelength, flux, p0=p0)

            resdata[i,:] = p

        self._raystable = DataFrame(columns=_genericheader, data=resdata)

    def adjustFromFirstGuess(self, polycoeff1guess, threshold=1., degcalib=2) :
        """Adjust the calibration rays, using the first guess, to a reference spectrum.

        :param polycoeff1guess: array comming from numpy.polyfit
        :param degcalib: degree of the polynomial fit between pixels and wavelength
        :param threshold: maximum delta between calibration rays and reference rays in Angstrom
        """

        self._polycoef1guess = polycoeff1guess
        self._raystable["1guess"] = self._poly1guess(self._raystable["centroid"])

        self._refcalibration = read_csv(_refcalibpath)
        self._refcalibration["centroid"] = NaN
        self._refcalibration["delta"] = NaN
        self._refcalibration["raynum"] = NaN

        for i in range(self._refcalibration.shape[0]) :
            a = self._refcalibration.loc[i,"lambda"]
            lp = (self.rayTable["1guess"]-a).abs()
            self._refcalibration.loc[i,"centroid"] = self.rayTable.loc[lp.argmin(),"centroid"]
            self._refcalibration.loc[i,"raynum"] = lp.argmin()
            self._refcalibration.loc[i,"delta"] = lp.min()
        self._refcalibration.raynum = self._refcalibration.raynum.astype(int32)

        self._refcalibration = self._refcalibration[self._refcalibration["delta"]<threshold]

        self._polycoef2guess = polyfit(self._refcalibration["centroid"], self._refcalibration["lambda"], degcalib)

        self._refcalibration["calibratedlambda"] = self._poly2guess(self._refcalibration["centroid"])




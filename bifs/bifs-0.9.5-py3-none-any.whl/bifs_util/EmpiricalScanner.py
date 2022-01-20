import itertools
import os
import re
import sys

# scans files to construct an empirical prior
from bifs import BIFS

# numpy >= 1.17
from numpy.random import Generator, PCG64
import numpy as np

class RunningMean:
    """Accepts values one at a time and computes the mean and sd of all values seen so far.
    The inputs are arrays, which must all have the same shape.  Mean and sd are accumulated
    separately for each cell in the array.
    """
    def __init__(self, sd=True):
        """If sd is false do not accumulate second moment.
        Clients should not request information related to the sd in that case.
        """
        self.n = 0
        self._second = sd  # as in second moment

    def observation(self, x):
        "x is an array-like object which is considered a single observation"
        self.n += 1
        if self.n == 1:
            self._mns = x
            if self._second:
                # ss will turn into a matrix later
                self._ss = 0.0
        else:
            lastdelta = x-self._mns
            self._mns += (lastdelta)/self.n
            if self._second:
                # element by element multiplication in next line
                self._ss += lastdelta*(x-self._mns)

    def mean(self):
        "return array of means so far"
        return self._mns

    def sd(self):
        "return array of sd so far"
        # element by element square root
        return np.sqrt(self._ss/(self.n-1))

class AbstractEmpiricalScanner:
    """ This class consumes a list of images and computes statistics on them.  Each statistic is computed separately for 
    each voxel, i.e. the result in the (2, 5) cell refers to all the (2, 5) cells in all the images (or their Fourier counterparts).
    All images must have the same dimensions, and they should be aligned with each other
    for the results to be meaningful.

    The mean and sd of the modulus is always accumulated; values for the phase can be requested as well, as can the correlations between the
    phase and modulus (again, at each point in Fourier space).

    Finally, one can request a sample of the original voxels in image space.

    Concrete classes provide particular ways to get images.  They then pass the images to _statsAccumulate and,
    optionally, _voxAccumulate (possibly different images for each) and call
    _post when done.  At that point, and only that point, are results available from self.modulus() and, if requested,
    self.phase(), self.corr(), and self.voxels().

    For backward compatility, self.mns, self.sds, and self.vox accessor return the mean and sd of self.modulus() and the voxels.
    Don't rely on that in new code.

    image_mask optionally indicates which areas of the image to ignore.
        It must be a boolean array with the same shape as image files.
        All voxels selected by image_mask are set to zero before doing BIFS processing.
        The mask applies to the original image NOT to the fourier space version, which will
        generally have non-0 values in the image_mask region.
        It is the subclass responsibility to implement these semantics.
        Note the "mask" here is not a mask in the numpy sense of a masked array, which
        concerns missing values.

    voxel sampling only considers the non-ignored regions, but the number sampled will be based on
        the total voxel count before masking.
    """
    def __init__(self, sampleFraction=0, seed=85792359, image_mask=None, phase=False, corr=False):
        """Setup for scan of images
        if sampleFraction is >0 (and it should be <=1) then that fraction of the image voxels will be retained.
        In that case, seed is used to set the random number generator.
        If phase is true, accumulate statistics on the phase as well as the modulus.
        If corr is true, accumulate statistics on the phase and its covariance with the modulus.
        Covariance is on  a cell by cell basis.
        """
        self.sampleFraction = sampleFraction
        self._modulus = RunningMean()
        if phase or corr:
            self._getPhase = True
            self._phase = RunningMean()
        if corr:
            self._getcorr = True
            self._xy = RunningMean(sd=False)
        if sampleFraction>0:
            self._voxels = []
            self._rg = Generator(PCG64(seed))
        self.masking = (image_mask is not None)
        if self.masking:
            self.image_mask = image_mask
            self.image_keep = np.logical_not(image_mask)
        self._benchmarkHdr = None  # checks for consistent headers
        self._mismatch = set()  # holds keys that had a mismatch
        self._bifs = BIFS()

    def modulus(self)->RunningMean:
        return self._modulus

    def phase(self)->RunningMean:
        return self._phase

    def corr(self):
        "Note we return the correlation matrix itself, not an accumulator"
        return (self._xy.mean()-self._modulus.mean()*self._phase.mean())/ \
            (self._modulus.sd()*self._phase.sd())


    def voxels(self):
        "return 1-d array sorted by intensity"
        return self._voxels

    def __getattr__(self, name):
        ## backward compatibility only
        if name == "mns":
            return self.modulus().mean()
        if name == "sds":
            return self.modulus().sd()
        if name == "vox":
            return self.voxels()
        raise AttributeError("'{}' object has no attribute '{}'".format(type(self).__name__, name))

    def _do_one(self, file):
        "file is a path-like object. Read it in and accumulate information"
        self._bifs.load_image_file(file)
        if self.masking:
            # dirty trick.  But doesn't invalidate anything else in _bifs.
            self._bifs._init_image[self.image_mask] = 0.0
        self._modulus.observation(self._bifs.mod_image())
        if self._getPhase:
            self._phase.observation(self._bifs.phase_image())
            if self._getcorr:
                # next multiplication is element by element
                self._xy.observation(self._bifs.phase_image()*self._bifs.mod_image())

        if self.sampleFraction>0:
            self._voxAccumulate(self._bifs.init_image())
        hdr = self._bifs.read_imfile.header
        if not self._benchmarkHdr:
            # first header encountered
            self._benchmarkHdr = hdr
            # could not delete the following key
            # it actually doesn't appear in the objects attributes
            #del benchmarkHdr.__dict__['db_name']  # differences expected and no concern
        else:
            for key in self._benchmarkHdr:
                if key == 'db_name':
                    continue
                if key.startswith("scl_"):
                    # values were array(nan, dtype=float32) and I had no luck testing for them
                    # in various ways
                    continue
                v1 = self._benchmarkHdr[key]
                v2 = hdr[key]
                if (v1 != v2).any():
                    self._mismatch.add(key)

    def _voxAccumulate(self, m):
        """accumulate voxel values.
        In the most likely case, the voxels are from image space while the empirical prior
        is from k-space.  So we provide seperate functions for the 2 values.
        Calling this is pointless unless sampleFraction>0.
        """
        # always base number sampled on the complete image size
        nSamp = int(m.size*self.sampleFraction)

        if self.masking:
            self._voxels.append(self._rg.choice(m[self.image_keep], nSamp))
        else:
            # m.ravel is not an acceptable first argument to choice
            # actually, it should have been np.ravel(m)
            # m.flatten and the mask selection above both create copies, unfortunately
            self._voxels.append(self._rg.choice(m.flatten(), nSamp))


    def _statsPost(self):
        """
        Finalize computation of voxel by voxel statistics for all images.
        Call after all images have been seen.

        Results returned as arrays self.mns and self.sds.
        """
        # currently handled by RunningMean instances automatically
        pass

    def _voxPost(self):
        """
        Finalize accumulated voxels.
        """
        if self.sampleFraction>0:
            self._voxels = np.concatenate(self._voxels)
            self._voxels.sort()


    def _post(self):
        "wrap up all processing"
        self._statsPost()
        self._voxPost()

    def nImages(self) -> int:
        "number of images processed so far = number of files read unless error"
        return self._modulus.n


class EmpiricalScanner(AbstractEmpiricalScanner):
    """Scan selected images on disk, ensuring they are alll compatible.

    topDir  path like object indicating where in the file system the scan should start
        all subdirectories will be scanned recursively unless they are excluded.
    matchFile  <String> regular expression for the file name of image files we want.
        Matching is on the file name only, not its full path.
    exclude     <String> optional regular expression.  Any directory matching this pattern is excluded.
        Any file that satisfies matchFile is excluded if it also matches exclude.
    ostr    A stream-like object that will receive routines notices of skipped files and statistics.

    See AbstractEmpiricalScanner for sampleFraction, seed and image_mask.

    The files are read in and converted to k-space.  We compute  the mean and sd of the k-space images,
    and optionally accumulate voxels from the original image.

    We also check that the headers are consistent.  This works for .nii files, and may or may not for others.
    """
    def __init__(self, sampleFraction=0, seed=85792359, topDir=".", matchFile="", exclude=None, image_mask=None, phase=False, corr=False, ostr=sys.stdout):
        super().__init__(sampleFraction, seed, image_mask, phase, corr)
        self._topDir = topDir
        self._matchRE = re.compile(matchFile, re.I)
        if exclude:
            self._excludeRE = re.compile(exclude, re.I)
        else:
            self._excludeRE = None
        self.go(ostr=ostr)

    def go(self, ostr=sys.stdout):
        """Actually perform the scan.
        Note this is triggered by object initialization.
        Repeated calls may not work.

        ostr is an output stream
        """
        for root, dirs, files in os.walk(self._topDir):
            if self._excludeRE:
                # avoid directories with our target case for whom we are trying to predict
                iKill = [ i for i, d in zip(itertools.count(), dirs) if self._excludeRE.search(d)]
                if iKill:
                    nKill = 0
                    for i in iKill:
                        i -= nKill
                        print("Skipping {}".format(dirs[i]), file=ostr)
                        del dirs[i-nKill]
                        nKill += 1
            # look for files to import
            if files:
                for f in files:

                    if not self._matchRE.search(f):
                        continue
                    if self._excludeRE:
                        if self._excludeRE.search(f):
                            print("Skipping {}".format(f), file=ostr)
                            continue
                    self._do_one(os.path.join(root, f))
        self._post()

class FeedScanner(AbstractEmpiricalScanner):
    """A scanner that accepts anything iterable as a list of file names to scan"""
    def __init__(self, files, sampleFraction=0, seed=85792359, image_mask=None, phase=False, corr=False, ostr=sys.stdout):
        super().__init__(sampleFraction, seed, image_mask, phase, corr)
        self._files = files
        self.go(ostr=ostr)

    def go(self):
        for f in self._files:
            self._do_one(f)
        self._post()
